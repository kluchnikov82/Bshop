import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { MatDialog } from '@angular/material';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { isPlatformBrowser } from '@angular/common';
import { PopupadviceComponent } from '../popup/popupadvice/popupadvice.component';
import { AppDataService } from '../../services/app-data.service';
import { CatalogService } from '../../routed/catalog/catalog.service';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss'],
  animations: [
    trigger('expandPanel', [
      state('initial', style({height: 0, opacity: 0, zIndex: -1})),
      state('expanded', style({height: '*', opacity: 1})),
      transition('* => *', animate('0.2s'))
    ])
  ]
})
export class FooterComponent implements OnInit {

  public categories: any[];
  public socialState: string;
  public serviceState: string;
  public catalogState: string;
  public companyState: string;
  public menuList: any[] = [];
  public showFooterMenu: boolean;

  constructor(
    private router: Router,
    private acRoute: ActivatedRoute,
    public sanitizer: DomSanitizer,
    private dialog: MatDialog,
    private catalogService: CatalogService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    this.catalogState = 'initial';
    this.serviceState = 'initial';
    this.socialState = 'initial';
    this.companyState = 'initial';
    this.showFooterMenu = true;

    this.router.events.subscribe((res) => {
      if (this.router.url.includes('order/')) {
        this.showFooterMenu = false;
      } else {
        this.showFooterMenu = true;
      }
    });

    this.catalogService.catalog$.subscribe((res) => {
      this.menuList = res;
      for (let cat of this.menuList) {
        cat.state = 'initial';
      }
    });

    // AppDataService.menuListChange$.subscribe(() => {
    // });
  }

  openCatalog(categoryName: any, subcat: any = false) {
    // AppDataService.currentCategory = categoryName;
    AppDataService.currentCategoryChange$.emit({subcat: false, category: categoryName});
    this.router.navigate(['catalog/' + categoryName + ((subcat) ? '/' + subcat : '')]);
  }

  openPage(page: string) {
    this.router.navigate([page]);
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

  toggleMenu(state: string) {
    if (state == 'initial') {
      state = 'expanded;';
    } else {
      state = 'initial';
    }
    return state;
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

  openPopup() {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'consult'
      }
    });
  }

  trackCategory(index, category) {
    return category.id;
  }

  openDog() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://dari-cosmetics.ru/assets/docs/dogovor.pdf', '_blank');
    }
  }

}
