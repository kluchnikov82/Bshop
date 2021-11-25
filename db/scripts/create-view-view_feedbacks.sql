CREATE OR REPLACE VIEW view_feedbacks AS
SELECT * FROM (
          SELECT k.id,
                 text,
                 video_link,
                 created,
                 with_text,
                 rating,
                 order_no,
                 approved,
                 user_id,
                 show_on_main_page,
                 updated,
                 deleted,
                 (
                     SELECT image
                     FROM shop_kit_feedback_image
                     WHERE feedback_id = k.id
                       AND deleted IS NULL
                     ORDER BY created DESC
                     LIMIT 1) as image
          FROM shop_kit_feedback k
          WHERE k.deleted IS NULL
            AND approved = TRUE
          UNION
          SELECT p.id,
                 text,
                 video_link,
                 created,
                 with_text,
                 rating,
                 order_no,
                 approved,
                 user_id,
                 show_on_main_page,
                 updated,
                 deleted,
                 (
                     SELECT image
                     FROM shop_product_feedback_image
                     WHERE feedback_id = p.id
                       AND deleted IS NULL
                     ORDER BY created DESC
                     LIMIT 1) as image
          FROM shop_product_feedback p
          WHERE p.deleted IS NULL
            AND approved = TRUE
) z
ORDER BY order_no, created DESC;