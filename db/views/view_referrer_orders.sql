CREATE OR REPLACE VIEW public.view_referrer_orders
AS SELECT uuid_generate_v4() AS id,
    ro.referrer_id AS user_id,
    o.created,
    o.payed,
    o.order_no,
    o.total_amount,
    ro.bonus
   FROM shop_order o
     JOIN shop_referrer_order ro ON ro.order_id = o.id
  WHERE o.is_payed = true;
