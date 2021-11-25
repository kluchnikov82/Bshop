CREATE OR REPLACE FUNCTION public.prod_feedback_after_insert_update()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
--триггер, рассчитывающий средний рейтинг товара после добавления отзыва
BEGIN
	IF COALESCE(NEW.rating, 0) BETWEEN 1 AND 5
    THEN
        UPDATE shop_product
        SET rating = (SELECT avg(rating*1.0) FROM shop_product_feedback
                      WHERE product_id = NEW.product_id AND deleted IS NULL AND rating BETWEEN 1 AND 5)
        WHERE id = NEW.product_id;
    END IF;
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER prod_feedback_after_insert AFTER INSERT ON public.shop_product_feedback
FOR EACH ROW EXECUTE PROCEDURE prod_feedback_after_insert_update();

CREATE TRIGGER prod_feedback_after_update AFTER UPDATE ON
public.shop_product_feedback FOR EACH ROW EXECUTE PROCEDURE prod_feedback_after_insert_update();
