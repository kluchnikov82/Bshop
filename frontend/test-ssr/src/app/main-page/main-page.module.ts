import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Routes, RouterModule, PreloadAllModules } from '@angular/router';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SharedModule } from './../shared/shared.module';
// import { InitialsPipe } from './../pipes/initials.pipe';
// import { GetDataService } from './../services/get-data.service';

// import {MatFormFieldModule,
//         MatIconModule,
//         MatTabsModule, 
//         MatInputModule,
//         MatAutocompleteModule,
//         MatSelectModule,
//         MatMenuModule,
//         MatDialogModule,
//         MatButtonModule } from '@angular/material';

// import { CareProgramComponent } from './../care-program/care-program.component';
// import { AccountComponent } from './../account/account.component';
// import { FeedbackComponent } from './../feedback/feedback.component';
import { SliderComponent } from './slider/slider.component';
import { MainPageComponent } from './../main-page/main-page.component';
import { InstafeedComponent } from './../instafeed/instafeed.component';

const routes: Routes = [
  {
    path: '',
    component: MainPageComponent,
    //data: { preload: true }
  },
  {
    path: 'ref/:id',
    component: MainPageComponent,
    //data: { preload: true }
  }
]

@NgModule({
  declarations: [
    MainPageComponent,
    InstafeedComponent,
    SliderComponent
    //InitialsPipe
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
    SliderComponent
    //MainPageComponent
  ],
  exports: [
    RouterModule
  ],
  // providers: [
  //   GetDataService
  // ]
})
export class MainPageModule { }
