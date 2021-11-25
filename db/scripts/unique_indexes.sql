CREATE UNIQUE INDEX shop_subcat_product_un ON shop_subcat_product(product_id, subcategory_id) WHERE (deleted is null);
CREATE UNIQUE INDEX shop_product_component_un ON shop_product_component(product_id, component_id) WHERE (deleted is null);
CREATE UNIQUE INDEX shop_kit_products_un ON shop_kit_products(product_id, kit_id) WHERE (deleted is null);
CREATE UNIQUE INDEX shop_linked_product_un ON shop_linked_product(product_id, linked_product_id) WHERE (deleted is null);