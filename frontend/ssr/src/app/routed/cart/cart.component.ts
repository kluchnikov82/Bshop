import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, Inject, PLATFORM_ID } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material';
import { Router, ActivatedRoute } from '@angular/router';
import { registerLocaleData, isPlatformBrowser } from '@angular/common';
import ru from '@angular/common/locales/ru';
import { Subscription } from 'rxjs';
import { GetDataService } from '../../services/get-data.service';
import { AppDataService } from '../../services/app-data.service';
import { Promocode } from '../../shared/entities/product';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.scss']
})
export class CartComponent implements OnInit {

  userDataForm = new FormGroup({
    fioControl: new FormControl('', [Validators.required, Validators.minLength(8)]),
    phoneControl: new FormControl('', Validators.required),
    emailControl: new FormControl()
  })

  deliveryForm = new FormGroup({
    regionControl: new FormControl(),
    cityControl: new FormControl(),
    streetControl: new FormControl(),
    houseControl: new FormControl(),
    flatControl: new FormControl()
  });

  subscription: Subscription;
  kladrId: string;
  public products: any[] = [];
  private localCart: any[] = [];
  public cartKits: any[] = [];
  public cartEvents: any[];
  public promocode: string;
  public orderHasPromocode = false;
  public promocodeText: string;
  public promoDiscount = 0;
  public showFreeDelivery = true;

  constructor(
    private getDataService: GetDataService,
    private router: Router,
    private snackBar: MatSnackBar,
    private activateRoute: ActivatedRoute,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.subscription = activateRoute.url.subscribe(() => {
      this.parseLocalCart();
    });
    AppDataService.cartChange$.subscribe(() => {
      this.parseLocalCart();
    });
  }

  ngOnInit() {
    // this.cartKits = [];
    // this.cartEvents = [];
    registerLocaleData( ru );
    this.showFreeDelivery = (this.getCartSum(true) < 4000);
    // this.parseLocalCart();
  }

  parseLocalCart() {
    if (isPlatformBrowser(this.platformId)) {
      let localCartS = localStorage.getItem('cart');
      this.cartKits = [];
      this.cartEvents = [];
      let localPromocode = localStorage.getItem('bshop_promo');
      if (localPromocode) {
        this.setPromocode(localPromocode);
      }
      if (localCartS) {
        this.localCart = JSON.parse(localCartS);
        let searchProducts = '';
        this.cartEvents = this.localCart.filter(prod => prod.event_id);
        for (let product of this.localCart) {
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
        }
        console.log(this.cartEvents);
        if (searchProducts) {
          this.getDataService.getProductsList(searchProducts).subscribe((data) => {
            // console.log(data);
            this.products = data;
          });
        }
      } else {
        this.router.navigate(['']);
      }
    }
  }

  getProductData(product, type) {
    if (product) {
      let productCart = this.localCart.find(item => item.product_id == product.id);
      if (productCart) {
        switch (type) {
          case 'primary_image': return this.getThumbImg(product);
          case 'name': return product.name;
          case 'quantity': return productCart.quantity;
          case 'sum': return (productCart.quantity * Number(product.price));
          case 'english_name': return product.english_name;
          default: return '';
        }
      } else {
        return '';
      }
    } else {
      return '';
    }
  }

  getEventData(event, field) {
    if (event) {
      let events = this.localCart.filter(item => item.event_id);
      if (events.length) {
        let curEvent = events.find(event_item => event_item.event_id == event.event_id);
        if (curEvent) {
          return curEvent[field];
        } else {
          return 0;
        }
      }
    }
  }

  getDiscountSum() {
    let sum = this.getCartSum();
    let sum2 = this.getCartSum(true);
    return (sum - sum2);
  }

  getCartSum(discount: boolean = false) {
    if (isPlatformBrowser(this.platformId)) {
      let localCart = JSON.parse(localStorage.getItem('cart'));
      let sum = 0, sumForDiscount = 0, sumWODiscount = 0;
      this.showFreeDelivery = true;
      if (localCart) {
        localCart.forEach(prod => {
          if (prod.product_id) {
            sum += (prod.quantity * Number(prod.price));
            sumForDiscount += (prod.quantity * Number(prod.price));
          }
          if (prod.event_id) {
            sum += this.getEventPrice(prod);
            if (prod.dont_apply_promo) {
              sumWODiscount += this.getEventPrice(prod);
            } else {
              sumForDiscount += this.getEventPrice(prod);
            }
          }
        });
        if (discount) {
          if (this.promoDiscount) {
            sum = sumForDiscount * (1 - this.promoDiscount) + sumWODiscount;
          } else {
            sum = sum * (1 - this.promoDiscount);
          }
        }
        return sum;
      } else {
        return 0;
      }
    }
  }

  getCartCount() {
    switch (this.localCart.length) {
      case 1:
      case 21: return this.localCart.length + ' товар';
      case 2:
      case 3:
      case 4:
      case 22:
      case 23:
      case 24: return this.localCart.length + ' товара';
      default: return this.localCart.length + ' товаров';
    }
  }

  changeQuantity(product, mode) {
    if (product) {
      let productCart = this.localCart.find(item => item.product_id === product.id);
      if (productCart) {
        if (mode === 'less') {
          productCart.quantity -= 1;
        } else {
            productCart.quantity += 1;
        }
      }
      if (productCart.quantity <= 1) {
        productCart.quantity = 1;
      }
      if (isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('cart');
        localStorage.setItem('cart', JSON.stringify(this.localCart));
        if (this.promoDiscount) {
          this.promocodeText = 'Скидка на заказ (' + (this.promoDiscount * 100) + '%): ' + Math.floor(this.getDiscountSum()) + '&nbsp;₽';
        }
      }
    }
  }

  changeEventQuantity(ev, mode) {
    if (ev) {
      let productCart = this.localCart.find(item => item.event_id === ev.event_id);
      if (productCart) {
        if (mode === 'less') {
          productCart.quantity -= 1;
        } else {
            productCart.quantity += 1;
        }
      }
      if (productCart.quantity <= 1) {
        productCart.quantity = 1;
      }
      if (isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('cart');
        localStorage.setItem('cart', JSON.stringify(this.localCart));
      }
    }
  }

  confirmOrder() {
    this.router.navigate(['order/confirm']);
  }

  removeFromCart(product: any) {
    if (product) {
      let ind = this.localCart.findIndex(item => item.product_id == product.id);
      if (ind > -1) {
        this.localCart.splice(ind, 1);
      } else {
        ind = this.localCart.findIndex(item => item.event_id == product.id);
        if (ind > -1) {
          this.localCart.splice(ind, 1);
        }
      }
      let indP = this.products.findIndex(item => item.id == product.id);
      if (indP > -1) {
        this.products.splice(indP, 1);
      } else {
        indP = this.cartKits.findIndex(item => item.id == product.id);
        if (indP > -1) {
          this.cartKits.splice(indP, 1);
        } else {
          indP = this.cartEvents.findIndex(item => item.event_id == product.id);
          if (indP > -1) {
            this.cartEvents.splice(indP, 1);
          }
        }
      }

      if (isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('cart');
        if (this.localCart.length) {
          localStorage.setItem('cart', JSON.stringify(this.localCart));
          AppDataService.cartChange$.emit();
        } else {
          localStorage.removeItem('cart');
          localStorage.removeItem('bshop_promo');
          this.router.navigate(['catalog']);
          AppDataService.cartChange$.emit();
        }
      }
    }
  }

  trackProducts(index, item) {
    return item.id;
  }

  trackEvents(index, item) {
    return item.event_id;
  }

  getProgramData(kit, type) {
    if (kit) {
      if (kit.kit_images) {
        return kit.kit_images[0].image;
      } else {
        return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
      }
    } else {
      return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
    }
  }

  getEventImg(promo) {
    if (promo && promo.event_image) {
      return promo.event_image;
    } else {
      return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
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

  openCatalog() {
    this.router.navigate(['catalog']);
  }

  setPromocode(code: string) {
    if (!code) {
      return;
    }
    if (code === 'DARI2019') {
      this.snackBar.open('Промокод успешно активирован!', 'x', {
        duration: 3000
      });
      if (isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('bshop_promo');
        localStorage.setItem('bshop_promo', code);
      }
      this.orderHasPromocode = true;
      this.promocodeText = 'Ваш подарок по промокоду: гидроколлагеновые патчи!';
    } else {
      this.orderHasPromocode = false;
      this.getDataService.getPromocodeInfo(code).subscribe((res: Promocode) => {
        if (res) {
          if (res.code_type === 2) {
            this.promocodeText = ''; // 'Кэшбэк (5%): ' + ((this.getCartSum()) / 20).toFixed(2) + '&nbsp;₽';
          }
          if (res.code_type === 1) {
            if (res.discount <= 1) {
              this.promoDiscount = res.discount;
              this.promocodeText = 'Скидка на заказ (' + (res.discount * 100) + '%): ' + Math.floor(this.getDiscountSum()) + '&nbsp;₽';
              this.snackBar.open('Обращаем ваше внимание, что промокод не действует на товары со скидкой', 'x', {
                duration: 3500
              });
            } else {
              this.snackBar.open('Промокод не действителен, попробуйте ввести другой.', 'x', {
                duration: 3000
              });
              this.promocodeText = '';
              this.promocode = '';
              if (isPlatformBrowser(this.platformId)) {
                localStorage.removeItem('bshop_promo');
              }
              return;
            }
          }
          if (res.code_type === 0) {
            this.promocodeText = 'Ваш подарок по промокоду: ' + res.gift.name;
          }
          this.orderHasPromocode = true;
          if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('bshop_promo');
            localStorage.setItem('bshop_promo', code);
          }
        } else {
          this.snackBar.open('Промокод не действителен, попробуйте ввести другой.', 'x', {
            duration: 3000
          });
          this.promocodeText = '';
          this.promocode = '';
        }
      }, (error) => {
        this.snackBar.open('Промокод не действителен, попробуйте ввести другой.', 'x', {
          duration: 3000
        });
        this.promocodeText = '';
        this.promocode = '';
      });
      // this.orderHasPromocode = false;
      // this.promocodeText = '';
      // this.promocode = '';
    }
    this.showFreeDelivery = (this.getCartSum(true) < 4000);
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  deletePromocode() {
    this.orderHasPromocode = false;
    this.promocode = '';
    this.promocodeText = '';
    this.promoDiscount = 0;
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('bshop_promo');
    }
  }

}
