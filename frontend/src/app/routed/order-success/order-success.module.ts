import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule } from '@angular/router';
import { OrderSuccessComponent } from './order-success.component';

const routes: Routes = [
  { path: '', component: OrderSuccessComponent }
];

@NgModule({
  declarations: [OrderSuccessComponent],
  imports: [CommonModule, RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrderSuccessModule { }
