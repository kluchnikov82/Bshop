import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from './../shared/shared.module';
import { OrderComponent } from './order.component';
import { EditOrderComponent } from './edit-order/edit-order.component';
import { ConfirmOrderComponent } from './confirm-order/confirm-order.component';
import { PreloaderComponent } from './../preloader/preloader.component';

const routes: Routes = [
  {
    path: 'confirm',
    component: ConfirmOrderComponent,
    pathMatch: 'full'
  },
  {
    path: ':id',
    component: OrderComponent
  },
  {
    path: 'edit/:id',
    pathMatch: 'full',
    component: EditOrderComponent
  },
  {
    path: 'edit',
    pathMatch: 'full',
    redirectTo: ''
  }

];

@NgModule({
  declarations: [
    OrderComponent,
    ConfirmOrderComponent,
    EditOrderComponent,
    PreloaderComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    SharedModule
  ],
  exports: [
    RouterModule
  ]
})
export class OrderModule { }
