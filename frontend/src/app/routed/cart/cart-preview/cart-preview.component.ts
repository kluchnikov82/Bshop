import { Component, OnInit } from '@angular/core';
import { GetDataService } from '../../../shared/services/get-data.service';
import { AppDataService } from '../../../shared/services/app-data.service';
import { PromoEvent } from '../../../shared/entities/product';

@Component({
  selector: 'cart-preview',
  templateUrl: './cart-preview.component.html',
  styleUrls: ['./cart-preview.component.scss']
})
export class CartPreviewComponent implements OnInit {

  public cartProducts: [] = [];
  public cartKits: any[] = [];
  public cartEvents: any[] = [];
  public cartSum: number;

  constructor(
    private getDataService: GetDataService
  ) { }

  ngOnInit() {
    this.cartProducts = [];
    this.cartEvents = [];
    this.cartSum = 0;
    let localCart = JSON.parse(localStorage.getItem('cart'));
    if (localCart) {
      let searchProducts = '';
      for (let product of localCart) {
        if (product.product_id) {
          if (product.isKit) {
            this.getDataService.getProgramData(product.product_id).subscribe((data) => {
              if (data) {
                this.cartKits.push(data);
              }
            });
          } else {
            if (product.product_id) {
              searchProducts += '&id=' + product.product_id;
            }
          }
        }
        if (product.event_id) {
          this.cartEvents.push(product);
        }
      }
      if (searchProducts) {
        this.getDataService.getProductsList(searchProducts).subscribe((data) => {
          //console.log(data);
          this.cartProducts = data;
        })
      }
    }

  }

  getProductData(product, type) {
    if (product) {
      let localCart = JSON.parse(localStorage.getItem('cart'));
      let productCart = localCart.find(item => item.product_id == product.id);
      if (productCart) {
        switch (type) {
          case 'primary_image': return this.getThumbImg(product);
          case 'name': return product.name;
          case 'quantity': return productCart.quantity;
          case 'sum': return (productCart.quantity * Number(product.price));
          default: return '';
        }
      }
    }
  }

  getCartSum() {
    let localCart = JSON.parse(localStorage.getItem('cart'));
    let sum = 0;
    if (localCart) {
      localCart.forEach(prod => {
        if (prod.product_id) {
          sum += (prod.quantity * Number(prod.price));
        }
        if (prod.event_id) {
          sum += this.getEventPrice(prod) * prod.quantity;
        }
      });
      return sum;
    } else {
      return '';
    }
  }

  getCartCount() {
    let localCart = JSON.parse(localStorage.getItem('cart'));
    if (localCart) {
      let cartCount = localCart.length;
      switch (cartCount) {
        case 1:
        case 21: return cartCount + ' товар';
        case 2:
        case 3:
        case 4:
        case 22:
        case 23:
        case 24: return cartCount + ' товара';
        default: return cartCount + ' товаров';
      }
    } else {
      return ' пусто';
    }
  }

  getEventImg(promo) {
    if (promo.event_image) {
      return promo.event_image;
    } else {
      return '/assets/logo-new.jpg';
    }
  }

  getEventPrice(promo) {
    let sum = 0;
    if (promo) {
      if (promo.price) {
        sum = promo.price;
      } else {
        promo.order_event_products.forEach(prod => {
          sum += prod.amount;
        });
      }
    }
    return sum;
  }

  toggleOuterScroll(type) {
    if (type == 'block') {
      document.body.classList.add('non-scroll');
    } else {
      document.body.classList.remove('non-scroll');
    }
  }

  getProgramData(kit, type = '') {
    if (kit) {
      if (kit.kit_images) {
        return kit.kit_images[0].image;
      } else {
        return '/assets/logo-new.jpg';
      }
    } else {
      return '/assets/logo-new.jpg';
    }
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

}
