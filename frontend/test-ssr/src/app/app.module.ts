import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { PrebootModule } from 'preboot';
import { AuthServiceConfig, SocialLoginModule, FacebookLoginProvider, VkontakteLoginProvider } from 'angular-6-social-login-v2';

import { SharedModule } from './shared/shared.module';
import { AppComponent } from './app.component';
import { GetDataService } from './services/get-data.service';
import { CatalogService } from './catalog/catalog.service';
import { TopPanelComponent } from './top-panel/top-panel.component';
import { NavbarComponent } from './navbar/navbar.component';

// import { MainPageComponent } from './main-page/main-page.component';

import { CommentsComponent } from './comments/comments.component';
import { FooterComponent } from './footer/footer.component';

import { CartComponent } from './cart/cart.component';
import { SocialCallbackComponent } from './social-callback/social-callback.component';
import { PromoComponent } from './promo/promo.component';
import { PopupLoginComponent } from './popup/popup-login/popup-login.component';
import { CartPreviewComponent } from './cart-preview/cart-preview.component';
import { PopupSignupComponent } from './popup/popup-signup/popup-signup.component';
import { PopupadviceComponent } from './popup/popupadvice/popupadvice.component';
import { PopupAddressComponent } from './popup/popup-address/popup-address.component';
import { ForgotPasswordComponent } from './forgot-password/forgot-password.component';
// import { AuthGuard } from './account/auth.guard';

const routes: Routes = [
  // {
  //   path: 'account',
  //   loadChildren: './account/account.module#AccountModule',
  //   canActivate: [AuthGuard],
  //   canActivateChild: [AuthGuard]
  // },
  {
    path: 'catalog',
    loadChildren: './catalog/catalog.module#CatalogModule'
  },
  {
    path: 'order',
    loadChildren: './order/order.module#OrderModule'
  },
  {
    path: 'care-program',
    loadChildren: './care-program/care-program.module#CareProgramModule'
  },
  {
    path: 'info',
    loadChildren: './info/info.module#InfoModule'
  },
  {
    path: 'blog',
    loadChildren: './blog/blog.module#BlogModule'
  },
  {
    path: 'comments',
    component: CommentsComponent,
    data: {preload: true}
  },
  {
    path: 'cart',
    component: CartComponent,
    data: {preload: true}
  },
  {
    path: 'order-success',
    loadChildren: './order-success/order-success.module#OrderSuccessModule'
  },
  {
    path: '',
    loadChildren: './main-page/main-page.module#MainPageModule'
  },
  {
    path: 'social-callback',
    component: SocialCallbackComponent,
    data: { preload: true }
  },
  {
    path: 'promo',
    component: PromoComponent,
    data: { preload: true }
  },
  {
    path: 'password/confirm/:id',
    component: ForgotPasswordComponent,
    data: { preload: true }
  },
];

let socialConfig = new AuthServiceConfig([
  {
  id: FacebookLoginProvider.PROVIDER_ID,
  provider: new FacebookLoginProvider('930428823969368')
  },
  // {
  //   id: VkontakteLoginProvider.PROVIDER_ID,
  //   provider: new VkontakteLoginProvider('6991642')
  // }
])

export function provideSocialConfig() {
  return socialConfig;
}

@NgModule({
  declarations: [
    AppComponent,
    TopPanelComponent,
    NavbarComponent,
    // MainPageComponent,
    CommentsComponent,
    FooterComponent,
    CartComponent,
    SocialCallbackComponent,
    PromoComponent,
    PopupLoginComponent,
    CartPreviewComponent,
    PopupSignupComponent,
    PopupadviceComponent,
    PopupAddressComponent,
    ForgotPasswordComponent,
    // PopupEventComponent,
    // InstafeedComponent
  ],
  imports: [
    BrowserModule.withServerTransition({ appId: 'bshop-server' }),
    PrebootModule.withConfig({appRoot: 'app-root'}),
    BrowserAnimationsModule,
    RouterModule.forRoot(routes, {preloadingStrategy: PreloadAllModules}),
    HttpClientModule,
    SharedModule,
    SocialLoginModule
  ],
  entryComponents: [
    // MainPageComponent,
    CommentsComponent,
    PopupLoginComponent,
    PopupSignupComponent,
    PopupadviceComponent,
    PopupAddressComponent,
    // InstafeedComponent
  ],
  exports: [
    RouterModule,
    SharedModule
  ],
  providers: [
    GetDataService,
    {
      provide: AuthServiceConfig,
      useFactory: provideSocialConfig
    },
    // AuthGuard
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
