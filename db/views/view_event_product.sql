create or replace view view_event_product(id, event_id, product_id) as
SELECT uuid_generate_v4() AS id,
       z.event_id,
       z.product_id
FROM (SELECT DISTINCT x.event_id,
                      x.product_id
      FROM (SELECT e.id AS event_id,
                   gp.product_id
            FROM shop_event e
                     JOIN shop_event_group g ON g.event_id = e.id
                     JOIN shop_event_group_product gp ON gp.group_id = g.id
            WHERE COALESCE(e.deleted, g.deleted, gp.deleted) IS NULL
            UNION
            SELECT e.id AS event_id,
                   ss.product_id
            FROM shop_event e
                     JOIN shop_event_product_some_the_same ss ON ss.event_id = e.id
            WHERE COALESCE(e.deleted, ss.deleted) IS NULL
            UNION
            SELECT e.id AS event_id,
                   ss.product_id
            FROM shop_event e
                     JOIN shop_event_product_2any ss ON ss.event_id = e.id
            WHERE COALESCE(e.deleted, ss.deleted) IS NULL) x) z;

alter table view_event_product owner to postgres;

