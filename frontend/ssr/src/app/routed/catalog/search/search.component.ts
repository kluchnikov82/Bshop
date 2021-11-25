import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { MatSnackBar } from '@angular/material';
import { CatalogService } from './../catalog.service';
import { AppDataService } from './../../../services/app-data.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {

  private subscription: Subscription;
  public products = [];
  bClist = [{
    text: 'Главная',
    link: '/'
  },
  {
    text: 'Каталог',
    link: '/catalog'
  },
  {
    text: 'Результаты поиска',
    link: ''
  }];

  constructor(
    private aRoute: ActivatedRoute,
    private service: CatalogService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit() {
    this.subscription = this.aRoute.params.subscribe(params => {
      this.searchProducts(params['query']);
    });
  }

  search(query) {
    console.log(query);
  }

  searchProducts(txt: string) {
    this.service.search(txt, (res) => {
      this.products = res;
    });
  }

  getProductImage(product: any) {
    return AppDataService.getThumbImg(product);
  }

  addToCart(product: any = false, event) {
    if (product) {
      AppDataService.addToCart(product);
      event.stopPropagation();
      this.snackBar.open('Товар добавлен в корзину', 'x', {
        duration: 3000
      });
    }
  }

}
