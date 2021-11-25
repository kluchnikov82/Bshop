CREATE OR REPLACE FUNCTION public.after_change_order_component()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
	PERFORM public.update_order_totals(NEW.order_id);
    RETURN NEW;
END;
$function$
;
