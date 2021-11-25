import { Component, OnInit, ViewChild, Inject, PLATFORM_ID } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatSnackBar, MatDialog } from '@angular/material';
import { Subscription } from 'rxjs';
import { GetDataService } from './../services/get-data.service';
import { AppDataService } from './../services/app-data.service';
import { CatalogService } from '../catalog/catalog.service';
import { DomSanitizer } from '@angular/platform-browser';
import { PerfectScrollbarComponent } from 'ngx-perfect-scrollbar';
import { PopupadviceComponent } from '../popup/popupadvice/popupadvice.component';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-main-page',
  templateUrl: './main-page.component.html',
  styleUrls: ['./main-page.component.scss']
})
export class MainPageComponent implements OnInit {

  @ViewChild('sliderFeedback') sliderRef?: PerfectScrollbarComponent;
  @ViewChild('sliderPrograms') sliderProgramRef?: PerfectScrollbarComponent;
  private subsrciption: Subscription;
  public id: string;
  public arraySlides: any[] = []; // = slides;
  public activeSlide: any;
  public activeIndex: Number;
  public index = 0;
  public categories: any[] = [];
  public comments: any[] = [];
  public url = '';
  public loaded = false;
  public agree = true;
  public indicators: any[] = [];
  public username: string;
  public userphone: string;
  public typesFeedback: any[];
  public isBrowser: boolean;

  constructor(
    private getDataService: GetDataService,
    private catalogService: CatalogService,
    private activateRoute: ActivatedRoute,
    private router: Router,
    public sanitizer: DomSanitizer,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.arraySlides = AppDataService.slides;
    for (let i = 0; i < this.arraySlides.length; i++) {
      this.indicators.push(i);
    }
    this.subsrciption = activateRoute.params.subscribe((params) => {
      this.id = params['id'];
      if (this.id) {
        if (!isNaN(Number(this.id))) {
          getDataService.setReferal(this.id).subscribe((data) => {
            // console.log(data)
          });
        }
      }
    });
  }

  ngOnInit() {
    this.activeIndex = 0;
    // this.activeSlide = {id: ''};
    this.arraySlides = AppDataService.slides; // (AppDataService.slides)? AppDataService.slides : slides;

    this.catalogService.catalog$.subscribe((res) => {
      this.categories = res;
    });

    this.isBrowser = isPlatformBrowser(this.platformId);

    this.loaded = true;
    // this.arraySlides = [];// slides;
    // this.activeSlide = {
    //   id: ''
    // }

    AppDataService.slidesLoaded$.subscribe(() => {
      this.indicators = [];
      this.arraySlides = AppDataService.slides;
      // for (let i = 0; i < this.arraySlides.length; i++) {
      //   this.indicators.push(i);
      // }
    });

    // AppDataService.menuListChange$.subscribe(() => {
    //   this.categories = AppDataService.menuList;
    //   this.loaded = true;
    // });

    // if (this.arraySlides.length) {
    //   this.activeSlide = this.arraySlides[0];
    // }

    // if (isPlatformBrowser(this.platformId)) {
    //   setInterval(() => {this.changeSlide(); }, 3500);
    // }

    this.getDataService.getProdFeedback().subscribe((data) => {
      // console.log(data);
      this.comments = data;
    });

    this.getDataService.getAdviceTypes().subscribe((data) => {
      this.typesFeedback = data;
    });
    this.loaded = true;
  }

  // getSlideImg(slide) {
  //   if (isPlatformBrowser(this.platformId)) {
  //     if (screen.width < 600) {
  //       return this.sanitizer.bypassSecurityTrustStyle('url("https://dari-cosmetics.ru/assets/123.jpg")');
  //     } else if (slide.image) {
  //       return this.sanitizer.bypassSecurityTrustStyle('url("' + slide.image + '")');
  //     } else {
  //       return '';
  //     }
  //   } else {
  //     if (slide.image) {
  //       return this.sanitizer.bypassSecurityTrustStyle('url("' + slide.image + '")');
  //     } else {
  //       return '';
  //     }
  //   }
  // }

  // changeSlide() {
  //   let index = this.index;
  //   if (this.arraySlides.length) {
  //     if (index >= (this.arraySlides.length - 1)) {
  //       index = 0;
  //     } else {
  //       index++;
  //     }
  //   } else {
  //     index = 0;
  //   }

  //   this.index = index;
  //   // this.activeSlide = this.arraySlides[index];
  // }

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

  getCategoryImg(category) {
    if (category) {
      if (category.image) {
        return (category.image);
      } else {
        return ('https://dari-cosmetics.ru/assets/no-photo.jpg');
      }
    } else {
      return ('https://dari-cosmetics.ru/assets/no-photo.jpg');
    }
  }

  getCategoryBkg(category) {
    let categoryStyle = '';
    if (category.image) {
      categoryStyle = 'url("' + category.image + '")';
    } else {
      categoryStyle = 'url("https://dari-cosmetics.ru/assets/no-photo.jpg")';
    }
    if (isPlatformBrowser(this.platformId)) {
      if (screen.width < 640) {
        if (category.name == 'Тело') {
          categoryStyle = 'url("https://dari-cosmetics.ru/assets/body-rotate.jpg")';
        }
      }
    }
    return this.sanitizer.bypassSecurityTrustStyle(categoryStyle);

  }

  openCatalog(categoryName: any) {
    AppDataService.currentCategory = categoryName;
    this.router.navigate(['catalog']);
  }

  moveSlider(arrow) {
    // this.scroll
    if (isPlatformBrowser(this.platformId)) {
      if (arrow == 'left') {
        this.sliderRef.directiveRef.scrollTo(0, 0, 500);
      } else {
        this.sliderRef.directiveRef.scrollTo(1100, 0, 500);
      }
    }
  }

  openVideo(link: string) {
    if (link) {
      if (isPlatformBrowser(this.platformId)) {
        window.open(link, '_blank');
      }
    }
  }

  openPage(page: string) {
    if (page) {
      this.router.navigate([page]);
    }
  }

  openLink(link) {
    if (link) {
      if (isPlatformBrowser(this.platformId)) {
        window.open(link, '_self');
      }
    }
  }

  openInst() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://instagram.com/daricosmetics', '_blank');
    }
  }

  openVK() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://vk.com/daricosmetics', '_blank');
    }
  }

  openFB() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://www.facebook.com/Daricosmetics-103691007751764/', '_blank');
    }
  }

  sendMessage() {
    let type = this.typesFeedback.find(i => i.type_name == 'Консультация').id;
    if (this.username && this.userphone && type) {
      this.getDataService.sendFeedback(this.username, this.userphone, 0, 'Запрос консультации (' + new Date() + ')', 'info@dari-cosmetics.ru', type).subscribe((res) => {
        if (res) {
          this.username = '';
          this.userphone = '';
          this.snackBar.open('Заявка на консультацию отправлена', 'x', {
            duration: 3000
          });
        }
      });
    } else {
      this.snackBar.open('Все поля обязательны для заполнения', 'x', {
        duration: 3000
      });
    }
  }

  openPopupConsult() {
    let consultDialog = this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'consult'
      }
    });
    consultDialog.afterClosed().subscribe((res) => {
      if (res) {
        if (res.name && res.phone) {
          this.username = res.name;
          this.userphone = res.phone;
          this.sendMessage();
        }
      }
    });
  }

  openDoc() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://dari-cosmetics.ru/assets/docs/personal_data.pdf', '_blank');
    }
  }

  checkBlockComments() {
    let res = false;
    const commentsWide = this.comments.length * 555;
    if (isPlatformBrowser(this.platformId)) {
      if (screen.width > 767) {
        if (screen.width > commentsWide) {
          res = true;
        }
      }
    }
    return res;
  }

}
