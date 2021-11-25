import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from '../../shared/shared.module';
import { RulesComponent } from './rules/rules.component';
import { ShippingComponent } from './shipping/shipping.component';
import { AboutComponent } from './about/about.component';
import { CertificatesComponent } from './certificates/certificates.component';
import { ContactsComponent } from './contacts/contacts.component';
import { FaqComponent } from './faq/faq.component';
import { OrderReturnComponent } from './order-return/order-return.component';
import { PartnersComponent } from './partners/partners.component';
import { PayingComponent } from './paying/paying.component';
import { PoliticsComponent } from './politics/politics.component';

const routes: Routes = [
  {
    path: 'shipping',
    component: ShippingComponent,
  },
  {
    path: 'politics',
    component: PoliticsComponent,
  },
  {
    path: 'rules',
    component: RulesComponent,
  },
  {
    path: 'paying',
    component: PayingComponent,
  },
  {
    path: 'contacts',
    component: ContactsComponent,
  },
  {
    path: 'order-return',
    component: OrderReturnComponent,
  },
  {
    path: 'faq',
    component: FaqComponent,
  },
  {
    path: 'about',
    component: AboutComponent,
  },
  {
    path: 'partners',
    component: PartnersComponent,
  },
  {
    path: 'certificates',
    component: CertificatesComponent,
  }
]

@NgModule({
  declarations: [
    ShippingComponent,
    PoliticsComponent,
    RulesComponent,
    PayingComponent,
    ContactsComponent,
    OrderReturnComponent,
    FaqComponent,
    AboutComponent,
    PartnersComponent,
    CertificatesComponent
  ],
  imports: [
    CommonModule,
    SharedModule,
    RouterModule.forChild(routes)
  ],
  exports: [
    RouterModule
  ]
})
export class InfoModule { }
