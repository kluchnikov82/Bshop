import { Component, OnInit, ElementRef, ViewChild, Inject, PLATFORM_ID } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { FormControl } from '@angular/forms';
import { MatSnackBar } from '@angular/material';
import { GetDataService } from './../services/get-data.service';
import { AppDataService } from './../services/app-data.service';
import { Category, Subcategory, CatalogService } from './catalog.service';
import { Product } from '../entities/product';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-catalog',
  templateUrl: './catalog.component.html',
  styleUrls: ['./catalog.component.scss'],
  animations: [
    trigger('expandPanel', [
      state('initial', style({height: 0, opacity: 0, 'z-index': -1})),
      state('expanded', style({height: '*', opacity: 1, 'z-index': 10})),
      transition('* => *', animate('0.2s'))
    ])
  ]
})

export class CatalogComponent implements OnInit {

  @ViewChild('catalogContent') public catalogRef: ElementRef;

  public currentCategoryId: string;
  public currentCategory: Category;
  public currentSubcatId: string;
  public currentSubcat: Subcategory;
  public categoryDescription: string;
  public filteredProducts: any[];
  public menuList: Category[];
  public activeCategory = false;
  public filteredKits: any[];
  public filterTypes = [
    {value: 'views', viewValue: 'По популярности'},
    {value: 'price', viewValue: 'По стоимости'}
  ];
  public selectedFilter: any;
  public pages = ['1', '2', '3'];
  public minPriceControl: FormControl = new FormControl();
  public maxPriceControl: FormControl = new FormControl();
  public minPrice: number;
  public maxPrice: number;
  public minPriceStart: number;
  public maxPriceStart: number;
  public filterState: string;
  public programState: string;
  public valueState: string;
  public priceRange: any;
  public bClist: any[];
  public isBrowser: boolean;
  public priceSliderConfig: any = {
    behaviour: 'drag',
    connect: true,
    start: [0, 100],
    step: 1,
    keyboard: true,
    range: {
      min: 0,
      max: 100
    }
  };

  notSearching = ['для', 'о', ' '];

  constructor(
    private acRoute: ActivatedRoute,
    private router: Router,
    private getDataService: GetDataService,
    private snackBar: MatSnackBar,
    private service: CatalogService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    AppDataService.searchProductStart$.subscribe((searchProd) => {
      this.searchProducts(searchProd);
    });
  }

  ngOnInit() {
    this.isBrowser = isPlatformBrowser(this.platformId);
    this.filteredKits = [];
    this.selectedFilter = 'views';
    this.filterState = 'initial';
    this.programState = 'initial';
    this.valueState = 'initial';
    this.minPriceControl.setValue(0);
    this.maxPriceControl.setValue(100);
    this.bClist = [];
    this.service.catalog$.subscribe((res) => {
      this.menuList = res;
      if (this.currentSubcat && this.currentCategory) {
        this.openCategory(this.currentCategory, this.currentSubcat);
      } else if (this.currentCategory) {
        this.openCategory(this.currentCategory);
      }
    });
    this.acRoute.paramMap.subscribe(params => {
      this.currentCategoryId = params.get('category');
      this.currentSubcatId = params.get('subcategory');
      console.log(params.get('category'));
      console.log(params.get('subcategory'));
      this.getCatalog();
    });
  }

  getCatalog() {
    if (!this.currentCategoryId) {
      this.currentCategoryId = this.menuList[0].slug;
      // document.location.href = ;
      this.router.navigate(['/catalog/' + this.currentCategoryId]);
      return;
    } else {
      this.getDataService.getCatalogCategory(this.currentCategoryId).subscribe((data) => {
        this.currentCategory = data as Category;
        AppDataService.currentCategory = data;
        if (!this.currentSubcatId) {
          this.openCategory(data);
        } else {
          this.getDataService.getCatalogSubcategory(this.currentSubcatId).subscribe((res) => {
            this.currentSubcat = res as Subcategory;
            AppDataService.currentSubcat = res;
            this.openCategory(this.currentCategory, this.currentSubcat);
          });
        }
      });
    }

    // if (!AppDataService.menuList) {
    //   this.getDataService.getCatalog().subscribe((data) => {
    //     AppDataService.menuList = data;
    //     this.menuList = data;
    //     if (this.menuList.length) {
    //       if (!this.currentCategoryId) {
    //         this.currentCategoryId = this.menuList[0].slug;
    //         this.currentCategory = this.menuList[0];
    //       }
    //     }
    //     for (let cat of this.menuList) {
    //       cat.expanded = false;
    //       cat.state = 'initial';
    //     }
    //     AppDataService.menuListChange$.emit();
    //     this.router.navigate(['catalog/' + this.currentCategoryId]);
    //   });
    // } else {
    //   this.menuList = AppDataService.menuList;
    //   for (let cat of this.menuList) {
    //     cat.expanded = false;
    //     cat.state = 'initial';
    //   }
    //   if (!this.currentCategoryId) {
    //     if (this.menuList) {
    //       this.currentCategoryId = this.menuList[0].slug;
    //       this.router.navigate(['catalog/' + this.currentCategoryId]);
    //       // this.currentCategory = this.menuList[0];
    //       // this.openCategory(this.currentCategory);
    //     }
    //   } else {
    //     this.getDataService.getCatalogCategory(this.currentCategoryId).subscribe((data) => {
    //       this.currentCategory = data as Category;
    //       AppDataService.currentCategory = data;
    //       if (!this.currentSubcatId) {
    //         this.openCategory(data);
    //       } else {
    //         this.getDataService.getCatalogSubcategory(this.currentSubcatId).subscribe((res) => {
    //           this.currentSubcat = res as Subcategory;
    //           AppDataService.currentSubcat = res;
    //           this.openCategory(this.currentCategory, this.currentSubcat);
    //         });
    //       }
    //     });
    //   }
    // }
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

  searchProducts(txt: string) {
    this.filteredProducts = [];
    let searchingText = txt.toLowerCase();
    let searchingTextArray = searchingText.split(' ');
    if (AppDataService.menuList) {
      for (let category of AppDataService.menuList) {
        for (let subcat of category.subcats) {
          for (let prod of subcat.subcat_products) {
            for (let str of searchingTextArray) {
              if (this.notSearching.includes(str)) {
                continue;
              }
              if (this.matchSearch(prod, str)) {
                let sProd = this.filteredProducts.find(item => item.id == prod.id);
                if (!sProd) {
                  this.filteredProducts.push(prod);
                }
                break;
              }
            }
          }
        }
      }
    }
  }

  sortCatalog() {
    if (this.selectedFilter == 'price') {
      this.filteredProducts.sort((item1, item2) => item1.price - item2.price);
    }
    if (this.selectedFilter == 'views') {
      this.filteredProducts.sort((item1, item2) => item1.hit_count - item2.hit_count)
    }
  }

  openCategory(category: Category, subcat: any = false) {
    this.bClist = [];
    for (let cat of this.menuList) {
      if (cat.id != category.id) {
        cat.expanded = false;
        cat.state = 'initial';
      } else {
        cat.expanded = true;
        cat.state = 'expanded';
      }
    }
    // category.state = 'expanded';
    // category.expanded = true; // (category.state === 'initial') ?  : 'initial'
    // AppDataService.menuList = this.menuList;
    // this.currentCategory = category.name;
    // this.currentSubcat = '';
    this.bClist = [];
    // AppDataService.currentCategory = category.name;
    this.bClist = [{
      text: 'Главная',
      link: '/'
    },
    {
      text: 'Каталог',
      link: '/catalog'
    },
    {
      text: category.name,
      link: '/catalog/' + category.slug
    }];
    if (subcat) {
      this.bClist.push({
        text: subcat.name,
        link: '/catalog/' + category.slug + '/' + subcat.slug
      });
    }
    this.changeCategory();
    // if (this.bClist.length > 3) {
    //   this.bClist.pop();
    // }
  }

  changeCategory() {
    this.filteredProducts = [];
    this.filteredKits = [];
    this.minPriceControl.setValue(0);
    this.maxPriceControl.setValue(0);
    let category = this.currentCategory;
    let subcat = this.currentSubcat;
    if (!subcat && category) {
      category.subcats.forEach(sub => {
        sub.subcat_products.forEach(prod => {
          if (this.filteredProducts.findIndex(p => p.id == prod.id) < 0) {
            prod.subcat = sub.slug;
            this.filteredProducts.push(prod);
          }
        });
      });
    } else if (subcat && category) {
      this.filteredProducts = subcat.subcat_products;
      this.filteredProducts.forEach(p => {
        p.subcat = subcat.slug;
      });
    }
    // if (category) {
    //   let filteredCategory = this.menuList.find(item => item.name == category);
    //   this.categoryDescription = filteredCategory.description;
    //   if (subcat) {
    //     let filteredSubcat = filteredCategory.subcats.find(sub => sub.name == subcat);
    //     if (filteredSubcat) {
    //       this.filteredProducts = filteredSubcat.subcat_products;
    //     } else {
    //       filteredCategory.subcats.forEach(item => {
    //         item.subcat_products.forEach(product => {
    //           if (!this.filteredProducts.find(item => item.id == product.id)) {
    //             this.filteredProducts.push(product);
    //           }
    //         });
    //       });
    //     }
    //   } else {
    //     filteredCategory.subcats.forEach(item => {
    //       item.subcat_products.forEach(product => {
    //         if (!this.filteredProducts.find(item => item.id == product.id)) {
    //           this.filteredProducts.push(product);
    //         }
    //       });
    //     });
    //   }
    //   this.activeCategory = true;
    // } else {
    //   this.categoryDescription = 'Каталог';
    // }

    if (this.filteredProducts.length) {
      for (let prod of this.filteredProducts) {
        prod.state = 'initial';
        let productKits = prod.kits;
        for (let kit of productKits) {
          if (!this.filteredKits.find(item => item.kit_id == kit.kit_id)) {
            this.filteredKits.push(kit);
          }
        }

      }
      let productList = this.filteredProducts.concat();
      productList.sort((i1, i2) => i1.price - i2.price);
      this.maxPriceStart = (productList[productList.length - 1].price);
      this.minPriceStart = (productList[0].price);
      this.maxPrice = (productList[productList.length - 1].price);
      this.minPrice = (productList[0].price);
      this.priceSliderConfig.start = [this.minPriceStart, this.maxPriceStart];
      this.priceSliderConfig.range = {
        min: this.minPriceStart,
        max: this.maxPriceStart
      };
      this.sortCatalog();
    }
    // console.log(this.filteredProducts);
    // console.log(this.filteredKits);
  }

  filterProducts(range: any = false) {
    if (this.menuList) {
      this.filteredProducts = [];
      let filteredCategory = this.menuList.find(item => item.name === this.currentCategory.name);
      let searchKits = [];
      this.filteredKits.forEach(kit => {
        if (kit.selected) {
          searchKits.push(kit);
        }
      });
      filteredCategory.subcats.forEach(item => {
        item.subcat_products.forEach(product => {
          if (searchKits.length) {
            searchKits.forEach(kit => {
              if (product.kits.find(item => item.kit_id == kit.kit_id)) {
                if (product.price >= this.minPrice && product.price <= this.maxPrice) {
                  this.filteredProducts.push(product);
                }
              }
            });
          } else {
            if (product.price >= this.minPrice && product.price <= this.maxPrice) {
              this.filteredProducts.push(product);
            }
          }
        });
      });
    }
  }

  changeSubcat(itemNode) {
    if (this.currentCategory) {
      this.currentSubcat = itemNode.name;
      this.changeCategory();
    }
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

  showProduct(product) {
    AppDataService.currentProduct = product;
    let link = product.id;
    if (product.slug) {
      link = product.slug;
    }
    this.router.navigate(['catalog/product/' + link]);
  }

  chooseKit(kit) {
    if (kit) {
      if (kit.selected) {
        kit.selected = false;
      } else {
        kit.selected = true;
      }
    }
    this.filterProducts();
  }

  toggleMenu(st: string) {
    if (st === 'initial') {
      st = 'expanded';
    } else {
      st = 'initial';
    }
    return st;
  }

  trackFilterProducts(index, elem) {
    return elem.id;
  }

  onChangeRange(event) {
    this.minPrice = event[0];
    this.maxPrice = event[1];
    this.filterProducts();
  }

  onChangePrice() {
    if (!this.minPrice) {
      this.minPrice = 0;
    }
    if (!this.maxPrice) {
      this.maxPrice = this.maxPriceStart;
    }
    this.priceRange = [this.minPrice, this.maxPrice];
    this.filterProducts();
  }

  getProductImage(product: any) {
    return AppDataService.getThumbImg(product);
  }

}
