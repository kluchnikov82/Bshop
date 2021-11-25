create or replace function order_before_update() returns trigger
	language plpgsql
as $$
--триггер, обрабатывающий оплату заказа
DECLARE
  p_referrer_id uuid;            --id реферрера
  p_bonus_share NUMERIC(14, 2);  --доля бонусной выплаты реферрера
  p_own_bonus_share NUMERIC(14, 2);  --доля бонусной выплаты создателя заказа
  creator_phone varchar(255);    --телефон создателя заказа
  creator_email varchar(255);    --email создателя заказа
  referrer_phone varchar(255);   --телефон реферрера
  referrer_email varchar(255);   --email реферрера
  creator_partner_type_id int;
  referrer_partner_type_id int;
  referrer_bonus_share NUMERIC(14, 2);
  bonus_amount NUMERIC(14, 2);
  m_user_id uuid;
BEGIN
	IF NEW.is_payed = TRUE AND OLD.is_payed = FALSE
       AND NOT EXISTS
		(
		  SELECT * FROM shop_order_pay_history
		  WHERE order_id = NEW.id
		)
    --если статус заказа меняется на "Оплачен" и заказ еще не был обработан триггером
    THEN
        IF NEW.payed IS NULL THEN
           NEW.payed = now();
        END IF;

        IF NEW.order_type = 0
	    --оплата заказанного товара
	    THEN
	        SELECT phone, email, partner_type_id
            INTO creator_phone, creator_email, creator_partner_type_id
            FROM appuser_user
            WHERE id = NEW.user_id;

	        --находим реферрера для данного заказа
			SELECT referrer_id INTO p_referrer_id
		    FROM shop_referrer_order
		    WHERE order_id = NEW.id;

	        -- начисление бонусов реферреру
			IF p_referrer_id IS NOT NULL THEN
			    -- начисление бонусов реферреру, если заказ создан реферралом
			    SELECT phone, email, partner_type_id, current_bonus_share
			    INTO referrer_phone, referrer_email, referrer_partner_type_id, referrer_bonus_share
			    FROM appuser_user
			    WHERE id = p_referrer_id;

				IF p_referrer_id IS DISTINCT FROM NEW.user_id
			       AND creator_phone <> referrer_phone
			       AND creator_email <> referrer_email
				    THEN
				       CASE WHEN referrer_partner_type_id = 1 THEN
				           -- если тип партнера - розница, получаем долю бонусной выплаты из параметров бонусной программы
                               SELECT bonus_share INTO p_bonus_share
                               FROM shop_reward_params
                               WHERE partner_type_id = referrer_partner_type_id
                                 AND deleted is null
                                 AND now() BETWEEN started and ended;
				           WHEN referrer_partner_type_id = 3 THEN
				               -- если тип партнера - дистрибьютор, доля бонусной выплаты зависит от суммы пополнений депозита и суммы заказов
				               -- и хранится в профиле пользователя
                               p_bonus_share := referrer_bonus_share;
                               -- начисляем фиксированный 10% бонус реферралу
				               perform public.increase_bonus_balance(NEW.user_id, NEW.total_amount*0.1, NEW.id);
                           WHEN referrer_partner_type_id = 4 THEN
                               -- если тип партнера - менеджер, то бонусы реферреру не начисляются
				               p_bonus_share := 0;
                       END CASE;

				       bonus_amount := NEW.total_amount*p_bonus_share;

				       --начисляем реферреру бонус
                       perform public.increase_bonus_balance(p_referrer_id, bonus_amount, NEW.id);
                       --и апдейтим сумму бонуса в реферральном заказе
                       UPDATE shop_referrer_order
                       SET bonus = NEW.total_amount * p_bonus_share
                       WHERE order_id = NEW.id;
                   END IF;
			END IF;

	        -- начисление бонусов создателю заказа
            CASE WHEN creator_partner_type_id = 1 THEN
                    -- если тип партнера - розница, получаем долю бонусной выплаты для своего заказа из параметров бонусной программы
                    SELECT own_bonus_share INTO p_own_bonus_share
                    FROM shop_reward_params
                    WHERE partner_type_id = creator_partner_type_id
                      AND deleted is null
                      AND now() BETWEEN started and ended
                    ORDER BY created DESC LIMIT 1;

                    --увеличиваем бонусный баланс создателя заказа
                    perform public.increase_bonus_balance(NEW.user_id, NEW.total_amount*p_own_bonus_share, NEW.id);
                WHEN creator_partner_type_id = 3 THEN
                    IF NEW.own = TRUE THEN
                       --если заказ создан для себя, то только увеличиваем общую сумму заказов без начисления бонусов
                       UPDATE appuser_user
                       SET total_amount = total_amount + NEW.total_amount
                       WHERE id = NEW.user_id;
                    END IF;
                WHEN creator_partner_type_id = 4 THEN
                    -- если тип партнера - Менеджер, определяем пользователя для начисления бонусов по номеру телефона в заказе
                    SELECT id INTO m_user_id
                    FROM appuser_user
                    WHERE phone = NEW.phone;

                    -- получаем бонусную ставку из параметров бонусной программы
                    SELECT own_bonus_share INTO p_own_bonus_share
                    FROM shop_reward_params
                    WHERE partner_type_id = creator_partner_type_id
                      AND deleted is null
                      AND now() BETWEEN started and ended
                    ORDER BY created DESC LIMIT 1;

                    --увеличиваем бонусный баланс получателя заказа
                    perform public.increase_bonus_balance(m_user_id, NEW.total_amount*p_own_bonus_share, NEW.id);
            END CASE;
		ELSE
		    --если заказа на пополнение депозита, то увеличиваем депозит создателя заказа
	        UPDATE appuser_user
	        SET balance = balance + NEW.total_amount
	        WHERE id = NEW.user_id;
	    END IF;

	    NEW.status := 1;

	    INSERT INTO shop_order_pay_history
        SELECT uuid_generate_v4(), now(), now(), NULL, NEW.id;
    END IF;

   RETURN NEW;
END;
$$;

alter function order_before_update() owner to postgres;

