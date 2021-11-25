import { Component } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { MatIconRegistry } from '@angular/material';
import { GetDataService } from './services/get-data.service';
import { AppDataService } from './services/app-data.service';
import { CatalogService } from './catalog/catalog.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(
    iconReg: MatIconRegistry,
    public sanitizer: DomSanitizer,
    private getDataService: GetDataService,
    private catalogService: CatalogService
  ) {

    catalogService.getCatalog().subscribe();

    iconReg.addSvgIcon('back', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/back-copy-15.svg'));
    iconReg.addSvgIcon('forward', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/back-copy-14.svg'));
    iconReg.addSvgIcon('arrowShare', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/share.svg'));
    iconReg.addSvgIcon('shape', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shape.svg'));
    iconReg.addSvgIcon('shapeR', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shape-rose.svg'));
    iconReg.addSvgIcon('vk', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/vk.svg'));
    iconReg.addSvgIcon('fb', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/facebook.svg'));
    iconReg.addSvgIcon('instagram', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/instagram-copy.svg'));
    iconReg.addSvgIcon('close', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/close.svg'));
    iconReg.addSvgIcon('shipping', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/delivery.svg'));
    iconReg.addSvgIcon('share', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/sharing-interface.svg'));
    iconReg.addSvgIcon('payCard', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/credit-card-2.svg'));
    iconReg.addSvgIcon('info', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/information-circular-button-symbol.svg'));
    iconReg.addSvgIcon('catalog', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/icon-catalog.svg'));
    iconReg.addSvgIcon('search', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/search.svg'));
    iconReg.addSvgIcon('cart', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shopping-purse-icon.svg'));
    iconReg.addSvgIcon('account', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/logout.svg'));
    iconReg.addSvgIcon('starFill', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/star-fill.svg'));
    iconReg.addSvgIcon('star', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/star.svg'));
    iconReg.addSvgIcon('profile', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/user-2.svg'));
    iconReg.addSvgIcon('list', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/group-3.svg'));
    iconReg.addSvgIcon('tile', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/group-2.svg'));
    iconReg.addSvgIcon('shield', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shield.svg'));
    iconReg.addSvgIcon('notification', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/notifications-button.svg'));
    iconReg.addSvgIcon('point', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/placeholder-filled-point.svg'));
    iconReg.addSvgIcon('problem', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/sim-card-problem.svg'));
    iconReg.addSvgIcon('target', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/target.svg'));
    iconReg.addSvgIcon('leaf', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/leaf.svg'));
    iconReg.addSvgIcon('spa', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/spa-face-mask-treatment-for-woman.svg'));
    iconReg.addSvgIcon('watch', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/stopwatch.svg'));
    iconReg.addSvgIcon('views', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/visibility-button.svg'));
    iconReg.addSvgIcon('moon', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/moon.svg'));
    iconReg.addSvgIcon('sunrize', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/sunrise.svg'));
    iconReg.addSvgIcon('cottonPad', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/cotton-pad.svg'));
    iconReg.addSvgIcon('skinCare', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/skin-care.svg'));
    iconReg.addSvgIcon('beauty', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/beauty.svg'));
    iconReg.addSvgIcon('diet', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/diet.svg'));
    iconReg.addSvgIcon('waterBottle', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/water-bottle.svg'));
    iconReg.addSvgIcon('beauty2', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/beauty-2.svg'));
    iconReg.addSvgIcon('mascara', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/mascara.svg'));
    iconReg.addSvgIcon('refresh', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/refresh.svg'));
    iconReg.addSvgIcon('shopCart', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shopping-cart-black-shape.svg'));
    iconReg.addSvgIcon('sortUp', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/sort-up.svg'));
    iconReg.addSvgIcon('sortDown', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/sort-down.svg'));
    iconReg.addSvgIcon('greenCheck', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/green-check.svg'));
    iconReg.addSvgIcon('redCross', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/red-cross.svg'));
    iconReg.addSvgIcon('gift', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/gift-box.svg'));
    iconReg.addSvgIcon('shoppingBag', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shopping-bag.svg'));
    iconReg.addSvgIcon('megaphone', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/megaphone.svg'));
    iconReg.addSvgIcon('voucher', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/voucher.svg'));
    iconReg.addSvgIcon('order', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/order-copy.svg'));
    iconReg.addSvgIcon('shopping', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/shopping.svg'));
    iconReg.addSvgIcon('checkMark', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/check-mark.svg'));
    iconReg.addSvgIcon('twitter', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/twitter.svg'));
    iconReg.addSvgIcon('ok', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/ok.svg'));
    iconReg.addSvgIcon('copy', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/copy-text.svg'));
    iconReg.addSvgIcon('checkBold', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/checkbold.svg'));
    iconReg.addSvgIcon('viber', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/viber.svg'));
    iconReg.addSvgIcon('whatsapp', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/whatsapp.svg'));
    iconReg.addSvgIcon('telegram', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/telegram.svg'));
    iconReg.addSvgIcon('vk_message', sanitizer.bypassSecurityTrustResourceUrl('https://dari-cosmetics.ru/assets/icons/vk_message.svg'));

    this.getDataService.getMainSlides().subscribe((data) => {
      AppDataService.slides = data;
      AppDataService.slidesLoaded$.emit();
    });

    // this.getDataService.getCatalog().subscribe((data) => {
    //   // console.log(data);
    //   // this.categories = data;
    //   AppDataService.menuList = data;
    //   AppDataService.menuListChange$.emit();
    //   // this.loaded = true;
    // });

  }

  title = 'dari-cosmetics';
}
