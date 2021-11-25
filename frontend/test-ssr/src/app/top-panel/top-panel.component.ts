import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog, MatSnackBar } from '@angular/material';
import { PopupLoginComponent } from '../popup/popup-login/popup-login.component';
import { PopupSignupComponent } from '../popup/popup-signup/popup-signup.component';
import { PopupadviceComponent } from '../popup/popupadvice/popupadvice.component';
import { AppDataService } from '../services/app-data.service';
import { Person } from '../entities/person';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-top-panel',
  templateUrl: './top-panel.component.html',
  styleUrls: ['./top-panel.component.scss']
})
export class TopPanelComponent implements OnInit {
  public showShare: boolean = false;
  public textArea: HTMLTextAreaElement;
  public loggedIn: boolean;
  public user: Person;

  constructor(
    private router: Router,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {

    AppDataService.userStatusChange$.subscribe(() => {
      this.loggedIn = AppDataService.userLoggedIn;
      if (this.loggedIn) {
        this.user = AppDataService.user;
      }
    });

    this.showShare = false;
  }

  openPage(page) {
    this.router.navigate([page]);
  }

  share(social: string) {
    let link = this.getShareLink();
    switch (social) {
      case 'inst': link = 'https://instagram.com/daricosmetics'; break;
      case 'fb': link = 'https://www.facebook.com/sharer/sharer.php?u=' + link; break;
      case 'vk': link = 'https://vk.com/share.php?url=' + link; break;
      case 'ok': link = 'https://connect.ok.ru/offer?url=' + link; break;
      case 'twitter': link = 'http://twitter.com/share?&url=' + link; break;
    }
    if (isPlatformBrowser(this.platformId)) {
      window.open(link, '_blank');
    }
  }

  openPopup(type: string = '') {
    if (type === 'consult') {
      let dialogRef = this.dialog.open(PopupadviceComponent, {
        data: {
          type: 'consult'
        }
      });
    } else {
      let dialogRef = this.dialog.open(PopupLoginComponent);
      dialogRef.afterClosed().subscribe((res) => {
        if (res) {
          if (res === 'signup') {
            this.dialog.open(PopupSignupComponent);
          }
        }
      });
    }
  }

  isiOS() {
    if (isPlatformBrowser(this.platformId)) {
      return navigator.userAgent.match(/ipad|iphone/i);
    } else {
      return false;
    }
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
      let txt = this.getShareLink();
      this.createTextArea(txt);
      this.selectText();
      document.execCommand('copy');
      document.body.removeChild(this.textArea);
      this.snackBar.open('Ссылка скопирована в буфер обмена', 'x', {
        duration: 2000
      });
    }
  }

  getShareLink() {
    let link = 'https://dari-cosmetics.ru' + this.router.url;
    if (this.loggedIn && this.user.total_amount > 2000) {
      link += '/ref/' + this.user.ref_id;
    }
    return link;
  }

}
