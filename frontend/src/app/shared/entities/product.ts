export class Product {
    id: string;
    name: string;
    english_name: string;
    primary_image: string;
    description: string;
    short_description: string;
    price: number;
    price_currency: string;
    is_available: boolean;
    hit_count: number;
    product_no: string;
    code: string;
    result: string;
    usage: string;
    certificate: string;
    hit: boolean;
    new: boolean;
    discount: number;
    categories: any[];
    rating: number;
    subcategories: any[];
    product_images: any[];
    active_components: any[];
    linked_products: any[];
    kits: any[];
}

export interface Promocode {
    code: string;
    description: string;
    code_type: number;
    discount: number;
    gift: {
        id: string,
        price: number,
        code: string,
        short_description: string,
        description: string,
        name: string,
        english_name: string,
        weight: number,
        volume: number,
        primary_image: string,
        product_images: any[]
    };
  }

export interface EventProduct {
  id?: string;
  code: string;
  quantity: number;
  product_id?: string;
  product_no: number;
  product_name: string;
  description: string;
  weight: number;
  volume: number;
  check: boolean;
  primary_image: string;
  price: number;
  english_name: string;
  name: string;
}

export interface PromoEvent {
  id: string;
  seq_no: number;
  name: string;
  description: string;
  image: string;
  event_products_some_the_same: EventProduct[];
  event_products_for2any: EventProduct[];
  event_products_bundle: EventProduct[];
  dont_apply_promo: boolean;
  discount_product: Product;
  discount_product_for_n: Product;
  discount_product_count: number;
  discount_for_n: number;
  event_groups: any[];
  gift: EventProduct;
  gift_count: number;
  half_screen: boolean;
  order_event_products?: EventProduct[];
  event?: any;
  price: number;
}
