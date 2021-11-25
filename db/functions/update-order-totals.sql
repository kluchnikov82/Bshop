create or replace function update_order_totals(p_order_id uuid) returns integer
	language plpgsql
as $$
DECLARE
  p_total_amount decimal(10, 2);
  p_total_weight decimal(10, 2);
  p_total_volume float;
  total_kits_amount decimal(10, 2);
  total_kits_weight decimal(10, 2);
  total_kits_volume float;
  total_events_amount decimal(10, 2);
  total_events_weight decimal(10, 2);
  total_events_volume float;
BEGIN
	SELECT COALESCE(sum(op.amount), 0),
           COALESCE(sum(greatest(p.packing_volume, p.volume/1000000)*op.quantity), 0),
           COALESCE(sum(p.gross_weight*op.quantity), 0)
    INTO p_total_amount, p_total_volume, p_total_weight
	FROM shop_order_product op
	JOIN shop_product p ON p.id = op.product_id
	WHERE order_id = p_order_id AND op.deleted IS NULL;

    SELECT COALESCE(sum(ok.amount), 0),
           COALESCE(sum(COALESCE(k.packing_volume, 0)*ok.quantity), 0),
           COALESCE(sum(k.gross_weight*ok.quantity), 0)
    INTO total_kits_amount, total_kits_volume, total_kits_weight
	FROM shop_order_kit ok
	JOIN shop_kit k ON k.id = ok.kit_id
	WHERE order_id = p_order_id AND ok.deleted IS NULL;

	SELECT COALESCE(sum(ep.amount), 0),
           COALESCE(sum(greatest(p.packing_volume, p.volume/1000000)*ep.quantity), 0),
           COALESCE(sum(p.gross_weight*ep.quantity), 0)
	INTO total_events_amount, total_events_volume, total_events_weight
	FROM shop_order_event e
	JOIN shop_order_event_products ep ON ep.order_event_id = e.id AND ep.deleted IS NULL
	JOIN shop_product p ON p.id = ep.product_id
	WHERE e.order_id = p_order_id AND e.deleted IS NULL;

    p_total_amount := p_total_amount + total_kits_amount + total_events_amount;
    p_total_volume := p_total_volume + total_kits_volume + total_events_volume;
    p_total_weight := p_total_weight + total_kits_weight + total_events_weight;

    UPDATE shop_order
    SET --total_amount = p_total_amount,
        total_volume = p_total_volume,
        total_weight = p_total_weight
    WHERE id = p_order_id;

	RETURN 0;
END;
$$;
