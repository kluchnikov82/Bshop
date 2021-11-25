CREATE OR REPLACE FUNCTION public.shop_category_after_update()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
--триггер, удаляющий подкатегории после удаления категории
BEGIN
	IF NEW.deleted IS NOT NULL
    THEN
        UPDATE shop_subcategory SET deleted = now() WHERE category_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER shop_category_after_update AFTER UPDATE ON
public.shop_category FOR EACH ROW EXECUTE PROCEDURE shop_category_after_update();

CREATE OR REPLACE FUNCTION public.shop_sub_category_after_update()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
--триггер, удаляющий товары из подкатегории после удаления подкатегории
BEGIN
	IF NEW.deleted IS NOT NULL
    THEN
        UPDATE shop_subcat_product
        SET deleted = now()
        WHERE subcategory_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER shop_sub_category_after_update AFTER UPDATE ON
public.shop_subcategory FOR EACH ROW EXECUTE PROCEDURE shop_sub_category_after_update();

CREATE OR REPLACE FUNCTION public.shop_active_component_after_update()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
--триггер, удаляющий активный компонент из товаров после удаления компонента
BEGIN
	IF NEW.deleted IS NOT NULL
    THEN
        UPDATE shop_product_component
        SET deleted = now()
        WHERE product_id = NEW.id;
    END IF;
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER shop_active_component_after_update AFTER UPDATE ON
public.shop_active_component FOR EACH ROW EXECUTE PROCEDURE shop_active_component_after_update();