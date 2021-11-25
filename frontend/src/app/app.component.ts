import { Component } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { MatIconRegistry } from '@angular/material';
import { GetDataService } from './shared/services/get-data.service';
import { AppDataService } from './shared/services/app-data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {

  constructor(
    iconReg: MatIconRegistry,
    public sanitizer: DomSanitizer,
    private getDataService: GetDataService
  ) {
    iconReg.addSvgIcon('back', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/back-copy-15.svg'));
    iconReg.addSvgIcon('forward', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/back-copy-14.svg'));
    iconReg.addSvgIcon('arrowShare', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/share.svg'));
    iconReg.addSvgIcon('shape', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shape.svg'));
    iconReg.addSvgIcon('shapeR', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shape-rose.svg'));
    iconReg.addSvgIcon('vk', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/vk.svg'));
    iconReg.addSvgIcon('fb', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/facebook.svg'));
    iconReg.addSvgIcon('instagram', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/instagram-copy.svg'));
    iconReg.addSvgIcon('close', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/close.svg'));
    iconReg.addSvgIcon('shipping', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/delivery.svg'));
    iconReg.addSvgIcon('share', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/sharing-interface.svg'));
    iconReg.addSvgIcon('payCard', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/credit-card-2.svg'));
    iconReg.addSvgIcon('info', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/information-circular-button-symbol.svg'));
    iconReg.addSvgIcon('catalog', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/icon-catalog.svg'));
    iconReg.addSvgIcon('search', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/search.svg'));
    iconReg.addSvgIcon('cart', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shopping-purse-icon.svg'));
    iconReg.addSvgIcon('account', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/logout.svg'));
    iconReg.addSvgIcon('starFill', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/star-fill.svg'));
    iconReg.addSvgIcon('star', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/star.svg'));
    iconReg.addSvgIcon('profile', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/user-2.svg'));
    iconReg.addSvgIcon('list', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/group-3.svg'));
    iconReg.addSvgIcon('tile', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/group-2.svg'));
    iconReg.addSvgIcon('shield', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shield.svg'));
    iconReg.addSvgIcon('notification', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/notifications-button.svg'));
    iconReg.addSvgIcon('point', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/placeholder-filled-point.svg'));
    iconReg.addSvgIcon('problem', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/sim-card-problem.svg'));
    iconReg.addSvgIcon('target', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/target.svg'));
    iconReg.addSvgIcon('leaf', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/leaf.svg'));
    iconReg.addSvgIcon('spa', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/spa-face-mask-treatment-for-woman.svg'));
    iconReg.addSvgIcon('watch', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/stopwatch.svg'));
    iconReg.addSvgIcon('views', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/visibility-button.svg'));
    iconReg.addSvgIcon('moon', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/moon.svg'));
    iconReg.addSvgIcon('sunrize', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/sunrise.svg'));
    iconReg.addSvgIcon('cottonPad', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/cotton-pad.svg'));
    iconReg.addSvgIcon('skinCare', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/skin-care.svg'));
    iconReg.addSvgIcon('beauty', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/beauty.svg'));
    iconReg.addSvgIcon('diet', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/diet.svg'));
    iconReg.addSvgIcon('waterBottle', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/water-bottle.svg'));
    iconReg.addSvgIcon('beauty2', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/beauty-2.svg'));
    iconReg.addSvgIcon('mascara', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/mascara.svg'));
    iconReg.addSvgIcon('refresh', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/refresh.svg'));
    iconReg.addSvgIcon('shopCart', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shopping-cart-black-shape.svg'));
    iconReg.addSvgIcon('sortUp', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/sort-up.svg'));
    iconReg.addSvgIcon('sortDown', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/sort-down.svg'));
    iconReg.addSvgIcon('greenCheck', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/green-check.svg'));
    iconReg.addSvgIcon('redCross', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/red-cross.svg'));
    iconReg.addSvgIcon('gift', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/gift-box.svg'));
    iconReg.addSvgIcon('shoppingBag', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shopping-bag.svg'));
    iconReg.addSvgIcon('megaphone', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/megaphone.svg'));
    iconReg.addSvgIcon('voucher', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/voucher.svg'));
    iconReg.addSvgIcon('order', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/order-copy.svg'));
    iconReg.addSvgIcon('shopping', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/shopping.svg'));
    iconReg.addSvgIcon('checkMark', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/check-mark.svg'));    
    iconReg.addSvgIcon('twitter', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/twitter.svg'));
    iconReg.addSvgIcon('ok', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/ok.svg'));
    iconReg.addSvgIcon('copy', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/copy-text.svg'));
    iconReg.addSvgIcon('checkBold', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/checkbold.svg'));
    iconReg.addSvgIcon('viber', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/viber.svg'));
    iconReg.addSvgIcon('whatsapp', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/whatsapp.svg'));
    iconReg.addSvgIcon('telegram', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/telegram.svg'));
    iconReg.addSvgIcon('vk_message', sanitizer.bypassSecurityTrustResourceUrl('/assets/icons/vk_message.svg'));

    this.getDataService.getMainSlides().subscribe((data) => {
      AppDataService.slides = data;
      AppDataService.slidesLoaded$.emit();
    })

    this.getDataService.getCatalog().subscribe((data) => {
      // console.log(data);
      //this.categories = data;
      AppDataService.menuList = data;
      AppDataService.menuListChange$.emit();
      //this.loaded = true;
    })

  }

  title = 'dari-cosmetics';
}
