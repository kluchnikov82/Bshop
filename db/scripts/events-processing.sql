create or replace function increase_bonus_balance(p_user_id uuid, p_amount numeric(10, 2)) returns integer
    language plpgsql
as
$$
--увеличение бонусного баланса пользователя
BEGIN
   UPDATE appuser_user
   SET bonus_balance = bonus_balance +
                       (
                           SELECT coalesce(current_bonus_share, 0)
                           FROM appuser_user
                           WHERE id = p_user_id
                       ) * p_amount
   WHERE id = p_user_id;

   RETURN 0;
END;
$$;

create or replace function order_before_update() returns trigger
    language plpgsql
as
$$
--триггер, обрабатывающий оплату заказа
DECLARE
  p_referrer_id uuid;            --id реферрера
  p_bonus_share NUMERIC(14, 2);  --доля бонусной выплаты реферрера
  receiver_user_id uuid;         --id пользователя-получателя заказа, определяемый по номеру телефона получателя
  p_memo varchar(1000);            --примечание к заказу (в нем перечислен список подарков по акции)
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
	        --добавление в memo информации о подарках, если заказ удовлетворяет условиям акций
            SELECT coalesce(array_to_string(array_agg(gift_name order by 1), ', '), '')
            INTO p_memo
            FROM (
             --акция "любые два товара из списка"
             SELECT p.name as gift_name
             FROM shop_order_product op
             JOIN shop_event_product_2any e2any ON e2any.product_id = op.product_id
                 AND e2any.deleted is null
             JOIN shop_event e ON e.id = e2any.event_id
                 AND e.is_active = TRUE
                 AND now() BETWEEN e.started and e.ended
             JOIN shop_product p ON p.id = e.gift_id
             WHERE order_id = NEW.id AND op.deleted is null
             GROUP BY p.name
             HAVING count(distinct op.product_id) >= 2
             UNION
             --акция "n+1"
             SELECT DISTINCT p.name as gift_name
             FROM shop_order_product op
             JOIN shop_event_product_some_the_same ss ON ss.product_id = op.product_id
                 AND ss.deleted is null
                 AND op.quantity >= ss.quantity
             JOIN shop_event e ON e.id = ss.event_id
                 AND e.is_active = TRUE
                 AND now() BETWEEN e.started and e.ended
             JOIN shop_product p ON p.id = op.product_id
             WHERE order_id = NEW.id AND op.deleted is null
             ) z;

            IF p_memo <> '' THEN
               NEW.memo = 'Ваши подарки: ' || p_memo;
            END IF;

	        -- определяем по номеру телефона в заказе, зарегистрирован ли получатель заказа в системе
	        receiver_user_id = (
	            SELECT id FROM appuser_user
	            WHERE phone = NEW.phone
	              AND id <> NEW.user_id
	            ORDER BY created DESC LIMIT 1);

	        if receiver_user_id is not null THEN
	           -- если зарегистрирован - начисляем ему бонус
	           perform public.increase_bonus_balance(receiver_user_id, NEW.total_amount);
	        END IF;

	        --находим реферрера для данного заказа
			SELECT referrer_id INTO p_referrer_id
		    FROM shop_referrer_order
		    WHERE order_id = NEW.id;
	      
			IF p_referrer_id IS NOT NULL
				AND p_referrer_id <> COALESCE(NEW.user_id, uuid_generate_v4())
	    	THEN
	    	   --если заказа создан реферралом, начисляем ему бонус
			   perform public.increase_bonus_balance(p_referrer_id, NEW.total_amount);

		       --и апдейтим сумму бонуса в реферральном заказе
			   SELECT coalesce(current_bonus_share, 0)
		       INTO p_bonus_share
               FROM appuser_user
               WHERE id = p_referrer_id;

		       UPDATE shop_referrer_order
		       SET bonus = NEW.total_amount * p_bonus_share
		       WHERE order_id = NEW.id;
		    ELSE
		       IF NEW.own = TRUE
		       THEN
		           --если заказ создан не реферралом, а для себя, увеличиваем общую сумму заказов
		           UPDATE appuser_user
		           SET total_amount = total_amount + NEW.total_amount
		           WHERE id = NEW.user_id;

		           --увеличиваем бонусный баланс создателя заказа
                   perform public.increase_bonus_balance(NEW.user_id, NEW.total_amount);
		       END IF;
		    END IF;
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


