import { Component, OnInit } from '@angular/core';
import { AppDataService } from '../services/app-data.service';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { MatDialog } from '@angular/material';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { PopupadviceComponent } from '../popup/popupadvice/popupadvice.component';

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
    public sanitizer: DomSanitizer,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.catalogState = 'initial';
    this.serviceState = 'initial';
    this.socialState = 'initial';
    this.companyState = 'initial';
    this.showFooterMenu = true;

    this.router.events.subscribe((res) => {
      if (this.router.url.includes('order/')){
        this.showFooterMenu = false;
      }else {
        this.showFooterMenu = true;
      }
    })

    AppDataService.menuListChange$.subscribe(() => {
      this.menuList = AppDataService.menuList;
      for (let cat of this.menuList) {
        cat.state = 'initial';
      }
    })
  }

  openCatalog(categoryName: any) {
    AppDataService.currentCategory = categoryName;
    AppDataService.currentCategoryChange$.emit({subcat: false, category: categoryName});
    this.router.navigate(['catalog']);
  }

  openPage(page: string) {
    this.router.navigate([page]);
  }

  openInst() {
    window.open('https://instagram.com/daricosmetics', '_blank');
  }

  openVK() {
    window.open('https://vk.com/daricosmetics', '_blank');
  }

  openFB() {
    window.open('https://www.facebook.com/Daricosmetics-103691007751764/','_blank');
  }

  toggleMenu(state: string) {
    if (state == 'initial') {
      state = 'expanded;'
    }else {
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
      return (category.state == 'initial')? 'expanded' : 'initial';
    }
    return curCat.state;
  }

  openPopup() {
    this.dialog.open(PopupadviceComponent, {
      data: {
        type: 'consult'
      }
    })
  }

  trackCategory(index, category) {
    return category.id;
  }

  openDog() {
    window.open('/assets/docs/dogovor.pdf', '_blank');
  }

}
