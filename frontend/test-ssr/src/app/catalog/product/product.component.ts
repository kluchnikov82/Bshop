import { Component, OnInit, ViewChild, ElementRef, Inject, PLATFORM_ID } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { trigger, state, style, transition, animate, keyframes } from '@angular/animations';
import { MatDialog, MatSnackBar } from '@angular/material';
import { Title, Meta } from '@angular/platform-browser';
import { AppDataService } from '../../services/app-data.service';
import { GetDataService } from '../../services/get-data.service';
import { CatalogService, Category } from './../catalog.service';
import { Subscription } from 'rxjs';
// import { PerfectScrollbarComponent } from 'ngx-perfect-scrollbar';
import { PopupadviceComponent } from '../../popup/popupadvice/popupadvice.component';

@Component({
  selector: 'app-product',
  templateUrl: './product.component.html',
  styleUrls: ['./product.component.scss'],
  animations: [
    trigger('animateCart', [
      transition('initial => added', animate('0.8s ease-in', keyframes([
        style({bottom: '17px', left: '85px', opacity: 0, 'z-index': -1, offset: 0}),
        style({bottom: '200px', left: '100px', opacity: 0.5, 'z-index': 10, offset: 0.2}),
        style({bottom: '500px', left: '300px', opacity: 0.5, 'z-index': 10, offset: 0.5}),
        style({bottom: '500px', left: '300px', opacity: 0, 'z-index': -1, offset: 1})
      ]))),
      transition('added => initial', animate('0s'))
    ]),
    trigger('animateToggle', [
      transition('void => *', [
        style({left: 5000}),
        animate('0.5s', style({left: 0}))
      ]),
      transition('* => void', [
        animate('0.2s', style({left: -5000}))
      ])
    ])
  ]
})
export class ProductComponent implements OnInit {

  scrollPosition = 0;

  // @ViewChild(PerfectScrollbarComponent) sliderRef?: PerfectScrollbarComponent;
  @ViewChild('blockComments') blockComment: ElementRef;

  public currentCategory: any;
  public currentSubcat: any;
  public menuList: Category[];
  public product: any;
  private subscription: Subscription;
  private id: any;
  public comments: any;
  public productQuantity: any;
  public visibleComponents: any[] = [];
  public activeComponents: any[] = [];
  public rating: number[] = [1, 2, 3, 4, 5];
  public relativeType: boolean;
  public relativeProducts: any[];
  public seenProducts: any[];
  public userLogged: boolean;
  public activeTab: string;
  public bClist: any[];

  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private http: HttpClient,
    private getDataService: GetDataService,
    private catalogService: CatalogService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private title: Title,
    private meta: Meta,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {

    AppDataService.userStatusChange$.subscribe(() => {
      this.userLogged = AppDataService.userLoggedIn;
    });
   }

  ngOnInit() {
    this.relativeType = true;
    this.relativeProducts = [];
    this.seenProducts = [];
    this.catalogService.catalog$.subscribe(res => {
      this.menuList = res;
      if (this.currentCategory && this.currentSubcat) {
        this.getBreadcrumbs();
      }
    });
    this.activateRoute.paramMap.subscribe(params => {
      // console.log(AppDataService.currentCategory);
      // console.log(AppDataService.currentSubcat);
      this.currentCategory = params.get('category');
      this.currentSubcat = params.get('subcategory');
      this.id = params.get('id');
      this.getData();
    });

    this.userLogged = AppDataService.userLoggedIn;
    this.productQuantity = 1;
    this.activeTab = 'description';
    // this.currentCategory = AppDataService.currentCategory;
    this.product = {
      name: '',
      kits: '',
      state: 'initial'
    };
    this.comments = {
      count: 0
    };
    let localSeenProductsString;
    if (isPlatformBrowser(this.platformId)) {
      localSeenProductsString = localStorage.getItem('bshop_seen');
    }
    let localSeenProducts: any[];
    if (localSeenProductsString) {
      localSeenProducts = JSON.parse(localSeenProductsString);
    } else {
      localSeenProducts = [];
    }
    // if (AppDataService.currentProduct) {
    //   this.product = AppDataService.currentProduct;
    //   // this.bClist.push({
    //   //   text: this.currentCategory,
    //   //   link: '/catalog'
    //   // })
    //   this.getDataService.getProductInfo(this.id).subscribe((data) => {
    //     this.product = data;
    //     // this.bClist.push({
    //     //   text: this.product.name,
    //     //   link: null
    //     // })
    //     this.product.state = 'initial';
    //     if (data.categories.length) {
    //       this.currentCategory = data.categories[0].category_name;
    //     }
    //     this.activeComponents = this.product.active_components;
    //     this.relativeProducts = this.product.linked_products;
    //     if (this.relativeProducts.length) {
    //       this.relativeProducts.unshift({
    //         product_id: this.product.id,
    //         product_name: this.product.name,
    //         price: this.product.price,
    //         primary_image: this.product.primary_image,
    //         english_name: this.product.english_name,
    //         hit: this.product.hit,
    //         new: this.product.new,
    //         product_images: this.product.product_images,
    //         check: true
    //       });
    //     }
    //     for (let p of this.relativeProducts) {
    //       p.check = true;
    //       p.price = Number(p.price);
    //     }
    //     // console.log(this.product);
    //     if (localSeenProducts.find(i => i.id == this.id)) {
    //     } else {
    //       localSeenProducts.unshift({
    //         product_id: this.product.id,
    //         product_name: this.product.name,
    //         price: this.product.price,
    //         primary_image: this.product.primary_image,
    //         english_name: this.product.english_name,
    //         hit: this.product.hit,
    //         new: this.product.new,
    //         product_images: this.product.product_images,
    //         check: true
    //       });
    //     }
    //     if (localSeenProducts.length > 5) {
    //       localSeenProducts = localSeenProducts.slice(0, 4);
    //     }
    //     if (isPlatformBrowser(this.platformId)) {
    //       localStorage.removeItem('bshop_seen');
    //       localStorage.setItem('bshop_seen', JSON.stringify(localSeenProducts));
    //     }
    //     this.seenProducts = localSeenProducts.filter(item => item.product_id != this.id);
    //   });
    // } else {
    //   // this.getData();
    // }
    // console.log(AppDataService.currentCategory);
    // this.getDataService.getProductComments(this.id).subscribe((data) => {
    //   this.comments = data;
    //   // console.log(this.comments);
    // });
  }

  getBreadcrumbs() {
    this.bClist = [];
    this.bClist = [{
      text: 'Главная',
      link: '/'
    }, {
      text: 'Каталог',
      link: '/catalog'
    }];
    let currentCat: Category, currentSub;
    if (this.currentCategory) {
      currentCat = this.menuList.find(cat => cat.slug == this.currentCategory);
      if (currentCat && this.currentSubcat) {
        currentSub = currentCat.subcats.find(sub => sub.slug == this.currentSubcat);
        this.bClist.push({
          text: currentCat.name,
          link: '/catalog/' + currentCat.slug
        });
        if (currentSub) {
          this.bClist.push({
            text: currentSub.name,
            link: '/catalog/' + currentCat.slug + '/' + currentSub.slug
          });
        }
      }
      this.bClist.push({
        text: this.product.name,
        link: ''
      });
    }
  }

  changeTab(tab: string) {
    this.activeTab = tab;
  }

  getData() {
    let localSeenProductsString;
    if (isPlatformBrowser(this.platformId)) {
      localSeenProductsString = localStorage.getItem('bshop_seen');
    }
    let localSeenProducts: any[];
    if (localSeenProductsString) {
      localSeenProducts = JSON.parse(localSeenProductsString);
    } else {
      localSeenProducts = [];
    }
    this.getDataService.getProductInfo(this.id).subscribe((data) => {
      this.product = data;
      this.getDataService.getProductComments(this.product.id).subscribe((res) => {
        this.comments = res;
      });
      this.title.setTitle('Купить онлайн ' + this.product.name + ' с доставкой по России | DARI-COSMETICS');
      this.meta.updateTag({ name: 'description', content: this.product.description });
      this.product.state = 'initial';
      // if (data.categories.length) {
      //   this.currentCategory = data.categories[0].category_name;
      // }
      // if (this.currentCategory) {
      //   this.bClist.push({
      //     text: this.currentCategory,
      //     link: '/catalog/' + this.currentCategory
      //   });
      // }
      // if (this.currentSubcat) {
      //   this.bClist.push({
      //     text: 
      //   })
      // }
      // this.bClist.push({
      //   text: this.product.name,
      //   link: null
      // });
      this.activeComponents = this.product.active_components;
      this.relativeProducts = this.product.linked_products.concat();
      if (this.relativeProducts.length) {
        this.relativeProducts.unshift(this.product);
      }
      for (let p of this.relativeProducts) {
        p.check = true;
      }
      // console.log(this.product);
      if (localSeenProducts.find(i => i.product_id == this.id)) {
      } else {
        // localSeenProducts.unshift(this.product);
      }
      if (localSeenProducts.length > 5) {
        localSeenProducts = localSeenProducts.slice(0, 4);
      }
      if (localSeenProducts.length) {
        if (isPlatformBrowser(this.platformId)) {
          localStorage.removeItem('bshop_seen');
          localStorage.setItem('bshop_seen', JSON.stringify(localSeenProducts));
        }
      }
      this.seenProducts = localSeenProducts.filter(item => item.product_id != this.id);
      this.getBreadcrumbs();
    });
  }

  toggleCheck(event, prod) {
    prod.check = !prod.check;
    event.stopPropagation();
  }

  getProductImage() {
    return (this.product.primary_image) ? this.product.primary_image : 'https://dari-cosmetics.ru/assets/no-photo.jpg';
  }

  changeQuantity(mode) {
    if (mode == 'less') {
      this.productQuantity -= 1;
    } else {
      this.productQuantity += 1;
    }

    if (this.productQuantity <= 1) {
      this.productQuantity = 1;
    }
  }

  getActiveComponentImg(component) {
    if (component.image) {
      return component.image;
    } else {
      return 'https://dari-cosmetics.ru/assets/no-photo.jpg';
    }
  }

  moveSlider(arrow) {
    let maxScrollPosition = (this.activeComponents.length - 1) * 450;
    // this.scroll
    if (arrow == 'left') {
      this.scrollPosition -= 500;
      if (this.scrollPosition <= 0) {
        this.scrollPosition = 0;
      }
      // this.sliderRef.directiveRef.scrollTo(this.scrollPosition, 0, 500);
    } else {
      this.scrollPosition += 500;
      if (this.scrollPosition >= maxScrollPosition) {
        this.scrollPosition = maxScrollPosition;
      }
      // this.sliderRef.directiveRef.scrollTo(this.scrollPosition, 0, 500);
    }
  }

  addToCart() {
    if (this.product) {
      AppDataService.addToCart(this.product, this.productQuantity);
      this.snackBar.open('Товар добавлен в корзину', 'x', {
        duration: 3000
      });
    }
  }

  getCommentImg(comment) {
    if (comment.user.avatar) {
      return comment.user.avatar;
    } else {
      return 'https://dari-cosmetics.ru/assets/otzyvy.jpg';
    }
  }

  getUserName(comment) {
    if (comment) {
      if (comment.user.last_name) {
        return comment.user.first_name + ' ' + comment.user.last_name;
      } else {
        return '';
      }
    } else {
      return '';
    }
  }

  openPage(page: string) {
    this.router.navigate([page]);
  }

  getTooltipText(item: any) {
    let benefit = item.benefits[0];
    if (benefit) {
      return benefit; // .substring(0,200);
    } else {
      return '';
    }
  }

  getCommentText(txt: string) {
    return txt.substring(0, 150) + '...';
  }

  sendAdvice() {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'product',
        id: this.id,
        name: this.product.name
      }
    });
  }

  openImg(url: string) {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'image',
        link: url
      }
    });
  }

  showAdvices() {
    let coordY = this.blockComment.nativeElement.getBoundingClientRect().top;
    if (isPlatformBrowser(this.platformId)) {
      window.scrollTo({left: 0, top: coordY, behavior: 'smooth'});
    }
  }

  getRelativeSum() {
    let sum = 0;
    for (let prod of this.relativeProducts) {
      if (prod.check) {
        sum += Number(prod.price);
      }
    }
    return sum;
  }

  buyRelative() {
    for (let prod of this.relativeProducts) {
      if (prod.check) {
        if (!prod.product_id) {
          prod.product_id = prod.id;
        }
        AppDataService.addToCart(prod, 1, true);
      }
    }
    this.snackBar.open('Товары добавлены в корзину.', 'x', {
      duration: 3000
    });
  }

  openComment(comment: any) {
    let dialogRef = this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'comment',
        comment: comment
      }
    });
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  getActiveComponentText(item) {
    if (item) {
      if (item.description) {
        let pIndex = item.description.indexOf('</p>');
        if (pIndex > -1) {
          return item.description.substring(0, pIndex);
        } else {
          return item.description;
        }
      } else {
        return '';
      }
    } else {
      return '';
    }
  }

}
