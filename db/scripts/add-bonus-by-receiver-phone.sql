create or replace function order_before_update() returns trigger
    language plpgsql
as
$$
--триггер, обрабатывающий оплату заказа
DECLARE
  p_referrer_id uuid;            --id реферрера
  p_bonus_share NUMERIC(14, 2);  --доля бонусной выплаты реферрера
  bonus NUMERIC(14, 2);          --сумма начисляемого бонуса
  receiver_user_id uuid;         --id пользователя-получателя заказа, определяемый по номеру телефона получателя
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
	        receiver_user_id = (SELECT id FROM appuser_user WHERE phone=NEW.phone ORDER BY created DESC LIMIT 1);

	        if receiver_user_id is not null THEN
	           SELECT current_bonus_share INTO p_bonus_share
		       FROM appuser_user
		       WHERE id = receiver_user_id;

		       bonus := NEW.total_amount * p_bonus_share;  --сумма бонуса в рублях
	            --увеличиваем бонусный баланс получателя заказа
		       UPDATE appuser_user
		       SET bonus_balance = bonus_balance + bonus
		       WHERE id = receiver_user_id;
	        END IF;

	        --находим реферрера для данного заказа
			SELECT referrer_id INTO p_referrer_id
		    FROM shop_referrer_order
		    WHERE order_id = NEW.id;
	      
			IF p_referrer_id IS NOT NULL
				AND p_referrer_id <> COALESCE(NEW.user_id, uuid_generate_v4())
	    	THEN
	    	   --если заказа создан реферралом, получаем текущий процент бонуса для реферрера
			   SELECT current_bonus_share INTO p_bonus_share
		       FROM appuser_user
		       WHERE id = p_referrer_id;
		      
		       bonus := NEW.total_amount * p_bonus_share;  --сумма бонуса в рублях
			
               --увеличиваем бонусный баланс
		       UPDATE appuser_user
		       SET bonus_balance = bonus_balance + bonus
		       WHERE id = p_referrer_id;

		       --апдейтим сумму бонуса в реферральном заказе
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

		           --увеличиваем бонусный баланс
                   UPDATE appuser_user
                   SET bonus_balance = bonus_balance + bonus
                   WHERE id = NEW.user_id;
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