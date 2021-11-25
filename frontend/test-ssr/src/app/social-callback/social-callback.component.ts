import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { Subscription } from 'rxjs';
import { GetDataService } from './../services/get-data.service';
import { AppDataService } from '../services/app-data.service';

@Component({
  selector: 'app-social-callback',
  templateUrl: './social-callback.component.html',
  styleUrls: ['./social-callback.component.scss']
})
export class SocialCallbackComponent implements OnInit {

  private subscription: Subscription;
  public accessToken: string;
  public url: any;

  constructor(
    private router: Router,
    private getDataService: GetDataService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
   }

  ngOnInit() {
    this.url = this.router.url;
    // let url = this.route.url;
    let parseURL = this.router.parseUrl(this.url);
    // console.log(parseURL);
    let token = parseURL.queryParams.code;
    if (isPlatformBrowser(this.platformId)) {
      this.getDataService.vkAuth(token).subscribe((data) => {
        if (data) {
          localStorage.removeItem('bshop_id');
          localStorage.removeItem('bshop_t');
          localStorage.setItem('bshop_id', data.user.id);
          localStorage.setItem('bshop_t', 'JWT ' + data.token);
          AppDataService.userLoggedIn = true;
          AppDataService.userStatusChange$.emit();
          this.router.navigate(['account']);
        }
        // console.log(data);
      });
    }
  }

  // loginVK(str) {
  //   if (str) {
  //     let token = str.substring(str.indexOf('access_token=') + 13, str.indexOf('&expires'));
  //     console.log(token);
  //     console.log(this.url);
  //     this.getDataService.facebookAuth(token, 'vk-oauth2').subscribe((data) => {
  //       console.log(data);
  //     })

  //   }
  // }

}
