import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material';
import { Subscription } from 'rxjs';
import { GetDataService } from './../../services/get-data.service';
import { AppDataService } from './../../services/app-data.service';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-edit-order',
  templateUrl: './edit-order.component.html',
  styleUrls: ['./edit-order.component.scss']
})
export class EditOrderComponent implements OnInit {

  private subscription: Subscription;
  public id: string;
  public orderData: any;
  public productsData: any[];
  public kitsData: any[];
  public orderEvents: any[];

  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private getDataService: GetDataService,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) { }

  ngOnInit() {
    this.subscription = this.activateRoute.params.subscribe((params) => {
      this.id = params['id'];
      this.getData();
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
          if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('cart');
            localStorage.removeItem('bshop_promo');
            localStorage.removeItem('bshop_order');
            if (this.orderData.promocode) {
              localStorage.setItem('bshop_promo', this.orderData.promocode);
            }
            localStorage.setItem('bshop_order', JSON.stringify(this.orderData));
          }
          this.productsData = data.order_products;
          this.orderEvents = data.order_events;
          for (let kit of data.order_kits) {
            this.getDataService.getProgramData(kit.kit_id).subscribe((res) => {
              if (res) {
                this.kitsData.push(res);
              }
            });
          }
          this.productsData.forEach(prod => {
            AppDataService.addToCart(prod, prod.quantity, true, false, prod.id);
          });
          this.kitsData.forEach(kit => {
            AppDataService.addToCart(kit, kit.quantity, true, true, kit.id);
          });
          this.orderEvents.forEach(ev => {
            AppDataService.addEventToCart(ev, ev.quantity, ev.id);
          });
          this.router.navigate(['order/confirm']);
        }
      });
    } else {
      this.router.navigate(['']);
    }
  }

}
