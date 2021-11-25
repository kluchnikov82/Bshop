import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material';
import { Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { AuthService, FacebookLoginProvider, VkontakteLoginProvider, SocialUser } from 'angular-6-social-login-v2';
import { GetDataService } from '../../../services/get-data.service';
import { AppDataService } from '../../../services/app-data.service';

@Component({
  selector: 'app-popup-login',
  templateUrl: './popup-login.component.html',
  styleUrls: ['./popup-login.component.scss']
})
export class PopupLoginComponent implements OnInit {

  public agree = true;
  public username: string;
  public password: string;
  public showError = false;
  public errorText = '';

  constructor(
    public dialogRef: MatDialogRef<PopupLoginComponent>,
    private router: Router,
    private authService: AuthService,
    private getDataService: GetDataService,
    @Inject(MAT_DIALOG_DATA) public data,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
   }

  ngOnInit() {
  }

  closePopup(res: string = '') {
    this.dialogRef.close(res);
  }

  signUp() {
    this.closePopup('signup');
  }

  forgot() {
    this.closePopup('forgot');
  }

  signIn(platform: string) {
    let platformProvider;
    if (platform == 'fb') {
      platformProvider = FacebookLoginProvider.PROVIDER_ID;
      this.authService.signIn(platformProvider).then((data) => {
        if (data) {
          if (data.provider == 'facebook') {
            this.getDataService.facebookAuth(data.token, 'facebook').subscribe((data) => {
              // console.log(data);
              if (data) {
                if (isPlatformBrowser(this.platformId)) {
                  localStorage.removeItem('bshop_id');
                  localStorage.removeItem('bshop_t');
                  localStorage.setItem('bshop_id', data.user.id);
                  localStorage.setItem('bshop_t', 'JWT ' + data.token);
                }
                AppDataService.userLoggedIn = true;
                AppDataService.userStatusChange$.emit();
                this.router.navigate(['account']);
                this.closePopup();
              }
            });
          }
        }
        // console.log(data);
      });
    } else if (platform == 'vk') {
      if (isPlatformBrowser(this.platformId)) {
        window.open('https://oauth.vk.com/authorize?client_id=6991642&display=page&redirect_uri=https://dari-cosmetics.ru/social-callback&scope=email&response_type=code&v=5.101', '_blank');
      }
    }
  }

  signOut(): void {
    this.authService.signOut();
  }

  login() {
    if (this.username && this.password) {
      this.getDataService.loginUser(this.username.toLowerCase(), this.password).subscribe((data) => {
        // console.log(data);
        if (data.token && data.user) {
          AppDataService.user = data.user;
          AppDataService.userToken = 'JWT ' + data.token;
          if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem('bshop_id');
            localStorage.removeItem('bshop_t');
            localStorage.setItem('bshop_id', data.user.id);
            localStorage.setItem('bshop_t', AppDataService.userToken);
          }
          AppDataService.userLoggedIn = true;
          AppDataService.userStatusChange$.emit();
          if (this.data && this.data.stayOn) {

          } else {
            this.router.navigate(['account']);
          }
          this.closePopup();
        }
      },
      (error) => {
        this.showError = true;
        if (error.error.non_field_errors) {
          this.errorText = error.error.non_field_errors[0];
        }
      });
    }
  }

  openDoc() {
    if (isPlatformBrowser(this.platformId)) {
      window.open('https://dari-cosmetics.ru/assets/docs/dogovor.pdf', '_blank');
    }
  }

}
