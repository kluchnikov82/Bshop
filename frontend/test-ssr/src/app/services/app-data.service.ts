import { Injectable, EventEmitter, Inject, PLATFORM_ID } from '@angular/core';
import { Person } from './../entities/person';
import { Product, PromoEvent, EventProduct } from './../entities/product';
import { isPlatformBrowser } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AppDataService {

  public static menuList: any[];
  public static currentCategory: any;
  public static currentSubcat: any;
  public static currentProduct: any;
  public static user: Person;
  public static userToken: string;
  public static userLoggedIn = false;
  public static slides: any[] = [];
  public static searchProduct: string;
  public static openEarningsBlock = false;

  public static menuListChange$: EventEmitter<Object> = new EventEmitter();
  public static cartChange$: EventEmitter<Object> = new EventEmitter();
  public static userStatusChange$: EventEmitter<Object> = new EventEmitter();
  public static userDataChange$: EventEmitter<Object> = new EventEmitter();
  public static userLogout$: EventEmitter<Object> = new EventEmitter();
  public static slidesLoaded$: EventEmitter<Object> = new EventEmitter();
  public static currentCategoryChange$: EventEmitter<Object> = new EventEmitter();
  public static searchProductStart$: EventEmitter<Object> = new EventEmitter();

  constructor() { }

  public static addToCart(product: any = false, quantity: number = 1, addProgram: boolean = false, isKit: boolean = false, id = null) {
    if (isPlatformBrowser(PLATFORM_ID)) {
      if (product) {
        let localCart = JSON.parse(localStorage.getItem('cart'));
        if (!localCart) {
          localCart = [];
        }
        let curProduct = localCart.find(item => item.product_id == product.id);
        if (addProgram) {
          curProduct = localCart.find(item => item.product_id == product.product_id);
        }
        if (curProduct) {
          curProduct.quantity += quantity;
        } else {
          let prodId = '';
          if (addProgram) {
            prodId = product.product_id;
          } else {
            prodId = product.id;
          }
          let prodInfo: any = {};
          prodInfo = {
            product_id: prodId,
            quantity: quantity,
            price: Number(product.price),
            isKit: isKit
          };
          if (id) {
            prodInfo.id = id;
          }
          localCart.push(prodInfo);
        }
        localStorage.removeItem('cart');
        localStorage.setItem('cart', JSON.stringify(localCart));
        AppDataService.cartChange$.emit();
      }
    }
  }

  public static addEventToCart(promoEvent: PromoEvent, quantity: number = 1, id = null) {
    if (isPlatformBrowser(PLATFORM_ID)) {
      let localCart = JSON.parse(localStorage.getItem('cart'));
      if (!localCart) {
        localCart = [];
      }
      let curEvent = localCart.find(ev => ev.event_id === promoEvent.id);
      if (!curEvent) {
        let eventProducts = [];
        let orderEventProducts = [];
        if (promoEvent.event_products_for2any && promoEvent.event_products_for2any.length) {
          eventProducts = promoEvent.event_products_for2any.filter(prod => prod.check) as EventProduct[];
          eventProducts.forEach(prod => {
            prod.quantity = 1;
          });
        } else if (promoEvent.event_products_some_the_same && promoEvent.event_products_some_the_same.length) {
          eventProducts = promoEvent.event_products_some_the_same;
        } else if (promoEvent.discount_product) {
          let evProd = Object.assign({}, promoEvent.discount_product);
          evProd.price = Math.round(promoEvent.discount_product.price * (1 - (promoEvent.discount_product.discount / 100) ));
          eventProducts.push(evProd);
        }
        eventProducts.forEach(prod => {
          orderEventProducts.push({
            product_id: (prod.product_id) ? prod.product_id : prod.id,
            is_gift: false,
            quantity: (prod.quantity) ? prod.quantity : 1,
            price: prod.price,
            amount: prod.price * ((prod.quantity) ? prod.quantity : 1),
          });
        });
        if (promoEvent.gift_count) {
          orderEventProducts.push({
            product_id: promoEvent.gift.id,
            is_gift: true,
            quantity: promoEvent.gift_count,
            price: 0,
            amount: 0
          });
        }
        let eventInfo: any = {};
        eventInfo = {
          event_id: promoEvent.id,
          event_name: promoEvent.name,
          event_image: promoEvent.image,
          quantity: quantity,
          order_event_products: orderEventProducts
        };
        if (id) {
          eventInfo.id = id;
        }
        localCart.push(eventInfo);
        localStorage.removeItem('cart');
        localStorage.setItem('cart', JSON.stringify(localCart));
        AppDataService.cartChange$.emit();
      } else {
        curEvent.quantity += quantity;
        localStorage.removeItem('cart');
        localStorage.setItem('cart', JSON.stringify(localCart));
        AppDataService.cartChange$.emit();
      }
    }
  }

  public static endingWord(count) {
    switch (count % 10) {
      case 1: return (count === 11) ? 'ов' : '';
      case 2: return (count === 12) ? 'ов' : 'а';
      case 3: return (count === 13) ? 'ов' : 'а';
      case 4: return (count === 14) ? 'ов' : 'а';
      case 5:
      case 6:
      case 7:
      case 8:
      case 9:
      case 0: return 'ов';
    }
  }

  public static getThumbImg(product: Product) {
    let link = '';
    if (product) {
      link = product.primary_image;
      if (product.product_images) {
        if (product.product_images.length) {
          link = product.product_images[0].image;
        }
      }
    }
    return link;
  }

}
