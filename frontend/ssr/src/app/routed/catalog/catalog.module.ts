import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatSelectModule, MatIconModule, MatTooltipModule } from '@angular/material';
import { SharedModule } from '../../shared/shared.module';
import { NouisliderModule } from 'ng2-nouislider';
// import { PerfectScrollbarModule } from 'ngx-perfect-scrollbar';
import { CatalogComponent } from './catalog.component';
import { ProductComponent } from './product/product.component';
import { SearchComponent } from './search/search.component';
import { IngredientComponent } from './ingredient/ingredient.component';

const routes: Routes = [
  {
    path: '',
    component: CatalogComponent
  },
  {
    path: 'search/:query',
    component: SearchComponent,
    pathMatch: 'full'
  },
  {
    path: 'ingredient/:id',
    component: IngredientComponent,
    pathMatch: 'full'
  },
  {
    path: ':category',
    component: CatalogComponent
  },
  {
    path: ':category/:subcategory',
    component: CatalogComponent
  },
  {
    path: ':category/:subcategory/:id',
    component: ProductComponent
  }
];

@NgModule({
  declarations: [
    CatalogComponent,
    ProductComponent,
    SearchComponent,
    IngredientComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    FormsModule,
    NouisliderModule,
    MatSelectModule,
    MatIconModule,
    MatTooltipModule,
    // PerfectScrollbarModule,
    SharedModule
  ],
  exports: [
    RouterModule
  ]
})
export class CatalogModule { }
