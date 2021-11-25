create or replace view view_order_gift(id, gift_description, created, updated, deleted) as
SELECT z.order_id                                                                                  AS id,
       'Ваши подарки: '::text ||
       COALESCE(array_to_string(array_agg(z.gift_name ORDER BY 1::integer), ', '::text), ''::text) AS gift_description,
       now()                                                                                       AS created,
       now()                                                                                       AS updated,
       NULL::timestamp with time zone                                                              AS deleted
FROM (SELECT op.order_id,
             (p.name::text || ': '::text) || e.gift_count::character varying(255)::text AS gift_name
      FROM shop_order_product op
               JOIN shop_event_product_2any e2any ON e2any.product_id = op.product_id AND e2any.deleted IS NULL
               JOIN shop_event e
                    ON e.id = e2any.event_id AND e.is_active = true AND now() >= e.started AND now() <= e.ended
               JOIN shop_product p ON p.id = e.gift_id
      WHERE op.deleted IS NULL
      GROUP BY p.name, e.gift_count, op.order_id, e.for_n_any_quantity, e.id
      HAVING count(DISTINCT op.product_id) >= coalesce(e.for_n_any_quantity, (
          SELECT count(*) FROM shop_event_product_2any
          WHERE event_id = e.id
            AND deleted IS NULL
          ))
      UNION
      SELECT x.order_id,
             x.gift_name
      FROM (SELECT DISTINCT op.order_id,
                            (p.name::text || ': '::text) ||
                            ((e.gift_count * op.quantity / ss.quantity))::character varying(255)::text               AS gift_name,
                            row_number()
                            OVER (PARTITION BY op.order_id ORDER BY (e.gift_count * op.quantity / ss.quantity) DESC) AS gift_count
            FROM shop_order_product op
                     JOIN shop_event_product_some_the_same ss
                          ON ss.product_id = op.product_id AND ss.deleted IS NULL AND op.quantity >= ss.quantity
                     JOIN shop_event e
                          ON e.id = ss.event_id AND e.is_active = true AND now() >= e.started AND now() <= e.ended
                     JOIN shop_product p ON p.id = op.product_id
            WHERE op.deleted IS NULL) x
      WHERE x.gift_count = 1) z
GROUP BY z.order_id;