create or replace function increase_bonus_balance(p_user_id uuid, p_amount numeric, p_order_id uuid) returns integer
	language plpgsql
as $$
--увеличение бонусного баланса пользователя
DECLARE
  bonus_amount NUMERIC(10, 2);
BEGIN
   UPDATE appuser_user
   SET bonus_balance = bonus_balance + p_amount
   WHERE id = p_user_id;

   INSERT INTO shop_order_bonus_change_history
   SELECT uuid_generate_v4(),
          now(), now(), NULL,
          'RUB',
          bonus_amount,
          p_order_id,
          p_user_id;
   RETURN 0;
END;
$$;

alter function increase_bonus_balance(uuid, numeric, uuid) owner to postgres;

