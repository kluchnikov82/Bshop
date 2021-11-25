import { Component, OnInit, PLATFORM_ID, Inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { trigger, state, style, transition, animate, keyframes } from '@angular/animations';
import { DomSanitizer } from '@angular/platform-browser';
import { MatDialog, MatSnackBar } from '@angular/material';
import { Title, Meta } from '@angular/platform-browser';
import { Subscription } from 'rxjs';
import { AppDataService } from '../../../services/app-data.service';
import { GetDataService } from '../../../services/get-data.service';
import { PopupadviceComponent } from '../../../shared/popup/popupadvice/popupadvice.component';

interface ProgramProduct {
  code: string;
  description: string;
  english_name: string;
  hit: boolean;
  new: boolean;
  price: number;
  primary_image: string;
  product_id: string;
  product_name: string;
  products_count: number;
}

@Component({
  selector: 'app-care-program-item',
  templateUrl: './care-program-item.component.html',
  animations: [
    trigger('animateCart', [
      transition('initial => added', animate('0.8s ease-in', keyframes([
        style({bottom: '17px', left: '85px', opacity: 0, 'z-index': -1, offset: 0}),
        style({bottom: '200px', left: '100px', opacity: 0.5, 'z-index': 10, offset: 0.2}),
        style({bottom: '500px', left: '300px', opacity: 0.5, 'z-index': 10, offset: 0.5}),
        style({bottom: '500px', left: '300px', opacity: 0, 'z-index': -1, offset: 1})
      ]))),
      transition('added => initial', animate('0s'))
    ])
  ]
})
export class CareProgramItemComponent implements OnInit {

  private id: any;
  private subscription: Subscription;
  public programData: any;
  public preferences: any[] = [];
  public products: any[] = [];
  public stagesTabs: string[] = [];
  public formattedStages: any[] = [];
  public activeTab = '';
  public arrayFeedback: any[] = [];
  public userLogged: boolean;
  public btnState = 'initial';
  public isBrowser;
  public commentsSliderConfig;

  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private http: HttpClient,
    private getDataService: GetDataService,
    public sanitizer: DomSanitizer,
    public dialog: MatDialog,
    public snackBar: MatSnackBar,
    private title: Title,
    private meta: Meta,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.subscription = activateRoute.params.subscribe(params => {
      this.id = params['id'];
      this.getData();
    });
    AppDataService.userStatusChange$.subscribe(() => {
      this.userLogged = AppDataService.userLoggedIn;
    });
   }

  ngOnInit() {
    this.preferences = [];
    this.stagesTabs = [];
    this.formattedStages = [];
    this.arrayFeedback = [];
    this.userLogged = AppDataService.userLoggedIn;
    this.btnState = 'initial';
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  getData() {
    if (this.id) {
      this.getDataService.getProgramFeedback(this.id).subscribe((data) => {
        if (data.count && data.count > 0) {
          this.arrayFeedback = data.results;
          this.arrayFeedback.forEach(item => {
            item.prod_feedback_images = item.kit_feedback_images;
          });
          this.commentsSliderConfig = {
            type: 'comments',
            slides: this.arrayFeedback,
            effect: 'slide',
            autoplay: false,
            slidesBreakpoints: {
              2048: {
                slidesPerView: 4
              },
              1920: {
                slidesPerView: 3
              },
              800: {
                slidesPerView: 1
              }
            }
            // slidesBreakpoints: {
            //   1024: {
            //     slidesPerView: 3
            //   },
            // },
          }
        }
        // console.log(this.arrayFeedback);
      });
      this.getDataService.getProgramData(this.id).subscribe((data) => {
        // console.log(data);
        this.programData = data;
        this.title.setTitle('Программа по уходу ' + this.programData.name.toUpperCase() + ' | DARI');
        this.meta.updateTag({ name: 'description', content: this.programData.description });
        this.preferences = this.programData.preferences;
        this.preferences.sort((i1, i2) => (i1.seq_no - i2.seq_no));
        this.products = this.programData.products;
        let stages = this.programData.stages;
        if (stages.length) {
          for (let stage of stages) {
            if (this.stagesTabs.find(item => item == stage.interval)) {} else {
              this.stagesTabs.push(stage.interval);
            }
            this.formattedStages[stage.interval] = {
              'Утро': [],
              'День': [],
              'Вечер': [],
              selected: false
            };
          }
          this.stagesTabs.sort((a, b) => {
            a = a.replace('-', '').replace('день', '');
            b = b.replace('-', '').replace('день', '');
            return Number(a) - Number(b);
          });
          this.activeTab = this.stagesTabs[0];
          for (let stage of stages) {
            this.formattedStages[stage.interval][stage.period].push({
              seq_no: stage.seq_no,
              description: stage.description,
              link_text: stage.link_text,
              product_link: stage.product_link
            });
          }
        }
        // console.log(this.formattedStages);
      });
    }
  }

  getBkgImg() {
    if (this.programData) {
      return this.sanitizer.bypassSecurityTrustStyle('url(' + this.programData.primary_image + ')');
    } else {
      return '';
    }
  }

  changeTab(tab) {
    if (tab) {
      this.activeTab = tab;
    }
  }

  getProductsSum() {
    if (this.programData) {
      let programProducts: ProgramProduct[] = this.programData.products;
      let sum = 0;
      for (let prod of programProducts) {
        sum += prod.products_count * prod.price;
      }
      return sum;
    }
  }

  buyProgram() {
    if (this.id) {
      AppDataService.addToCart(this.programData, 1, false, true);
      this.snackBar.open('Товар добавлен в корзину', 'x', {
        duration: 3000
      });
    }
  }

  getProductData(link: string, field: string) {
    let product = this.products.find(i => i.product_id == link);
    if (product) {
      if (field == 'primary_image') {
        return this.getThumbImg(product);
      } else {
        return product[field];
      }
    } else {
      return '';
    }
  }

  openProduct(link: string) {
    // let productId = link.substr(link.indexOf('products') + 9);
    this.router.navigate(['catalog/product/' + link]);
  }

  sendAdvice() {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'kit',
        id: this.id,
        name: this.programData.name
      }
    });
  }

  openProgram(adv: any) {
    if (adv) {
      if (adv.advice_kit_link) {
        let link = adv.advice_kit_link.replace('https://dari-cosmetics.ru//api/shop/kits/', '');
        if (link) {
          this.router.navigate(['care-program/' + link]);
        }
      }
    }
  }

  isLastMiddle(i: number) {
    switch (i) {
      case 4:
      case 7:
      case 10:
      case 13:
      case 16: return true;
      default: return false;
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

  getFBText(txt: string) {
    return txt.substring(0, 150) + '...';
  }

  openComment(comment: any) {
    // let dialogRef =
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'comment',
        comment: comment
      }
    });
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  hideAllPopups() {
    for (let step of this.formattedStages[this.activeTab]['Утро']) {
      step.hover = false;
    }
    for (let step of this.formattedStages[this.activeTab]['Вечер']) {
      step.hover = false;
    }
  }

}
