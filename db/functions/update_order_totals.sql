CREATE OR REPLACE FUNCTION public.update_order_totals(p_order_id uuid)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
  p_total_amount decimal(10, 2);
  p_total_weight decimal(10, 2);
  p_total_volume float;
  total_kits_amount decimal(10, 2);
  total_kits_weight decimal(10, 2);
  total_kits_volume float;
BEGIN
	SELECT COALESCE(sum(op.amount), 0),
           COALESCE(sum(COALESCE(p.packing_volume, p.volume, 0)*op.quantity), 0),
           COALESCE(sum(p.weight*op.quantity)/1000.0, 0)
    INTO p_total_amount, p_total_volume, p_total_weight
	FROM shop_order_product op
	JOIN shop_product p ON p.id = op.product_id
	WHERE order_id = p_order_id AND op.deleted IS NULL;

    SELECT COALESCE(sum(ok.amount), 0),
           COALESCE(sum(COALESCE(k.packing_volume, 0)*ok.quantity), 0),
           COALESCE(sum(k.weight*ok.quantity)/1000.0, 0)
    INTO total_kits_amount, total_kits_volume, total_kits_weight
	FROM shop_order_kit ok
	JOIN shop_kit k ON k.id = ok.kit_id
	WHERE order_id = p_order_id AND ok.deleted IS NULL;

    p_total_amount := p_total_amount + total_kits_amount;
    p_total_volume := p_total_volume + total_kits_volume;
    p_total_weight := p_total_weight + total_kits_weight;

    UPDATE shop_order
    SET total_amount = p_total_amount,
        total_volume = p_total_volume,
        total_weight = p_total_weight
    WHERE id = p_order_id;

	RETURN 0;
END;
$function$
;
