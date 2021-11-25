import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { SharedModule } from './../shared/shared.module';
import { BlogComponent } from './blog.component';
import { ArticleComponent } from './article/article.component';

const routes: Routes = [
  {
    path: '',
    component: BlogComponent,
    pathMatch: 'full'
  },
  {
    path: ':id',
    component: ArticleComponent
  }
]

@NgModule({
  declarations: [
    ArticleComponent,
    BlogComponent
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
export class BlogModule { }
