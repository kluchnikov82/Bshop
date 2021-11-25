import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Router } from '@angular/router';
import { MatTabGroup, MatSnackBar, MatDialog } from '@angular/material';
import { trigger, state, style, transition, animate, keyframes } from '@angular/animations';
import { registerLocaleData } from '@angular/common';
import ru from '@angular/common/locales/ru';
import { AppDataService } from '../../shared/services/app-data.service';
import { GetDataService } from '../../shared/services/get-data.service';
import { Person } from '../../shared/entities/person';
import { PopupAddressComponent } from '../../shared/popup/popup-address/popup-address.component';
import { PopupadviceComponent } from '../../shared/popup/popupadvice/popupadvice.component';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.scss'],
  animations: [
    trigger('animateToggle', [
      transition('void => *', [
        style({opacity: 0}),
        animate('0.3s', style({opacity: 1}))
      ]),
      transition('* => void', [
        animate('0.2s', style({opacity: 0}))
      ])
    ])
  ]
})
export class AccountComponent implements OnInit {

  @ViewChild('matTabs') public mat: MatTabGroup;
  @ViewChild('blockEarn') public blockEarn: ElementRef;
  @ViewChild('blockProfile') public blockProfile: ElementRef;

  public user: Person = new Person();
  public cartPrice: any;
  public products: any;
  public orders: any;
  public ordersArray: any[] = [];
  public countOrders = 0;
  public refOrders: any[] = [];
  public referalList: any[] = [];
  public fullName: string;
  public discount: number;
  public productsData: any[];
  public isPartner = false;
  public isManager = false;
  public activeTab: string;
  public orderProducts: any[];
  public editPasMode = false;
  public editMode = false;
  public birthdate: Date;
  public newPass: string;
  public newPass2: string;
  public refDiscount: number;
  public textArea: HTMLTextAreaElement;
  public percentDone: string;
  public percentRemain: string;
  public emailNotice: boolean;
  public smsNotice: boolean;
  public files: any;
  public showChangeProfileBlock: boolean;
  public showReflink: boolean;
  public lastOrderDate: Date;
  public bClist: any[];
  public ordersSum: number;
  public selectedPeriod: any;
  public periodList: any[] = [];
  public pages: any[];
  public curPage: number;
  public pagesRef: any[];
  public pagesReflist: any[];
  public curPageRef: number;
  public curPageReflist: number;
  public countPages: number;
  public countPagesRef: number;
  public countPagesReflist: number;
  public orderSum: number;

  constructor(
    private router: Router,
    private getDataService: GetDataService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) { }

  formatPhone(phone: string) {
    if (phone.includes('+7')) {
      return phone;
    }
    if (phone[0] === '7') {
      phone = phone.substring(1, 11);
    } else {
      phone = phone.substring(0, 10);
    }
    phone = phone.replace(/^(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/, '($1)$2-$3-$4');
    return '+7' + phone;
  }

  getMonthName(monthNum: number) {
    switch (monthNum) {
      case 0: return 'январь';
      case 1: return 'февраль';
      case 2: return 'март';
      case 3: return 'апрель';
      case 4: return 'май';
      case 5: return 'июнь';
      case 6: return 'июль';
      case 7: return 'август';
      case 8: return 'сентябрь';
      case 9: return 'октябрь';
      case 10: return 'ноябрь';
      case 11: return 'декабрь';
    }
  }

  setPeriods(cb: any = false) {
    const today = new Date();
    this.periodList = [];
    this.periodList.push({
      value: today.getMonth(),
      visibleValue: this.getMonthName(today.getMonth())
    })
    for (let k = 1; k < 6; k++) {
      let curDate = new Date(today.getFullYear(), today.getMonth() - k, 1);
      this.periodList.unshift({
        value: curDate.getMonth(),
        visibleValue: this.getMonthName(curDate.getMonth())
      })
    }
    // for (let i = firstDate.getMonth(); i <= today.getMonth(); i++) {
    //   this.periodList.push({
    //     value: i,
    //     visibleValue: this.getMonthName(i)
    //   });
    // }

    if (!!cb) {
      cb();
    }
  }

  ngOnInit() {
    this.orderSum = 0;
    registerLocaleData( ru );
    this.setPeriods(() => {
      this.selectedPeriod = this.periodList[this.periodList.length - 1];
      this.getDataService.getUserOrders(AppDataService.userToken, 100, 0).subscribe((data) => {
        if (data) {
          if (data.count) {
            let orders = data.results;
            for (let ord of orders) {
              if (ord.payed) {
                let orderDate = new Date(ord.payed);
                if (this.selectedPeriod) {
                  if (orderDate.getMonth() == this.selectedPeriod.value) {
                    this.orderSum += ord.total_amount;
                  }
                }
              }
            }
          }
        }
      });
    });

    this.orderProducts = [];
    this.discount = 0;
    this.refDiscount = 5;
    this.activeTab = 'personal';
    this.birthdate = null;
    this.showChangeProfileBlock = false;
    this.showReflink = false;
    this.curPage = 0;
    this.curPageRef = 0;
    this.pages = [];
    this.pagesRef = [];
    this.pagesReflist = [];
    this.curPageReflist = 0;
    this.countPages = 0;
    this.countPagesRef = 0;
    this.countPagesReflist = 0;
    this.bClist = [{
      text: 'Главная',
      link: '/'
    },
    {
      text: 'Личный кабинет',
      link: null
    }];
    if (AppDataService.user) {
      this.user = AppDataService.user;
      this.getData();
    } else {
      let localToken = localStorage.getItem('bshop_t');
      let localUserId = localStorage.getItem('bshop_id');
      if (localUserId && localToken) {
        AppDataService.userToken = localToken;
        this.getDataService.getUserInfo(localToken, localUserId).subscribe((data) => {
          AppDataService.user = data;
          this.user = data;
          AppDataService.userLoggedIn = true;
          AppDataService.userStatusChange$.emit();
          this.getData();
        });
      } else {
        this.user.last_name = '';
        this.user.first_name = '';
        this.user.id = '';
        this.user.ref_link = '';
        this.user.patronymic = '';
        this.router.navigate(['/']);
      }
    }
  }

  getReferals(limit) {
    this.referalList = [];
    this.getDataService.getReferals(limit, this.curPageReflist * 10).subscribe((res) => {
      if (res && res.count) {
        this.referalList = res.results;
        if (res.count > 10) {
          this.countPagesReflist = Math.ceil(res.count / 10);
          for (let i = 1; i <= this.countPagesReflist; i++) {
            this.pagesReflist.push(i);
          }
        }
      }
    });
  }

  getRefName(order) {
    if (order.referral) {
      let refName = order.referral;
      return refName.last_name + ' ' + refName.first_name;
    }
  }

  getUserOrders(limit: number = 10) {
    this.pages = [];
    this.getDataService.getUserOrders(AppDataService.userToken, limit, this.curPage * 10).subscribe((data) => {
      // console.log(data);
      this.ordersArray = data.results;
      this.countOrders = data.count;
      for (let ord of this.ordersArray) {
        if (ord.payed) {
          if ((new Date(ord.payed) > this.lastOrderDate) || !this.lastOrderDate) {
            this.lastOrderDate = new Date(ord.payed);
          }
        }
      }
      if (data.count > 10) {
        this.countPages = Math.ceil(data.count / 10);
        for (let i = 1; i <= this.countPages; i++) {
          this.pages.push(i);
        }
      }
      this.showReflink = (this.user.total_amount > 2000);
      if (this.user.is_old) {
        this.showReflink = true;
      }
    });
  }

  getRefOrders(limit: number = 10) {
    this.pagesRef = [];
    this.getDataService.getRefOrders(limit, this.curPageRef * 10).subscribe((data) => {
      if (data && data.count) {
        for (let refOrder of data.results) {
          if (refOrder.payed) {
            if (refOrder.referral) {
              if (refOrder.referral.id !== this.user.id) {
                this.refOrders.push(refOrder);
              }
            } else {
              this.refOrders.push(refOrder);
            }
            if ((new Date(refOrder.payed) > this.lastOrderDate) || !this.lastOrderDate) {
              this.lastOrderDate = new Date(refOrder.payed);
            }
          }
        }
        if (data.count > 10) {
          this.countPagesRef = Math.ceil(data.count / 10);
          for (let i = 1; i <= this.countPagesRef; i++) {
            this.pagesRef.push(i);
          }
        }
      }
    })
  }

  getData() {
    this.orders = 0;
    if (this.user) {
      if (this.user.partner_type == 'Партнер 1 уровня (розница)') {
        this.refDiscount = 5;
      } else {
        this.refDiscount = this.user.current_discount * 100;
      }
      if (this.user.phys_profile) {
        if (this.user.phys_profile.birth_date) {
          this.birthdate = this.user.phys_profile.birth_date;
        }
      }
      if (this.user.phone) {
        this.user.phone = this.formatPhone(this.user.phone);
      }
      this.smsNotice = this.user.sms_notice;
      this.emailNotice = this.user.email_notice;
      // console.log(this.user);
      this.fullName = this.user.last_name + ' ' + this.user.first_name;
      let localCart = JSON.parse(localStorage.getItem('cart'));
      if (localCart) {
        this.products = localCart.length;
        this.cartPrice = localCart.reduce((sum, item) => sum + Number(item.price), 0);
      } else {
        this.products = 0;
        this.cartPrice = 0;
      }

      if (this.user.partner_type == 'Партнер 1 уровня (розница)') {
        this.isPartner = false;
        this.isManager = false;
      } else if (this.user.partner_type == 'Менеджер') {
        this.isPartner = false;
        this.isManager = true;
      } else {
        this.isManager = false;
        this.isPartner = true;
        this.percentRemain = ((0.5 - this.user.current_discount) / 0.5) * 100 + '%';
        this.percentDone = (this.user.current_discount / 0.5) * 100 + '%';
      }

      this.getUserOrders();
      this.getRefOrders();
      this.getReferals(10);

      if (this.user.partner_type == 'Партнер 1 уровня (розница)') {
        this.discount = 5;
      }

      if (AppDataService.openEarningsBlock) {
        this.changeTab('myEarns');
      }

    } else {
      this.router.navigate(['']);
    }
  }

  getEnding(count) {
    let ending = AppDataService.endingWord(count);
    return ending;
  }

  getUserData(type) {
    if (this.user) {
      switch (type) {
        case 'name': return this.user.first_name + ' ' + this.user.last_name;
        case 'reflink': return this.user.ref_link;
        case 'email': return this.user.email;
        case 'avatar': return (this.user.avatar) ? this.user.avatar : '/assets/no-photo.jpg';
      }

    } else {
      if (type == 'avatar') {
        return '/assets/no-photo.jpg'
      } else {
        return '';
      }
    }
  }

  openOrder(id: string) {
    if (id) {
      this.router.navigate(['order/' + id]);
    }
  }

  sort(arrayOrders: any[], field: string, arrow: string) {
    if (arrayOrders.length) {
      arrayOrders.sort((i1, i2) => i1[field] - i2[field]);
    }
  }

  selectFirstTab() {
    this.mat.selectedIndex = 0;
  }

  openPage(page: string) {
    this.router.navigate([page]);
  }

  logout() {
    AppDataService.userLogout$.emit();
    this.openPage('');
  }

  getProdImage(prodId) {
    if (this.productsData.length) {
      let findProd = this.productsData.find(item => item.id == prodId);
      if (findProd) {
        return findProd.primary_image;
      }
    }
  }

  showClipboardTooltip(event) {
    if (event) {
      this.snackBar.open('Код скопирован в буфер обмена!', 'x', {
        duration: 3000
      })
    }
  }

  changeTab(tab: string) {
    if (this.activeTab == tab) {
      if (screen.width < 975) {
        this.activeTab = '';
      }
    } else {
      this.activeTab = tab;
    }
  }

  orderTrack(index, elem) {
    return elem.id;
  }

  showOrderDetails(order) {
    if (order) {
      order.showDetails = !order.showDetails;
    }
  }

  repeatOrder(order) {
    if (order) {
      let products = order.order_products;
      let kits = order.order_kits;
      if (products.length) {
        for (let prod of products) {
          AppDataService.addToCart(prod, prod.quantity, true);
        }
      }
      if (kits.length) {
        for (let kit of kits) {
          AppDataService.addToCart(kit, kit.quantity, true, true);
        }
      }
      if (products.length || kits.length) {
        this.router.navigate(['cart']);
      }
    }
  }

  userAddress(adr: any) {
    if (adr) {
      let address = adr.postcode + ((adr.city) ? ', ' + adr.city : '') +
                    ((adr.settlement) ? ', ' + adr.settlement : '') +
                    ((adr.street) ? ', ' + adr.street : '') +
                    ((adr.house) ? ', ' + adr.house : '');
      return address;
    } else {
      return '';
    }
  }

  changeProfile() {
    if (!this.editMode) {
      this.editMode = true;
    } else {
      if (!this.fullName || !this.user.email || !this.user.phone) {
        this.snackBar.open('Все поля обязательны для заполнения!', 'x', {
          duration: 3000
        });
        this.showChangeProfileBlock = true;
        return;
      }
      let nameArray = this.fullName.split(' ');
      if (nameArray.length < 2) {
        this.snackBar.open('Неккоректные ФИО', 'x', {
          duration: 3000
        });
        return;
      } else {
        this.user.last_name = nameArray[0];
        this.user.first_name = nameArray[1];
        this.user.patronymic = nameArray[2];
      }
      if (!this.user.phys_profile) {
        this.user.phys_profile = {};
      }
      this.user.jur_profile = {};
      if (this.birthdate) {
        if (typeof this.birthdate == 'string') {
          this.user.phys_profile.birth_date = this.birthdate;
        } else {
          let newBirthdate = new Date(this.birthdate.setDate(this.birthdate.getDate() + 1));
          this.user.phys_profile.birth_date = newBirthdate.toISOString().substr(0, 10);
        }
      } else {
        this.user.phys_profile.birth_date = null;
      }
      this.user.phone = this.user.phone.substr(0, 16);
      this.user.phys_profile.phone_number = this.user.phone;
      this.user.sms_notice = this.smsNotice;
      this.user.email_notice = this.emailNotice;
      this.getDataService.changeProfile(this.user).subscribe((res) => {
        // console.log(res);
        this.snackBar.open('Данные профиля успешно сохранены', 'x', {
          duration: 3000
        });
        this.editMode = false;
      }, (error) => {
        this.snackBar.open('Ошибка сохранения данных профиля!', 'x', {
          duration: 3000
        });
      })
    }
  }

  changeNotice(notice: boolean, type: string) {
    notice = !notice;
    if (type == 'sms') {
      this.smsNotice = notice;
    } else {
      this.emailNotice = notice;
    }
    this.editMode = true;
    this.changeProfile();
  }

  changePass() {
    if (!this.editPasMode) {
      this.editPasMode = true;
    } else {
      if (this.newPass !== this.newPass2) {
        this.snackBar.open('Пароли не совпадают!', 'x', {
          duration: 3000
        });
        return;
      } else {
        this.getDataService.changePassword(this.newPass).subscribe((res) => {
          this.snackBar.open(res.message, 'x', {
            duration: 3000
          });
        });
      }
    }
  }

  addAddress() {
    let dialogRef = this.dialog.open(PopupAddressComponent);
    dialogRef.afterClosed().subscribe((data) => {
      if (data) {
        this.user.addresses.push(data);
        this.editMode = true;
        this.changeProfile();
      }
    });
  }

  isiOS() {
    return navigator.userAgent.match(/ipad|iphone/i);
  }

  createTextArea(text: string) {
    this.textArea = document.createElement('textarea');
    this.textArea.value = text;
    document.body.appendChild(this.textArea);
  }

  selectText() {
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

  copyClipboard() {
    let txt = this.user.promo;
    this.createTextArea(txt);
    this.selectText();
    document.execCommand('copy');
    document.body.removeChild(this.textArea);
    this.snackBar.open('Код скопирован в буфер обмена', 'x', {
      duration: 2000
    });
  }

  bonusToBalance() {
    if (this.user.available_bonus_amount) {
      this.getDataService.bonusToBalance(this.user.available_bonus_amount).subscribe((data) => {
        if (data) {
          this.snackBar.open(data.message, 'x', {
            duration: 3000
          });
        }
      });
    } else {
      this.snackBar.open('Нет доступных бонусов', 'x', {
        duration: 3000
      });
    }
  }

  addDepo() {

  }

  getRefSum() {
    let sum = 0;
    if (this.refOrders.length) {
      for (let ord of this.refOrders) {
        if (ord.payed) {
          sum += (ord.total_amount * this.refDiscount) / 100;
        }
      }
    }
    return Math.floor(sum);
  }

  getPartnersBonusAmount() {
    if (this.user) {
      return (this.user.total_sale_amount * 0.1);
    }
  }

  getUserImg() {
    let src = '/assets/feedback.jpg';
    if (this.user) {
      if (this.user.avatar) {
        src = this.user.avatar;
      }
    }
    return src;
  }

  addImg(event) {
    let target = event.target || event.srcElement;
    this.files = target.files;
    if (this.files.length) {
      if (this.files[0].size > 2096576) {
        this.snackBar.open('Ошибка загрузки изображения. Превышен допустимый размер файла (2 Мб)', 'x', {
          duration: 3000
        });
      } else {
        let formData = new FormData();
        formData.append('file', this.files[0]);
        this.getDataService.changeAvatar(this.files[0].name, formData).subscribe(() => {
          this.getDataService.getUserInfo(AppDataService.userToken, this.user.id).subscribe((data) => {
            AppDataService.user = data;
            this.user = data;
          })
          this.snackBar.open('Аватар успешно изменен', 'x', {
            duration: 3000
          });
        });
      }
    }
  }

  showPartnersInfo() {
    this.blockEarn.nativeElement.scrollIntoView({behavior: 'smooth'});
  }

  showProfile() {
    this.showChangeProfileBlock = !this.showChangeProfileBlock;
    if (this.showChangeProfileBlock) {
      if (this.blockProfile) {
        this.blockProfile.nativeElement.scrollIntoView({behavior: 'smooth'});
      }
    }
  }

  getManagerSum() {
    return this.orderSum;
  }

  changeManagerSum() {
    this.orderSum = 0;
    this.getDataService.getUserOrders(AppDataService.userToken, 100, 0).subscribe((data) => {
      if (data) {
        if (data.count) {
          let orders = data.results;
          for (let ord of orders) {
            if (ord.payed) {
              let orderDate = new Date(ord.payed);
              if (orderDate.getMonth() == this.selectedPeriod.value) {
                this.orderSum += ord.total_amount;
              }
            }
          }
        }
      }
    });
  }

  changePage(pageNum) {
    if (pageNum >= 0 && pageNum <= this.countPages) {
      this.curPage = pageNum;
    } else if (pageNum > this.countPages) {
      this.curPage = 0;
    } else {
      this.curPage = this.countPages;
    }
    this.getUserOrders();
  }

  changePageRef(pageNum) {
    if (pageNum >= 0 && pageNum <= this.countPagesRef) {
      this.curPageRef = pageNum;
    } else if (pageNum > this.countPagesRef) {
      this.curPageRef = 0;
    } else {
      this.curPageRef = this.countPagesRef;
    }
    this.getRefOrders();
  }

  changePageReflist(pageNum) {
    if (pageNum >= 0 && pageNum <= this.countPagesReflist) {
      this.curPageReflist = pageNum;
    } else if (pageNum > this.countPagesReflist) {
      this.curPageReflist = 0;
    } else {
      this.curPageReflist = this.countPagesReflist;
    }
  }

  getRefFullname(referal) {
    if (referal) {
      return (referal.last_name + ' ' + referal.first_name + ((referal.middle_name) ? ' ' + referal.middle_name : ''));
    } else {
      return '';
    }
  }

  addDays(date: Date, days: number) {
    if (date && days) {
      const d: Date = new Date();
      d.setDate(date.getDate() + 14);
      return d;
    } else {
      return null;
    }
  }

  showBonusHistory() {
    this.getDataService.getBonusHistory().subscribe((res: any) => {
      if (res && res.count) {
        this.dialog.open(PopupadviceComponent, {
          data: {
            type: 'history',
            history: res.results
          }
        });
      }
    });
  }

  editOrder(order) {
    if (order && order.id) {
      this.router.navigate(['order/edit/' + order.id]);
    }
  }

}
