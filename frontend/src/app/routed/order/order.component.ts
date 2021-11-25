import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { FormControl, FormGroup, FormBuilder, Validators } from '@angular/forms';
import { registerLocaleData } from '@angular/common';
import ru from '@angular/common/locales/ru';
import { Subscription } from 'rxjs';
import { debounceTime, takeWhile } from 'rxjs/operators';
import { GetDataService } from '../../shared/services/get-data.service';
import { AppDataService } from '../../shared/services/app-data.service';
import { Person } from '../../shared/entities/person';
import { Promocode } from '../../shared/entities/product';

@Component({
  selector: 'app-order',
  templateUrl: './order.component.html',
  styleUrls: ['./order.component.scss']
})
export class OrderComponent implements OnInit, OnDestroy {

  private subscription: Subscription;
  public id: string;
  public orderData: any;
  public productsData: any[];
  public kitsData: any[];
  public orderEvents: any[];
  public loggedIn: boolean;
  public user: Person;
  public bonusAmount: number;
  public isPartner = false;
  private isActiveComponent: boolean;
  public promoDiscount = false;
  public promoDiscountValue = 0;
  public promoRef = false;

  orderForm = this.fb.group({
    bonusDiscount: new FormControl('', Validators.min(0))
  });


  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private getDataService: GetDataService,
    private snackBar: MatSnackBar,
    private fb: FormBuilder
  ) {
    this.subscription = activateRoute.params.subscribe((params) => {
      this.id = params['id'];
      this.getData();
    });
   }

  checkPartner() {
    this.isPartner = false;
    if (this.user && this.loggedIn) {
      if (this.user.partner_type === 'Партнер 3 уровня (дистрибьютор)') {
        this.isPartner = true;
      } else {
        this.isPartner = false;
      }
    }
  }

  ngOnInit() {
    this.isPartner = false;
    this.isActiveComponent = true;
    registerLocaleData( ru );
    if (this.id) {
      // this.getData();
      if (AppDataService.user) {
        this.user = AppDataService.user;
        this.loggedIn = AppDataService.userLoggedIn;
        this.bonusAmount = (this.user.available_bonus_amount) ? Math.floor(this.user.available_bonus_amount) : 0;
        this.checkPartner();
      }
    } else {
      this.router.navigate(['']);
    }
    AppDataService.userStatusChange$.subscribe(() => {
      this.loggedIn = AppDataService.userLoggedIn;
    });
    AppDataService.userDataChange$.subscribe((data) => {
      if (data) {
        this.loggedIn = true;
        this.user = data;
        this.bonusAmount = (this.user.available_bonus_amount) ? Math.floor(this.user.available_bonus_amount) : 0;
        this.checkPartner();
      }
    });

    let bonusDiscount = this.orderForm.get('bonusDiscount');
    bonusDiscount.valueChanges.pipe(debounceTime(100), takeWhile(() => this.isActiveComponent)).subscribe((data) => {
      if (bonusDiscount.value) {
        if (Number(data)) {
          if (this.user) {
            data = Math.min(data, this.bonusAmount, this.getCartSum(true));
          } else {
            data = 0;
          }
        } else {
          data = 0;
        }
        bonusDiscount.patchValue(Math.round(data));
      } else {
        bonusDiscount.patchValue(0);
      }
    });
  }

  getData() {
    this.kitsData = [];
    this.orderEvents = [];
    if (this.id) {
      this.getDataService.getOrderData(this.id).subscribe((data) => {
        // console.log(data);
        this.orderData = data;
        if (data) {
          this.productsData = data.order_products;
          this.orderEvents = data.order_events;
          if (this.orderData.promo_discount) {
            if (this.orderData.promo_discount <= 1) {
              this.promoDiscount = true;
              this.promoDiscountValue = this.orderData.promo_discount;
            }
          }
          if (this.orderData.promocode) {
            this.getDataService.getPromocodeInfo(this.orderData.promocode).subscribe((res: Promocode) => {
              if (res) {
                if (res.code_type === 1) {

                }
                if (res.code_type === 2) {
                  this.promoRef = true;
                }
              }
            });
          }
          for (let kit of data.order_kits) {
            this.getDataService.getProgramData(kit.kit_id).subscribe((res) => {
              if (res) {
                this.kitsData.push(res);
              }
            });
          }
        }
        console.log(this.orderData.payed);
        if (!this.orderData.payed) {
          if (this.user) {
            this.orderForm.get('bonusDiscount').patchValue(Math.min(this.user.available_bonus_amount, Math.round(this.getCartSum())));
          }
        }
      });
    } else {
      this.router.navigate(['']);
    }
  }

  getCartSum(bonus: boolean = false) {
    let sum = this.orderData.order_products.reduce((acc, curr) => acc += curr.amount, 0) +
              this.orderData.order_kits.reduce((acc, cur) => acc += cur.amount, 0);
    if (this.promoDiscount) {
      sum = Math.round(sum * (1 - this.promoDiscountValue));
    }
    if (this.orderEvents.length) {
      this.orderEvents.forEach(ev => {
        ev.order_event_products.forEach(prod => {
          sum += prod.amount;
        });
      });
    }
    return (bonus) ? Math.floor(sum / 2) : sum;
  }

  getProductData(product, type) {
    if (product) {
      const productCart = this.orderData.order_products.find(item => item.product_id === product.id);
      if (productCart) {
        switch (type) {
          case 'quantity': return productCart.quantity;
          case 'sum': return (productCart.quantity * Number(product.price));
          default: return '';
        }
      }
    }
  }

  getProgramData(kit, type) {
    if (kit) {
      const kitCart = this.orderData.order_kits.find(item => item.kit_id === kit.id);
      if (kitCart) {
        switch (type) {
          case 'quantity': return kitCart.quantity;
          case 'image': return (kit.kit_images) ? kit.kit_images[0].image : '/assets/logo-new.jpg';
        }
      }
    }
  }

  getEventImg(promo) {
    if (promo && promo.event.image) {
      return promo.event.image;
    } else {
      return '/assets/logo-new.jpg';
    }
  }

  getEventPrice(promo) {
    let sum = 0;
    if (promo) {
      if (promo.event && promo.event.price) {
        sum = promo.event.price;
      } else {
        promo.order_event_products.forEach(prod => {
          sum += prod.amount;
        });
      }
    }
    return sum;
  }

  getAddress() {
    if (this.orderData) {
      let adr = this.orderData.address;
      if (this.orderData.delivery_point_address) {
        return this.orderData.delivery_point_address;
      }
      if (adr) {
        return adr.postcode + ', ' +
        ((adr.region) ? adr.region + ',' : '') +
        ((adr.district) ? adr.district + ',' : '') +
        ((adr.city) ? adr.city + ',' : '') +
        ((adr.settlement) ? ((adr.settlement != adr.city) ? adr.settlement + ', ' : '') : '') +
        ((adr.street) ? adr.street + ', ' : '') +
        ((adr.house) ? adr.house + ', ' : '') +
        ((adr.flat) ? ', кв.' + adr.flat : '');
      }
    } else {
      return '';
    }
  }

  getDeliveryType() {
    if (this.orderData) {
      switch (this.orderData.shipping_method_id) {
        case 0: return 'Почта России';
        case 1: return 'EMS';
        case 2: return 'СДЭК до двери';
        case 3: return 'СДЭК до ПВЗ';
        case 7: return 'Самовывоз';
        case 8: return 'Курьер по Оренбургу';
        default: return 'Почта России';
      }
    }
  }

  pay() {
    if (this.orderData) {
      if (this.user) {
        let bonusDiscount = this.orderForm.get('bonusDiscount');
        this.getDataService.getPaymentLinkUser(this.id, this.orderData.shipping_amount, bonusDiscount.value).subscribe((data) => {
          if (data) {
            if (!data.error) {
              window.open(data.data, '_self');
            } else {
              this.snackBar.open(data.message, 'x', {
                duration: 3000
              });
            }
          }
        }, (error) => {
          this.snackBar.open(error.error.message, 'x', {
            duration: 3000
          });
        });
      } else {
        this.getDataService.getPaymentLink(this.id, this.orderData.shipping_amount).subscribe((data) => {
          if (data) {
            if (!data.error) {
              window.open(data.data, '_self');
            } else {
              this.snackBar.open(data.message, 'x', {
                duration: 3000
              });
            }
          }
        }, (error) => {
          this.snackBar.open(error.error.message, 'x', {
            duration: 3000
          });
        });
      }
    }
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  ngOnDestroy() {
    this.isActiveComponent = false;
  }

}
