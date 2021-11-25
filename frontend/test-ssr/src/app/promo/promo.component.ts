import { Component, OnInit } from '@angular/core';
import { GetDataService } from './../services/get-data.service';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { AppDataService } from '../services/app-data.service';
import { PromoEvent, EventProduct } from '../entities/product';

@Component({
  selector: 'app-promo',
  templateUrl: './promo.component.html',
  styleUrls: ['./promo.component.scss']
})

export class PromoComponent implements OnInit {

  public events: PromoEvent[];
  productList: string[];
  productListData: any[];

  constructor(
    private getDataService: GetDataService,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
    this.productList = [];
    this.getDataService.getEventsList().subscribe((data) => {
      if (data) {
        this.events = data;
        this.events.sort((i1, i2) => i1.seq_no - i2.seq_no);
        this.events.forEach(event => {
          for (let prod of event.event_products_for2any) {
            prod.check = true;
          }
          for (let prod of event.event_products_some_the_same) {
            prod.check = true;
          }
        });
      }
    });
  }

  openEventProd(promoEvent: PromoEvent) {
    if (promoEvent) {
      if (promoEvent.event_products_some_the_same.length) {
        let prodId = promoEvent.event_products_some_the_same[0].product_id;
        if (prodId) {
          this.router.navigate(['catalog/product/' + prodId]);
        }
      }
    }
  }

  toggleCheck(event, prod, promoEvent: any = false) {
    prod.check = !prod.check;
    if (promoEvent) {
      if (promoEvent.event_products_for2any.length > 3) {
        let checks = 0;
        for (let p of promoEvent.event_products_for2any) {
          if (p.check) {
            checks++;
          }
        }
        if (checks > 1) {
          promoEvent.gift_count = 1;
        }
        if (checks == 4) {
          promoEvent.gift_count = 2;
        }
        if (checks < 2) {
          promoEvent.gift_count = 0;
        }
      }
    }
    event.stopPropagation();
  }

  getProdData(prod: EventProduct, field: string) {
    let searchProd = this.productListData.find(i => i.id == prod.product_id);
    let img = 'https://dari-cosmetics.ru/assets/no-photo.jpg';
    if (field == 'primary_image') {
      return searchProd.primary_image || img;
    }
    return searchProd[field] || '';
  }

  getPromoSum(promoEvent: PromoEvent) {
    let sum = 0;
    if (promoEvent.event_products_some_the_same.length) {
      for (let prod of promoEvent.event_products_some_the_same) {
        if (prod.check) {
          sum += prod.price * prod.quantity;
        }
      }
    }
    if (promoEvent.event_products_for2any.length) {
      for (let prod of promoEvent.event_products_for2any) {
        if (prod.check) {
          sum += prod.price;
        }
      }
    }
    if (promoEvent.discount_product) {
      if (promoEvent.discount_product.discount) {
        sum = promoEvent.discount_product.price * (1 - (promoEvent.discount_product.discount / 100));
        sum = Math.round(sum);
      }
    }
    return sum;
  }

  buyRelative(promoEvent: PromoEvent) {
    AppDataService.addEventToCart(promoEvent);
    this.snackBar.open('Акция добавлена в корзину', 'x', {
      duration: 3000
    });
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  getPromoWidth(promo: PromoEvent) {
    let res = 100;
    if (promo) {
      if (promo.discount_product && promo.discount_product.id) {
        res = 30;
      } else if (promo.event_products_for2any) {
        res = (promo.event_products_for2any.length * 20);
        if (promo.gift_count) {
          res = ((promo.event_products_for2any.length + 1) * 20);
        }
      } else if (promo.event_products_some_the_same) {

      }
    }
    if (res > 100) {
      res = 100;
    }
    if (!res) {
      res = 50;
    }
    return res.toString();
  }

}
