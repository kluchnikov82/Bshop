import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from './../shared/shared.module';
import { CareProgramComponent } from './care-program.component';
import { CareProgramItemComponent } from './care-program-item/care-program-item.component';

const routes: Routes = [
  {
    path: '',
    component: CareProgramComponent,
    pathMatch: 'full'
  },
  {
    path: ':id',
    component: CareProgramItemComponent
  }
]

@NgModule({
  declarations: [
    CareProgramComponent,
    CareProgramItemComponent
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
export class CareProgramModule { }
