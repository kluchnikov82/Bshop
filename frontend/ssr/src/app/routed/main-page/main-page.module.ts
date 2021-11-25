import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from '../../shared/shared.module';
import { MainPageComponent } from './main-page.component';
import { InstafeedComponent } from './instafeed/instafeed.component';

const routes: Routes = [
  {
    path: '',
    component: MainPageComponent,
    // data: { preload: true }
  },
  {
    path: 'ref/:id',
    component: MainPageComponent,
    // data: { preload: true }
  }
];

@NgModule({
  declarations: [
    MainPageComponent,
    InstafeedComponent,
    // InitialsPipe
  ],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule.forChild(routes),
    // MatFormFieldModule,
    // MatIconModule,
    // MatTabsModule,
    // MatInputModule,
    // MatAutocompleteModule,
    // MatSelectModule,
    // MatMenuModule,
    // MatDialogModule,
    // MatButtonModule,
    SharedModule
  ],
  entryComponents: [
    InstafeedComponent,
    // MainPageComponent
  ],
  exports: [
    RouterModule
  ],
  // providers: [
  //   GetDataService
  // ]
})
export class MainPageModule { }
