import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PopupadviceComponent } from './popupadvice.component';

describe('PopupadviceComponent', () => {
  let component: PopupadviceComponent;
  let fixture: ComponentFixture<PopupadviceComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PopupadviceComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PopupadviceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
