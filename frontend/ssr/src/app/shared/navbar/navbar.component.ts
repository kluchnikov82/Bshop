import { Component, OnInit, ViewChild, ElementRef, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { MatDialog, MatMenuTrigger, MatSnackBar } from '@angular/material';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { PopupLoginComponent } from '../popup/popup-login/popup-login.component';
import { PopupSignupComponent } from '../popup/popup-signup/popup-signup.component';
import { PopupadviceComponent } from '../popup/popupadvice/popupadvice.component';
import { AppDataService } from '../../services/app-data.service';
import { GetDataService } from '../../services/get-data.service';
import { CatalogService } from '../../routed/catalog/catalog.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
  animations: [
    trigger('expandPanel', [
      state('initial', style({height: 0, opacity: 0, zIndex: -20})),
      state('expanded', style({height: '*', opacity: 1})),
      transition('* => *', animate('0.2s'))
    ]),
    trigger('expandMenu', [
      transition('void => *', [
        style({opacity: 0}),
        animate('0.2s', style({opacity: 1})),
      ]),
      transition('* => void', [
        animate('0.2s', style({opacity: 0}))
      ])
    ])
  ]
})
export class NavbarComponent implements OnInit {

  @ViewChild(MatMenuTrigger) trigger: MatMenuTrigger;
  @ViewChild('menuBtn') menuBtn: ElementRef;

  public cartCount = 0;
  public user: any;
  public loggedIn: boolean;
  public searchProduct: string;
  public username = '';
  public password = '';
  public showLoginPanel = false;
  public menuList: any[] = [];
  public showMenuPanel = false;
  public showCartPreview = false;
  public showProfileMenu = false;
  public catalogState: string;
  public menuState = false;
  public subcatState: string;
  public sharePanelState: string;
  public textArea: HTMLTextAreaElement;
  public activeSearch = false;
  public isManager = false;

  constructor(
    private getDataService: GetDataService,
    private catalogService: CatalogService,
    private router: Router,
    public dialog: MatDialog,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
      AppDataService.cartChange$.subscribe(() => {
        this.getCartCount();
      });
   }

  sortMenu() {
    let sortArray = ['Антиакне', 'Лицо', 'Глаза и губы', 'Тело', 'Волосы'];
    let newMenuList = [];
    if (this.menuList.length) {
      for (let sortCat of sortArray) {
        let cat = this.menuList.find(item => item.name == sortCat);
        if (cat) {
          newMenuList.push(cat);
        }
      }
    }
    if (newMenuList.length) {
      this.menuList = newMenuList;
    }
  }

  ngOnInit() {
    this.catalogState = 'initial';
    this.menuState = false;
    this.subcatState = 'initial';
    this.sharePanelState = 'initial';
    this.activeSearch = false;
    this.isManager = true;

    this.catalogService.catalog$.subscribe((res) => {
      this.menuList = res;
    });

    AppDataService.userLogout$.subscribe(() => {
      AppDataService.user = {
        addresses: [],
        avatar: '',
        balance: '',
        available_bonus_amount: 0,
        bonus_balance: '',
        current_discount: '',
        current_period_bonus_payments: '',
        current_period_payments: '',
        current_period_sale_amount: '',
        email: '',
        email_notice: false,
        first_name: '',
        id: '',
        is_jur: false,
        is_partner: false,
        jur_profile: '',
        last_name: '',
        last_period_bonus_payments: '',
        last_period_payments: '',
        last_period_sale_amount: '',
        partner_type: '',
        patronymic: '',
        phys_profile: '',
        ref_id: 0,
        promo: '',
        ref_link: '',
        sms_notice: false,
        total_amount: '',
        total_bonus_payments: '',
        total_payments: '',
        total_sale_amount: '',
        user_type: '',
        username: '',
        phone: '',
        current_target: 0,
        next_target: 0
      };
      this.loggedIn = false;
      AppDataService.userLoggedIn = false;
      AppDataService.userStatusChange$.emit();
      if (isPlatformBrowser(this.platformId)) {
        localStorage.removeItem('bshop_id');
        localStorage.removeItem('bshop_t');
      }
    });

    this.showProfileMenu = false;
    this.menuList = this.catalogService.catalog;
    if (isPlatformBrowser(this.platformId)) {
      let localToken = localStorage.getItem('bshop_t');
      let localUserId = localStorage.getItem('bshop_id');
      if (localToken && localUserId) {
        AppDataService.userToken = localToken;
        this.getDataService.getUserInfo(localToken, localUserId).subscribe((data) => {
          if (data) {
            AppDataService.user = data;
            this.user = data;
            AppDataService.userLoggedIn = true;
            AppDataService.userStatusChange$.emit();
            AppDataService.userDataChange$.emit(data);
          }
        }, (error) => {
          AppDataService.userLogout$.emit();
        });
      }
    }

    AppDataService.userStatusChange$.subscribe(() => {
      this.loggedIn = AppDataService.userLoggedIn;
      if (this.loggedIn) {
        this.user = AppDataService.user;
        if (this.user.partner_type == 'Менеджер') {
          this.isManager = true;
        } else {
          this.isManager = false;
        }
      }
    });

    this.getCartCount();
    // this.getDataService.getCatalog().subscribe((data) => {
    //   AppDataService.menuList = data;
    //   this.menuList = data;
    //   this.sortMenu();
    //   for (let cat of this.menuList) {
    //     cat.state = 'initial';
    //   }
    //   // console.log(data);
    //   AppDataService.menuListChange$.emit();
    // });
  }

  showMenu() {
  }

  closeMenu() {
  }

  getCartCount() {
    if (isPlatformBrowser(this.platformId)) {
      let localCart = JSON.parse(localStorage.getItem('cart'));
      if (localCart) {
        this.cartCount = localCart.length;
      } else {
        this.cartCount = 0;
      }
    }
  }

  openPage(page) {
    // this.pageContentService.call_page(page);
    this.menuState = false;
    this.showMenuPanel = false;
    this.showCartPreview = false;
    this.showProfileMenu = false;
    if (page == 'cart') {
      if (!this.cartCount) {
        return;
      }
    }
    this.router.navigate([page]);
  }

  openCatalog(categoryName: any, subcat: any) {
    this.menuState = false;
    this.showMenuPanel = false;
    AppDataService.currentCategory = categoryName;
    AppDataService.currentSubcat = subcat;
    // AppDataService.currentCategoryChange$.emit({subcat: subcat, category: categoryName});
    this.router.navigate(['catalog/' + categoryName + '/' + subcat]);
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

  account() {
    this.menuState = false;
    if (this.loggedIn) {
      this.openPage('account');
    } else {
      let dialogRef = this.dialog.open(PopupLoginComponent);
      dialogRef.afterClosed().subscribe((res) => {
        if (res) {
          if (res == 'signup') {
            this.dialog.open(PopupSignupComponent);
          }
          if (res == 'forgot') {
            this.dialog.open(PopupadviceComponent, {
              data: {
                type: 'forgot'
              }
            });
          }
        }
      });
    }
  }

  hideLoginPanel() {
    this.showLoginPanel = false;
  }

  signUp() {
    this.showLoginPanel = false;
    this.openPage('signup');
  }

  login() {
    if (this.username && this.password) {
      this.getDataService.loginUser(this.username, this.password).subscribe((data) => {
        // console.log(data);
        if (data.token && data.user) {
          AppDataService.user = data.user;
          AppDataService.userToken = 'JWT ' + data.token;
          this.showLoginPanel = false;
          AppDataService.userLoggedIn = true;
          if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('bshop_id');
            localStorage.removeItem('bshop_t');
            localStorage.setItem('bshop_id', data.user.id);
            localStorage.setItem('bshop_t', AppDataService.userToken);
          }
          AppDataService.userStatusChange$.emit();
          this.openPage('account');
        }
      });
    }
  }

  logout() {
    AppDataService.userLogout$.emit();
    this.openPage('');
  }

  toggleMenu(st: string) {
    if (st == 'initial') {
      st = 'expanded;';
    } else {
      st = 'initial';
    }
    return st;
  }

  toggleSubMenu(category) {
    for (let cat of this.menuList) {
      if (cat.id != category.id) {
        cat.state = 'initial';
      }
    }
    let curCat = this.menuList.find(item => item.id == category.id);
    if (curCat) {
      return (category.state == 'initial') ? 'expanded' : 'initial';
    }
    return curCat.state;
  }

  trackCategory(index, category) {
    return category.id;
  }

  share(social: string) {
    let link = '';
    switch (social) {
      case 'inst': link = 'https://instagram.com/daricosmetics'; break;
      case 'fb': link = 'https://www.facebook.com/sharer/sharer.php?u=https://dari-cosmetics.ru'; break;
      case 'vk': link = 'https://vk.com/share.php?url=https://dari-cosmetics.ru'; break;
      case 'ok': link = 'https://connect.ok.ru/offer?url=https://dari-cosmetics.ru'; break;
      case 'twitter': link = 'http://twitter.com/share?&url=https://dari-cosmetics.ru'; break;
    }
    if (isPlatformBrowser(this.platformId)) {
      window.open(link, '_blank');
    }
  }

  isiOS() {
    let res;
    if (isPlatformBrowser(this.platformId)) {
      res = navigator.userAgent.match(/ipad|iphone/i);
    }
    return res;
  }

  createTextArea(text: string) {
    if (isPlatformBrowser(this.platformId)) {
      this.textArea = document.createElement('textarea');
      this.textArea.value = text;
      document.body.appendChild(this.textArea);
    }
  }

  selectText() {
    if (isPlatformBrowser(this.platformId)) {
      let range: Range, selection: Selection;
      if (this.isiOS()) {
        range = document.createRange();
        range.selectNodeContents(this.textArea);
        selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        this.textArea.setSelectionRange(0, 99999);
      } else {
        this.textArea.select();
      }
    }
  }

  copyClipboard() {
    if (isPlatformBrowser(this.platformId)) {
      let txt = 'https://dari-cosmetics.ru';
      this.createTextArea(txt);
      this.selectText();
      document.execCommand('copy');
      document.body.removeChild(this.textArea);
      this.snackBar.open('Ссылка скопирована в буфер обмена', 'x', {
        duration: 2000
      });
    }
  }

  search() {
    if (this.searchProduct) {
      AppDataService.searchProduct = this.searchProduct;
      AppDataService.searchProductStart$.emit(this.searchProduct.toLowerCase());
      // if (!this.router.url.includes('catalog')) {
        this.openPage('catalog/search/' + this.searchProduct);
      // }
    }
  }

  mobileSearch() {
    if (this.activeSearch && this.searchProduct) {
      this.search();
    } else if (this.activeSearch) {
      this.activeSearch = false;
    } else {
      this.activeSearch = true;
    }
  }

  openEarning() {
    AppDataService.openEarningsBlock = true;
    this.account();
  }

}
