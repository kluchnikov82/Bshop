import { Component, OnInit, Input } from '@angular/core';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { AppDataService } from './../../../services/app-data.service';
import { PromoEvent, EventProduct } from './../../../shared/entities/product';

@Component({
  selector: 'promo-event',
  templateUrl: './event.component.html',
  styleUrls: ['./event.component.scss']
})
export class EventComponent implements OnInit {

  @Input() promoEvent: PromoEvent;

  constructor(
    private router: Router,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
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

  getPromoSum(promoEvent: PromoEvent) {
    let sum = 0;
    if (promoEvent.price) {
      sum = promoEvent.price;
    } else {
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
      if (promoEvent.discount_product_for_n) {
        if (promoEvent.discount_for_n) {
          sum = promoEvent.discount_product_for_n.price * promoEvent.discount_product_count * (1 - (promoEvent.discount_for_n / 100));
          sum = Math.round(sum);
        }
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

}
