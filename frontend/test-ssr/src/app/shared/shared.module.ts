import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule,
  MatExpansionModule,
  MatBadgeModule,
  MatTabsModule,
  MatInputModule,
  MatAutocompleteModule,
  MatSelectModule,
  MatMenuModule,
  MatDialogModule,
  MatButtonModule,
  MatSnackBarModule,
  MatTooltipModule,
  MatDatepickerModule,
  MatNativeDateModule,
  MatToolbarModule,
  MAT_DATE_LOCALE } from '@angular/material';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { PerfectScrollbarModule } from 'ngx-perfect-scrollbar';
import { BreadcrumbsComponent } from './../breadcrumbs/breadcrumbs.component';
import { CopyClipboardDirective } from './../copy-clipboard.directive';
import { PhoneMaskDirective } from './../phone-mask.directive';
import { FioMaskDirective } from './../fio-mask.directive';
import { InitialsPipe } from './../pipes/initials.pipe';
import { DateFormatPipe } from './../pipes/date-format.pipe';
import { SortStepsPipe } from './../pipes/sort-steps.pipe';

@NgModule({
  declarations: [
    BreadcrumbsComponent,
    CopyClipboardDirective,
    PhoneMaskDirective,
    FioMaskDirective,
    InitialsPipe,
    DateFormatPipe,
    SortStepsPipe
  ],
  imports: [
    CommonModule,
    MatIconModule,
    MatExpansionModule,
    MatBadgeModule,
    MatTabsModule,
    MatInputModule,
    MatAutocompleteModule,
    MatSelectModule,
    MatMenuModule,
    MatDialogModule,
    MatButtonModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatToolbarModule,
    FormsModule,
    ReactiveFormsModule,
    PerfectScrollbarModule,
  ],
  exports: [
    MatIconModule,
    MatExpansionModule,
    MatBadgeModule,
    MatTabsModule,
    MatInputModule,
    MatAutocompleteModule,
    MatSelectModule,
    MatMenuModule,
    MatDialogModule,
    MatButtonModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatToolbarModule,
    FormsModule,
    ReactiveFormsModule,
    PerfectScrollbarModule,
    BreadcrumbsComponent,
    InitialsPipe,
    DateFormatPipe,
    SortStepsPipe,
    PhoneMaskDirective,
    FioMaskDirective,
    CopyClipboardDirective
  ],
  providers: [
    {
      provide: MAT_DATE_LOCALE,
      useValue: 'ru-RU'
    }
  ]
})
export class SharedModule { }
