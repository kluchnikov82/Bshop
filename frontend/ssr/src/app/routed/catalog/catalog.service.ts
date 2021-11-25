import { Injectable } from '@angular/core';
import { Router, Resolve } from '@angular/router';
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';
import { GetDataService } from '../../services/get-data.service';
import { Product } from '../../shared/entities/product';

export interface Category {
  id: string;
  state: string;
  expanded: boolean;
  name: string;
  slug: string;
  description: string;
  image: string;
  header_image: string;
  subcats: Subcategory[];
  SEO_description: string;
  SEO_title: string;
}

export interface Subcategory {
  id: string;
  name: string;
  slug: string;
  subcat_products: Product[];
  SEO_description: string;
  SEO_title: string;
}

@Injectable({
  providedIn: 'root'
})
export class CatalogService {

  private catalogData: Category[];
  public catalogBSubject: BehaviorSubject<Category[]>;
  notSearching = ['для', 'о', ' '];

  constructor(
    private getDataService: GetDataService
  ) {
    this.catalogBSubject = new BehaviorSubject([]);
  }

  getCatalog(): Observable<Category[]> {
    const catalogSubject = new Subject();
    if (!this.catalogData) {
      this.getDataService.getMenu().subscribe((data) => {
        this.catalogData = data.results;
        this.catalog = data.results;
        catalogSubject.next(data.results);
        catalogSubject.complete();
      }, (err) => {
        console.log('Ошибка загрузки каталога');
        console.log(err);
      });
    } else {
      this.catalog = this.catalogData;
      catalogSubject.next(this.catalogData);
      catalogSubject.complete();
    }

    return catalogSubject.asObservable() as Observable<Category[]>;

  }

  get catalog() {
    return this.catalogData;
  }

  get catalog$(): Observable<Category[]> {
    return this.catalogBSubject.asObservable();
  }

  set catalog(data: Category[]) {
    this.catalogBSubject.next(data);
    // this.catalogBSubject.complete();
  }

  matchSearch(product: Product, searchText: string) {
    let prodName = product.name.toLowerCase();
    let prodCode = product.code;
    if (prodName.includes(searchText) || prodCode.includes(searchText)) {
      return true;
    } else {
      return false;
    }
  }

  search(term: string, cb: any = false) {
    let found = [];
    let searchingText = term.toLowerCase();
    let searchingTextArray = searchingText.split(' ');
    this.getDataService.getCatalog().subscribe(res => {
      if (res) {
        for (let category of res) {
          for (let subcat of category.subcats) {
            for (let prod of subcat.subcat_products) {
              for (let str of searchingTextArray) {
                if (this.notSearching.includes(str)) {
                  continue;
                }
                if (this.matchSearch(prod, str)) {
                  let sProd = found.find(item => item.id == prod.id);
                  if (!sProd) {
                    prod.category = {
                      name: category.name,
                      slug: category.slug
                    },
                    prod.subcat = {
                      name: subcat.name,
                      slug: subcat.slug
                    };
                    found.push(prod);
                  }
                  break;
                }
              }
            }
          }
        }
        if (cb) {
          cb(found);
        }
      }
    });
  }
}
