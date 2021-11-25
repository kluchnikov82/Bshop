import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CareProgramComponent } from './care-program.component';

describe('CareProgramComponent', () => {
  let component: CareProgramComponent;
  let fixture: ComponentFixture<CareProgramComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CareProgramComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CareProgramComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
