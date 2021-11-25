import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatSelectModule, MatIconModule, MatTooltipModule } from '@angular/material';
import { SharedModule } from '../../shared/shared.module';
import { NouisliderModule } from 'ng2-nouislider';
import { PerfectScrollbarModule } from 'ngx-perfect-scrollbar';
import { CatalogComponent } from './catalog.component';
import { ProductComponent } from './product/product.component';
import { IngredientComponent } from './ingredient/ingredient.component';
import { SearchComponent } from './search/search.component';

const routes: Routes = [
  {
    path: '',
    component: CatalogComponent
  },
  {
    path: 'product/:id',
    component: ProductComponent
  },
  {
    path: 'ingredient/:id',
    component: IngredientComponent
  }
]

@NgModule({
  declarations: [
    CatalogComponent,
    ProductComponent,
    IngredientComponent,
    SearchComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    FormsModule,
    NouisliderModule,
    MatSelectModule,
    MatIconModule,
    MatTooltipModule,
    PerfectScrollbarModule,
    SharedModule
  ],
  exports: [
    RouterModule
  ]
})
export class CatalogModule { }
