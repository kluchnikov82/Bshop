import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NgModule } from '@angular/core';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';
import { AuthServiceConfig, SocialLoginModule, FacebookLoginProvider, VkontakteLoginProvider } from 'angular-6-social-login-v2';

import { SharedModule } from './shared/shared.module';
import { AppComponent } from './app.component';
import { GetDataService } from './shared/services/get-data.service';
import { TopPanelComponent } from './shared/top-panel/top-panel.component';
import { NavbarComponent } from './shared/navbar/navbar.component';

import { MainPageComponent } from './routed/main-page/main-page.component';

import { CommentsComponent } from './routed/comments/comments.component';
import { FooterComponent } from './shared/footer/footer.component';

import { InstafeedComponent } from './routed/main-page/instafeed/instafeed.component';
import { CartComponent } from './routed/cart/cart.component';
import { SocialCallbackComponent } from './shared/social-callback/social-callback.component';
import { PromoComponent } from './routed/promo/promo.component';
import { PopupLoginComponent } from './shared/popup/popup-login/popup-login.component';
import { CartPreviewComponent } from './routed/cart/cart-preview/cart-preview.component';
import { PopupSignupComponent } from './shared/popup/popup-signup/popup-signup.component';
import { PopupadviceComponent } from './shared/popup/popupadvice/popupadvice.component';
import { PopupAddressComponent } from './shared/popup/popup-address/popup-address.component';
import { ForgotPasswordComponent } from './routed/forgot-password/forgot-password.component';
import { PopupEventComponent } from './shared/popup/popup-event/popup-event.component';
import { AuthGuard } from './routed/account/auth.guard';
import { NotFoundComponent } from './routed/not-found/not-found.component';

const routes: Routes = [
  {
    path: 'account',
    loadChildren: './routed/account/account.module#AccountModule',
    canActivate: [AuthGuard],
    canActivateChild: [AuthGuard]
  },
  {
    path: 'catalog',
    loadChildren: './routed/catalog/catalog.module#CatalogModule'
  },
  {
    path: 'order',
    loadChildren: './routed/order/order.module#OrderModule'
  },
  {
    path: 'care-program',
    loadChildren: './routed/care-program/care-program.module#CareProgramModule'
  },
  {
    path: 'info',
    loadChildren: './routed/info/info.module#InfoModule'
  },
  {
    path: 'blog',
    loadChildren: './routed/blog/blog.module#BlogModule'
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
    loadChildren: './routed/order-success/order-success.module#OrderSuccessModule'
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
  {
    path: 'ref/:id',
    component: MainPageComponent,
    data: { preload: true }
  },
  {
    path: '',
    component: MainPageComponent,
    // pathMatch: 'full',
    data: { preload: true }
  },
  {
    path: '**',
    component: NotFoundComponent,
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
    MainPageComponent,
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
    PopupEventComponent,
    InstafeedComponent,
    NotFoundComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    RouterModule.forRoot(routes, {scrollPositionRestoration: 'enabled', anchorScrolling: 'enabled', preloadingStrategy: PreloadAllModules}),
    HttpClientModule,
    SharedModule,
    SocialLoginModule
  ],
  entryComponents: [
    MainPageComponent,
    CommentsComponent,
    PopupLoginComponent,
    PopupSignupComponent,
    PopupadviceComponent,
    PopupAddressComponent,
    InstafeedComponent
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
    AuthGuard
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
