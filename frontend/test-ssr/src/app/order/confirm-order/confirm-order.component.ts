import { Component, OnInit, OnDestroy, Inject, PLATFORM_ID } from '@angular/core';
import { MatDialog, MatSnackBar } from '@angular/material';
import { FormBuilder, FormControl, FormGroup, Validators, AbstractControl } from '@angular/forms';
import { Router } from '@angular/router';
import { registerLocaleData, isPlatformBrowser } from '@angular/common';
import ru from '@angular/common/locales/ru';
import { isNullOrUndefined } from 'util';
import { debounceTime, takeWhile } from 'rxjs/operators';
import { Person } from '../../entities/person';
import { Promocode } from './../../entities/product';
import { AppDataService } from '../../services/app-data.service';
import { GetDataService } from '../../services/get-data.service';
import { PopupLoginComponent } from '../../popup/popup-login/popup-login.component';
import { PopupSignupComponent } from '../../popup/popup-signup/popup-signup.component';
import { PopupadviceComponent } from '../../popup/popupadvice/popupadvice.component';

@Component({
  selector: 'app-confirm-order',
  templateUrl: './confirm-order.component.html',
  styleUrls: ['./confirm-order.component.scss']
})
export class ConfirmOrderComponent implements OnInit, OnDestroy {

  userDataForm = new FormGroup({
    fioControl: new FormControl('', [Validators.required, Validators.minLength(6), Validators.pattern(/[А-ЯЁA-Z][а-яёa-z]{0,}\s[А-ЯЁA-Z][а-яёa-z]{1,}/)]),
    phoneControl: new FormControl('', [Validators.required, Validators.minLength(16)]),
    emailControl: new FormControl('', [Validators.required, Validators.email]),
    memoControl: new FormControl(''),
  });

  deliveryForm = new FormGroup({
    regionControl: new FormControl(),
    cityControl: new FormControl('', [Validators.required]),
    streetControl: new FormControl(),
    houseControl: new FormControl('', [Validators.required]),
    flatControl: new FormControl()
  });

  kladrId: string;
  postcode: string;
  promocode: string;
  public products: any[] = [];
  public kits: any[] = [];
  private localCart: any[] = [];
  public cartEvents: any[];
  public orderWeight: number;
  public regionOptions: string[] = [];
  private oldRegion: any;
  public cityOptions: string[] = [];
  private oldCity: any;
  public streetOptions: string[] = [];
  private oldStreet: any;
  public houseOptions: string[] = [];
  private oldHouse: any;
  public hasErrors = false;
  public shippingMethods: any[] = [];
  public curShippingMethod: number;
  public minPriceDP: any;
  public DPdays: any;
  public minPriceCourier: any;
  public courierDays: any;
  public minPricePost: any;
  public postDays: any;
  public showDeliveryBlock: boolean;
  private location: any;
  public selectedCourier: any;
  public dpList: any[];
  public selectedDP: any;
  public deliveryCost: number;
  public firstStep: boolean;
  private selectedSuggestion: any;
  public showDPList = false;
  private unrestrictedAddress = '';
  public user: Person;
  public selectedAddress: any;
  public hasOwnAddress = false;
  public isPartner = false;
  public ownOrder = false;
  public agree: boolean;
  public orderHasGift: boolean;
  public giftText: string;
  private isActiveComponent: boolean;
  public loadShipping: boolean;
  public bClist: any[];
  public promoOrder: boolean;
  public promoDiscount = 0;
  public refPromoOrder: boolean;

  public loggedIn: boolean;
  public errorClass = {
    name: '',
    phone: '',
    email: ''
  };

  constructor(
    private getDataService: GetDataService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  autocompleteAddress(control: AbstractControl, query: any, oldValue: any, options: string[]) {
    this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31', query).subscribe((data) => {
      // console.log(data);
      if (data.suggestions) {
        if (data.suggestions.length) {
          data.suggestions.forEach(suggest => {
            options.push(suggest);
          });
        }
      }
    });
  }

  getShippingMethods(postcode: string = '') {
    let postal_code: string;
    this.loadShipping = true;
    let cartSum = this.getCartSum(true);
    if (postcode) {
      postal_code = postcode;
    } else {
      postal_code = this.postcode;
    }
    if (postal_code) {
      this.shippingMethods = [];
      let order_products = [];
      let shippingMethods = [];
      let order_kits = [];
      let order_events = this.localCart.filter(item => item.event_id);
      for (let product of this.localCart) {
        if (product.product_id) {
          if (product.isKit) {
            order_kits.push({
              kit_id: product.product_id,
              quantity: product.quantity,
              price: product.price
            });
          }
          order_products.push({
            product_id: product.product_id,
            quantity: product.quantity,
            price: product.price
          });
        }
      }

      if (order_products.length || order_kits.length || order_events.length) {
        let address = {
          postcode: postal_code,
          country: 643
        };

        let orderInfo = {
          order_products: order_products.length ? order_products : [],
          order_kits: order_kits.length ? order_kits : [],
          order_events: order_events.length ? order_events : [],
          address: address
        };

        this.getDataService.calcShipping(orderInfo).subscribe((data) => {
          if (data && !data.error) {
            let res: any[] = data;
            let results, errors;
            if (res.length) {
              errors = res.filter(item => item.message && item.message.includes('Ошибка'));
              results = res.filter(item => item.cost || (item.shipping_method_id == 7));
            }
            if (errors.length) {
              let msg = '';
              errors.forEach(err => {
                msg += err.message + '\r\n';
              });
              this.snackBar.open(msg, 'x', {
                duration: 5000
              });
            }
            if (results.length) {
              for (let res of results) {
                if (res.shipping_method_id == 0 && cartSum >= 4000) {
                  res.cost = 0;
                }
                let shippingMethod = {
                  id: res.shipping_method_id,
                  name: res.shipping_method_name,
                  days: Number.parseInt(res.delivery_time),
                  cost: Math.ceil(res.cost),
                };
                shippingMethods.push(shippingMethod);
              }
              this.shippingMethods = shippingMethods;
            } else {
              this.snackBar.open('Ошибка расчета стоимости доставки. Попробуйте позднее', 'x', {
                duration: 3000
              });
              return;
            }
          }
          this.loadShipping = false;
          this.chooseShippingMethod(this.shippingMethods[0]);
        }, (error) => {
          this.loadShipping = false;
          console.log(error);
        });
      }
    } else {
      this.loadShipping = false;
    }
  }

  chooseShippingMethod(type) {
    for (let method of this.shippingMethods) {
      method.selected = false;
      if (method == type) {
        method.selected = true;
      }
    }
    this.curShippingMethod = type.id;
    this.deliveryCost = Math.ceil(type.cost);
    if (type.id === 3) {// cdek PVZ
      this.dpList = [];
      this.getDataService.getDeliveryPoints(this.postcode).subscribe((data) => {
        if (this.curShippingMethod === 3) {
          this.dpList = data.cdek;
          this.showDPList = true;
        }
      });
    } else {
      this.showDPList = false;
    }
  }

  setClass(field) {
    let className = '';
    if (field === 'phone') {
      let phoneControl = this.userDataForm.get('phoneControl');
      if (!phoneControl.dirty) {
        className = '';
      }
      if (phoneControl.invalid && (phoneControl.dirty || phoneControl.touched)) {
        className = 'invalid';
      }
      if (phoneControl.valid) {
        className = 'valid';
      }
    }
    if (field === 'email') {
      let emailControl = this.userDataForm.get('emailControl');
      if (!emailControl.dirty) {
        className = '';
      }
      if (emailControl.invalid && (emailControl.dirty || emailControl.touched)) {
        className = 'invalid';
      }
      if (emailControl.valid) {
        className = 'valid';
      }
    }
    if (field === 'name') {
      let fioControl = this.userDataForm.get('fioControl');
      if (!fioControl.dirty) {
        className = '';
      }
      if (fioControl.invalid && (fioControl.dirty || fioControl.touched)) {
        className = 'invalid';
      }
      if (fioControl.valid) {
        className = 'valid';
      }
    }
    this.errorClass[field] = className;
  }

  formatPhone(phone: string) {
    phone = phone.replace('(', '').replace(')', '').replace('-', '').replace('-', '');
    if (phone.startsWith('+7')) {
      phone = phone.substring(2, 12);
    }
    if (phone.startsWith('7') || phone.startsWith('8')) {
      phone = phone.substring(1, 11);
    } else {
      phone = phone.substring(0, 10);
    }
    phone = phone.replace(/^(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/, '($1)$2-$3-$4');
    return '+7' + phone;
  }

  checkPromocode(code: string) {
    if (code)  {
      if (code == 'DARI2019') {
        this.orderHasGift = true;
        this.giftText = 'Гидроколлагеновые патчи (1шт.)';
      } else {
        this.getDataService.getPromocodeInfo(code).subscribe((res: Promocode) => {
          if (res) {
            if (res.code_type === 0) {
              let giftProd = Object.assign({}, res.gift as any);
              giftProd.price = 0;
              giftProd.quantity = 1;
              this.products.push(giftProd);
            } else if (res.code_type === 1) {
              if (res.discount <= 1) {
                this.promoOrder = true;
                this.promoDiscount = res.discount;
              }
            } else if (res.code_type === 2) {
              this.refPromoOrder = true;
            }
            this.promocode = res.code;
          }
        });
      }
    }
  }

  ngOnInit() {
    registerLocaleData( ru );
    this.orderHasGift = false;
    this.giftText = '';
    this.isActiveComponent = true;
    this.loadShipping = false;
    this.promoOrder = false;
    this.refPromoOrder = false;
    this.bClist = [{
      text: 'Главная',
      link: '/'
    }, {
      text: 'Оформление заказа',
      link: null
    }];
    AppDataService.userDataChange$.subscribe((data) => {
      if (data) {
        this.loggedIn = true;
        this.user = data;
        this.setUserData();
      }
    });
    let localPromo, localCartS;
    if (isPlatformBrowser(this.platformId)) {
      localPromo = localStorage.getItem('bshop_promo');
      localCartS = localStorage.getItem('cart');
    }
    this.hasOwnAddress = false;
    this.firstStep = true;
    this.loggedIn = AppDataService.userLoggedIn;
    this.location = {};
    this.dpList = [];
    this.kits = [];
    this.cartEvents = [];
    this.agree = true;
    this.shippingMethods = [];
    let defaultShipping = {
      name: 'Почта России',
      cost: 250,
      selected: true
    };
    this.shippingMethods.push(defaultShipping);
    this.showDeliveryBlock = false;
    this.orderWeight = 0;
    this.user = AppDataService.user;
    if (localCartS) {
      this.localCart = JSON.parse(localCartS);
      let searchProducts = '';
      this.cartEvents = this.localCart.filter(prod => prod.event_id);
      for (let product of this.localCart) {
        if (product.product_id) {
          if (product.isKit) {
            this.getDataService.getProgramData(product.product_id).subscribe((data) => {
              if (data) {
                this.kits.push(data);
              }
            });
          } else {
            if (product.product_id) {
              searchProducts += '&id=' + product.product_id;
            }
          }
        }
      }
      if (searchProducts) {
        this.getDataService.getProductsList(searchProducts).subscribe((data) => {
          // console.log(data);
          this.products = data;
          data.forEach(prod => {
            this.orderWeight += prod.weight;
          });
        });
      }
      this.checkPromocode(localPromo);
    }

    // let fioControl = this.userDataForm.get('fioControl');
    // fioControl.valueChanges.subscribe((res: string) => {
    //   if (res.length) {
    //     let ar = res.split(' ');

    //   }
    // })

    let regionControl = this.deliveryForm.get('regionControl');
    regionControl.valueChanges.pipe(debounceTime(300), takeWhile(() => this.isActiveComponent)).subscribe((res) => {
      if (res) {
        if (res.length > 2) {
          this.regionOptions = [];
          let queryDaData = {
            locations: [],
            from_bound: {value: 'region'},
            to_bound: {value: 'area'},
            query: res
          };
          this.autocompleteAddress(regionControl, queryDaData, this.oldRegion, this.regionOptions);
          this.eraseAddressControls(['cityControl', 'streetControl', 'houseControl', 'flatControl']);
          this.cityOptions = [];
          this.streetOptions = [];
          this.houseOptions = [];
        }
      }
    });

    let cityControl = this.deliveryForm.get('cityControl');
    cityControl.valueChanges.pipe(debounceTime(300), takeWhile(() => this.isActiveComponent)).subscribe((res) => {
      if (res) {
        if (res.length < 3) {
          this.location['settlement_fias_id'] = '';
          this.location['city_fias_id'] = '';
          this.location['street_fias_id'] = '';
          this.kladrId = '';
          this.shippingMethods = [];
          this.shippingMethods.push(defaultShipping);
        }
        if (res.length > 1) {
          this.cityOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'city'},
            to_bound: {value: 'settlement'},
            query: res
          };
          this.autocompleteAddress(cityControl, queryDaData, this.oldCity, this.cityOptions);
          this.eraseAddressControls(['streetControl', 'houseControl', 'flatControl']);
          this.streetOptions = [];
          this.houseOptions = [];
        }
      }
    });

    let streetControl = this.deliveryForm.get('streetControl');
    streetControl.valueChanges.pipe(debounceTime(300), takeWhile(() => this.isActiveComponent)).subscribe((res) => {
      if (res) {
        if (res.length < 3) {
          this.location['street_fias_id'] = '';
          this.kladrId = '';
          this.shippingMethods = [];
          this.shippingMethods.push(defaultShipping);
        }
        if (res.length) {
          this.streetOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'street'},
            to_bound: {value: 'street'},
            query: res
          };
          this.autocompleteAddress(streetControl, queryDaData, this.oldStreet, this.streetOptions);
          this.eraseAddressControls(['houseControl', 'flatControl']);
          this.houseOptions = [];
        }
      }
    });

    let houseControl = this.deliveryForm.get('houseControl');
    houseControl.valueChanges.pipe(debounceTime(500), takeWhile(() => this.isActiveComponent)).subscribe((res) => {
      if (res) {
        if (res.length) {
          this.houseOptions = [];
          let locations = [];
          locations.push(this.location);
          let queryDaData = {
            locations: locations,
            from_bound: {value: 'house'},
            query: res
          };
          this.autocompleteAddress(houseControl, queryDaData, this.oldHouse, this.houseOptions);
          this.eraseAddressControls(['flatControl']);
        }
      }
    });

    this.setUserData();

    let phoneControl = this.userDataForm.get('phoneControl');
    phoneControl.valueChanges.subscribe((data) => {
      if (phoneControl.value) {
        if ((data.length == 11) && (!data.includes('(')) && (!data.includes(')')) && (!data.includes('-')) && (!data.startsWith('+'))) {
          phoneControl.patchValue(this.formatPhone(data));
        }
        if (data.length == 12 && data.startsWith('+7')) {
          phoneControl.patchValue(this.formatPhone(data));
        }
      }
    });

    AppDataService.userStatusChange$.subscribe(() => {
      if (AppDataService.userLoggedIn) {
        this.user = AppDataService.user;
        this.loggedIn = AppDataService.userLoggedIn;
        this.setUserData();
      }
    });
  }

  setUserData() {
    this.isPartner = false;
    let localOrderS;
    if (isPlatformBrowser(this.platformId)) {
      localOrderS = localStorage.getItem('bshop_order');
    }
    let fioControl = this.userDataForm.get('fioControl');
    let phoneControl = this.userDataForm.get('phoneControl');
    let emailControl = this.userDataForm.get('emailControl');
    if (localOrderS) {
      let localOrder = JSON.parse(localOrderS);
      fioControl.setValue(localOrder.surname + ' ' + localOrder.name + (localOrder.patronymic ? ' ' + localOrder.patronymic : ''));
      phoneControl.setValue(this.formatPhone(localOrder.phone));
      emailControl.setValue(localOrder.email);
      // let regionControl = this.deliveryForm.get('regionControl');
      // regionControl.setValue({value: localOrder.address.region});
      // regionControl.updateValueAndValidity();
    } else if (this.user && this.loggedIn) {
      // let user = AppDataService.user;
      if (this.user.addresses.length) {
        this.hasOwnAddress = true;
      }
      if (this.user && this.loggedIn) {
        if (this.user.partner_type == 'Партнер 3 уровня (дистрибьютор)') {
          this.isPartner = true;
        } else {
          this.isPartner = false;
        }
      }
      fioControl.setValue(this.user.last_name + ' ' + this.user.first_name + ((this.user.patronymic) ? ' ' + this.user.patronymic : ''));
      phoneControl.setValue(this.formatPhone(this.user.phone));
      emailControl.setValue(this.user.email);
    }
  }

  login() {
    let dialogRef = this.dialog.open(PopupLoginComponent, {
      data: {
        stayOn: true
      }
    });
    dialogRef.afterClosed().subscribe((res) => {
      if (res) {
        if (res === 'signup') {
          this.dialog.open(PopupSignupComponent);
        }
        if (res === 'forgot') {
          this.dialog.open(PopupadviceComponent, {
            data: {
              type: 'forgot'
            }
          });
        }
      }
    });
  }

  eraseAddressControls(arrayControls: string[]) {
    for (let controlName of arrayControls) {
      this.deliveryForm.get(controlName).reset();
    }
  }

  selectRegion(event) {
    if (event.option) {
      let region = event.option.value;
      this.location = {};

      // console.log(event);
      if (region) {
        if (region.data.area_fias_id) {
          this.location['area_fias_id'] = region.data.area_fias_id;
        } else {
          this.location['region_fias_id'] = region.data.region_fias_id;
        }
      }
    }
  }

  selectCity(event) {
    // let region = this.deliveryForm.get('regionControl');
    if (event.option) {
      let city = event.option.value;
      this.location['settlement_fias_id'] = '';
      this.location['city_fias_id'] = '';
      if (city) {
        if (city.data.settlement_fias_id){
          this.location['settlement_fias_id'] = city.data.settlement_fias_id;
        } else {
          this.location['city_fias_id'] = city.data.city_fias_id;
        }
        this.kladrId = city.data.kladr_id;
        this.postcode = city.data.postal_code;
        this.selectedSuggestion = city.data;
        this.unrestrictedAddress = city.unrestricted_value;
        // region.setValue(city.data.region_with_type);
        this.getShippingMethods();
        // this.showDeliveryBlockFn();
      }
    }
  }

  selectStreet(event) {
    if (event.option) {
      let street = event.option.value;
      this.location['street_fias_id'] = '';
      if (street) {
        this.location['street_fias_id'] = street.data.street_fias_id;
        this.kladrId = street.data.kladr_id;
        this.postcode = street.data.postal_code;
        this.selectedSuggestion = street.data;
        this.unrestrictedAddress = street.unrestricted_value;
        this.getShippingMethods();
        if (!this.postcode) {
          this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31',
            {
              query: this.unrestrictedAddress,
              restrict_value: true,
              count: 1
            }).subscribe((data) => {
              if (data.suggestions) {
                if (data.suggestions.length == 1) {
                  this.selectedSuggestion = data.suggestions[0].data;
                  this.postcode = this.selectedSuggestion.postal_code;
                  this.getShippingMethods();
                }
              }
          });
        }
      }
    }
  }

  selectHouse(event) {
    if (event.option) {
      let house = event.option.value;
      if (house) {
        this.kladrId = house.data.kladr_id;
        this.postcode = house.data.postal_code;
        this.selectedSuggestion = house.data;
        this.unrestrictedAddress = house.unrestricted_value;
        this.getShippingMethods();
        if (!this.postcode) {
          this.getDataService.dadataQuery('62c868493b7000c72a320298458761611b70cc31',
            {
              query: this.unrestrictedAddress,
              restrict_value: true,
              count: 1
            }).subscribe((data) => {
              if (data.suggestions) {
                if (data.suggestions.length == 1) {
                  this.selectedSuggestion = data.suggestions[0].data;
                  this.postcode = this.selectedSuggestion.postal_code;
                  this.getShippingMethods();
                }
              }
          });
        }
      }
    }
  }

  displayRegion(region?: any) {
    return region ? region.value : '';
  }

  displayCity(city?: any) {
    if (city) {
      let area = isNullOrUndefined(city.data.area_with_type) ? '' : city.data.area_with_type + ', ';
      let cityA = isNullOrUndefined(city.data.city_with_type) ? '' : city.data.city_with_type + ', ';
      let settlement = isNullOrUndefined(city.data.settlement_with_type) ? '' : city.data.settlement_with_type;
      let fullCity = (area + cityA + settlement).trim();
      if (fullCity.substr(fullCity.length - 1, 1) === ',') {
        fullCity = fullCity.substring(0, fullCity.length - 1);
      }
      return fullCity;
    } else {
      return '';
    }
  }

  displayStreet(street?: any) {
    if (street) {
      let adr = '';
      if (street.data.settlement && street.data.area) {
        adr = street.data.street_with_type + '(' + street.data.settlement_with_type + ', ' + street.data.area_with_type + ')';
      } else {
        adr = street.data.street_with_type;
      }
      return adr;
    } else {
      return '';
    }
  }

  displayHouse(house?: any) {
    if (house) {
      let adr = house.data.house_type + ' ' + house.data.house;
      if (house.data.block) {
        adr += ' ' + house.data.block_type + ' ' + house.data.block;
      }
      return adr;
    } else {
      return '';
    }
  }

  checkAutocomplete(control: AbstractControl, options: any[]) {
    if (control) {
      let res = false;
      let opt = options.filter(o => o == control.value);
      if (opt.length) {
        res = true;
      }
      if (!res && !this.postcode) {
        control.reset();
      }
    }
  }

  getProductData(product, type) {
    if (product) {
      let productCart = this.localCart.find(item => item.product_id == product.id);
      if (productCart) {
        switch (type) {
          case 'primary_image': return AppDataService.getThumbImg(product);
          case 'name': return product.name;
          case 'quantity': return productCart.quantity;
          case 'sum': return (productCart.quantity * Number(product.price));
          default: return '';
        }
      } else {
        if (type == 'quantity') {
          return product.quantity;
        }
      }
    }
  }

  getEventImg(promo) {
    if (promo && promo.event_image) {
      return promo.event_image;
    } else {
      return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
    }
  }

  getEventPrice(promo) {
    let sum = 0;
    if (promo) {
      promo.order_event_products.forEach(prod => {
        sum += prod.amount;
      });
    }
    return sum;
  }

  getCartSum(discount: boolean = false) {
    if (isPlatformBrowser(this.platformId)) {
      let localCart = JSON.parse(localStorage.getItem('cart'));
      let sum = 0;
      if (localCart) {
        localCart.forEach(prod => {
          if (prod.product_id) {
            sum += (prod.quantity * Number(prod.price));
          }
          if (prod.event_id) {
            sum += this.getEventPrice(prod) * prod.quantity;
          }
        });
        if (discount) {
          if (this.promoDiscount) {
            sum = sum * (1 - this.promoDiscount);
          }
        }
        return sum;
      } else {
        return 0;
      }
    } else {
      return 0;
    }
  }

  trimString(str: string, charsArray: string[]) {
    charsArray.forEach(ch => {
      str = str.replace(new RegExp('\\' + ch, 'g'), '');
    });
    return str;
  }

  saveOrder() {
    let fioControl = this.userDataForm.get('fioControl');
    let phoneControl = this.userDataForm.get('phoneControl');
    let emailControl = this.userDataForm.get('emailControl');
    let regionControl = this.deliveryForm.get('regionControl');
    let cityControl = this.deliveryForm.get('cityControl');
    let houseControl = this.deliveryForm.get('houseControl');
    let flatControl = this.deliveryForm.get('flatControl');
    let address: any = {};
    if (fioControl.invalid || fioControl.untouched) {
      fioControl.markAsTouched();
    }
    if (phoneControl.invalid || phoneControl.untouched) {
      phoneControl.markAsTouched();
    }
    if (emailControl.invalid || emailControl.untouched) {
      emailControl.markAsTouched();
    }
    if (!this.selectedAddress) {
      if (regionControl.invalid || regionControl.untouched) {
        regionControl.markAsTouched();
      }
      if (cityControl.invalid || cityControl.untouched) {
        cityControl.markAsTouched();
      }
      if ((this.deliveryForm.valid && this.selectedSuggestion && this.postcode && (this.curShippingMethod != 7) && (this.curShippingMethod != 3))) {
        // console.log(this.selectedSuggestion);
        // console.log(this.unrestrictedAddress);
        address = {
          kladr_id: this.kladrId,
          postcode: this.postcode,
          region: this.selectedSuggestion.region_with_type,
          district: this.selectedSuggestion.area_with_type,
          settlement: this.selectedSuggestion.settlement_with_type,
          country: this.selectedSuggestion.country,
          city: this.selectedSuggestion.city_with_type,
          street: this.selectedSuggestion.street_with_type,
          house: (this.selectedSuggestion.house) ? this.selectedSuggestion.house : houseControl.value,
          flat: flatControl.value,
          cdek_city_id: null
        };
      } else if ((this.curShippingMethod == 7)) {
        address = {};
      } else if (this.curShippingMethod == 3) {

      } else {
        this.snackBar.open('Ошибка адреса, воспользуйтесь подсказками при вводе.', 'x', {
          duration: 3000
        });
        houseControl.markAsTouched();
        return;
      }
    } else {
      let adr = this.user.addresses.find(i => i.id == this.selectedAddress);
      address = {
        kladr_id: adr.kladr_id,
        postcode: adr.postcode,
        region: adr.region,
        district: adr.district,
        settlement: adr.settlement,
        country: adr.country,
        city: adr.city,
        street: adr.street,
        house: adr.house,
        flat: adr.flat,
        cdek_city_id: null
      };
    }

    // console.log(address);

    if (this.userDataForm.invalid || (this.deliveryForm.invalid && !this.selectedAddress && (this.curShippingMethod != 7))) {
      this.hasErrors = true;
    } else {
      if (!this.postcode && (this.curShippingMethod != 7)) {
        this.snackBar.open('Индекс не определен! При заполнении адреса воспользуйтесь подсказками.', 'x', {
          duration: 5000
        });
        this.deliveryForm.reset();
        return;
      }
      let order_products = [];
      let order_kits = [];
      let order_events = this.localCart.filter(item => item.event_id);
      for (let product of this.localCart) {
        if (product.product_id) {
          let price = + product.price;
          price = (this.ownOrder) ? (price * (1 - this.user.current_discount)) : price;
          if (product.isKit) {
            let kitInfo: any = {};
            kitInfo = {
              kit_id: product.product_id,
              quantity: product.quantity,
              price: + price,
              amount: price * product.quantity
            };
            if (product.id) {
              kitInfo.id = product.id;
            }
            order_kits.push(kitInfo);
          } else {
            let prodInfo: any = {};
            prodInfo = {
              product_id: product.product_id,
              quantity: product.quantity,
              price: +(price),
              amount: price * product.quantity
            };
            if (product.id) {
              prodInfo.id = product.id;
            }
            order_products.push(prodInfo);
          }
        }
      }
      let surname: string, name: string, patronymic: string, deliveryPointId: any;
      if (fioControl.valid) {
        let fioArray = String(fioControl.value).split(' ');
        surname = fioArray[0];
        name = fioArray[1];
        if (fioArray.length > 2) {
          patronymic = fioArray[2];
        } else {
          patronymic = null;
        }
        if (this.curShippingMethod != 3) {
          deliveryPointId = null;
        } else {
          deliveryPointId = this.selectedDP;
        }
        let order_info = {
          total_amount: (this.promoOrder) ? +((this.getCartSum() * (1 - this.promoDiscount))).toFixed(2) : this.getCartSum(),
          total_amount_wo_discount: this.getCartSum(),
          own: this.ownOrder,
          phone: this.trimString(phoneControl.value, ['(', ')', ' ', '+', '-']).substr(0, 11),
          email: this.userDataForm.get('emailControl').value.toLowerCase(),
          surname: surname,
          name: name,
          patronymic: patronymic,
          promocode: this.promocode,
          memo: this.userDataForm.get('memoControl').value,
          order_type: 0,
          order_products: order_products,
          order_kits: order_kits,
          order_events: order_events,
          shipping_method_id: this.curShippingMethod,
          delivery_point_id: deliveryPointId,
          shipping_amount: this.deliveryCost,
          address: address
        };
        let editOrder = '';
        if (isPlatformBrowser(this.platformId)) {
          if (localStorage.getItem('bshop_order')) {
            let localOrder = JSON.parse(localStorage.getItem('bshop_order'));
            editOrder = localOrder.id;
          }
        }
        this.getDataService.saveOrder(editOrder, order_info).subscribe((data) => {
          // console.log(data);
          if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('cart');
            localStorage.removeItem('bshop_promo');
            localStorage.removeItem('bshop_order');
          }
          AppDataService.cartChange$.emit();
          this.router.navigate(['order/' + data.id]);
        }, (error) => {
          if (error.error)  {
            let msg = '';
            for (let k in error.error) {
              if (k) {
                msg += '[' + k + '] ' + error.error[k];
              }
            }
            this.snackBar.open(msg, 'x', {
              duration: 3000
            });
          } else {
            this.snackBar.open(error, 'x', {
              duration: 3000
            });
          }
        });
      }
    }
  }

  nextStep() {
    this.userDataForm.get('fioControl').markAsTouched();
    this.userDataForm.get('phoneControl').markAsTouched();
    this.userDataForm.get('emailControl').markAsTouched();
    for (let key of ['name', 'phone', 'email']) {
      this.setClass(key);
    }
    if (this.userDataForm.valid) {
      this.firstStep = false;
    } else {
      return;
    }
  }

  getFullAddress(adr) {
    if (adr) {
      let address = ((adr.city) ? adr.city + ', ' : '') +
                    ((adr.settlement) ? adr.settlement + ', ' : '') +
                    ((adr.street) ? adr.street + ', ' : '') +
                    ((adr.house) ? adr.house : '');
      return address;
    } else {
      return '';
    }
  }

  selectOwnAddress() {
    // console.log(this.selectedAddress);
    let adr = this.user.addresses.find(i => i.id == this.selectedAddress);
    if (adr) {
      this.getShippingMethods(adr.postcode);
      this.postcode = adr.postcode;
    }
  }

  getProgramData(kit, type = '') {
    if (kit) {
      if (kit.kit_images) {
        return kit.kit_images[0].image;
      } else {
        return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
      }
    } else {
      return 'https://dari-cosmetics.ru/assets/logo-new.jpg';
    }
  }

  openCart() {
    this.router.navigate(['cart']);
  }

  openDoc() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://dari-cosmetics.ru/assets/docs/personal_data.pdf', '_blank');
    }
  }

  getThumbImg(relProd) {
    return AppDataService.getThumbImg(relProd);
  }

  ngOnDestroy() {
    this.isActiveComponent = false;
  }

  getDeliveryFormHeight() {
    let height = 0;
    if (!this.firstStep) {
      height = this.shippingMethods.length * 46;
      if (this.hasOwnAddress) {
        height += 46;
      }
      if (this.selectedAddress) {
        height += 166;
      } else {
        height += 456;
      }
      if (this.curShippingMethod == 3) {
        height += 60;
      }
    }
    return height + 'px';
  }

  clearOwnAddress() {
    this.selectedAddress = '';
    this.shippingMethods = [];
    let defaultShipping = {
      name: 'Почта России',
      cost: 250,
      selected: true
    };
    this.shippingMethods.push(defaultShipping);
  }

  checkPhone() {
    this.errorClass.phone = '';
    let phoneControl = this.userDataForm.get('phoneControl');
    if (!phoneControl.value || phoneControl.value.length < 2) {
      phoneControl.setValue('+7');
    }
  }

  isControlInvalid(controlName: string) {
    let control = this.deliveryForm.get(controlName);
    return (control.invalid && control.touched);
  }

}
