create or replace function appuser_before_update() returns trigger
    language plpgsql
as
$$
--триггер перерасчета целевого показателя, доли бонусной выплаты, скидки и статистических показателей при изменении депозита и/или бонусного баланса
DECLARE
  diff NUMERIC(14,2);
  p_bonus_share NUMERIC(14,2);
  p_discount NUMERIC(14,2);
BEGIN
	IF NEW.balance <> OLD.balance
	-- если произошло изменение депозита (как в большую, так и в меньшую сторону)
	THEN
	    diff := NEW.balance - OLD.balance;
	    NEW.total_payments = NEW.total_payments + diff;                   --изменение общей суммы пополнений депозита
        NEW.current_period_payments = NEW.current_period_payments + diff; --изменение суммы пополнений депозита текущего периода
	    NEW.current_target := NEW.current_period_payments + NEW.last_period_sale_amount - NEW.last_period_bonus_payments;  --изменение текущего целевого показателя
	    
        --изменение скидки и бонусного процента в соответствии с новым целевым показателем
	    SELECT COALESCE(discount, 0), COALESCE(bonus_share, 0)
	    INTO p_discount, p_bonus_share
        FROM public.shop_reward_params
	    WHERE now() BETWEEN started AND ended
	      AND partner_type_id = NEW.partner_type_id
	      AND NEW.current_target >= target
	    ORDER BY target DESC
	    LIMIT 1;
	   
	    NEW.current_discount := p_discount;
	    NEW.current_bonus_share := p_bonus_share;
	END IF;

    diff := NEW.bonus_balance - OLD.bonus_balance;
	IF diff > 0
    --если увеличился бонусный баланс
    THEN
        NEW.total_bonus_payments = NEW.total_bonus_payments + diff;                   --увеличение общей суммы пополнений бонусного баланса
	    NEW.current_period_bonus_payments = NEW.current_period_bonus_payments + diff; --увеличение суммы пополнений бонусного баланса за текущий период
		NEW.total_sale_amount = NEW.total_sale_amount + diff;                         --увеличение общей суммы продаж реферралов
		NEW.current_period_sale_amount = NEW.current_period_sale_amount + diff;       --увеличение суммы продаж реферралов текущего периода
	END IF;

	IF diff <> 0 THEN
        --добавляем запись в историю изменений бонусного баланса
        INSERT INTO appuser_bonus_change_history
        SELECT uuid_generate_v4(),
               now(), now(), null,
               'RUB',
               diff,
               NEW.id;
    end if;

    RETURN NEW;
END;
$$;

alter function appuser_before_update() owner to postgres;
