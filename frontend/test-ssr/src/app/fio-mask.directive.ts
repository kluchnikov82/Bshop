import { Directive, HostListener } from '@angular/core';
import { NgControl } from '@angular/forms';

@Directive({
  selector: '[fioMask]'
})
export class FioMaskDirective {

  @HostListener('ngModelChange', ['$event']) onModelChange(event) {
    this.fioChange(event);

  }

  constructor(
    public model: NgControl
  ) { }

  fioChange(value: string) {
    let fioArray: string[] = value.split(' ');
    let newArray: string[] = []
    fioArray.forEach(item => {
      newArray.push(item.charAt(0).toUpperCase() + item.substr(1));
    });
    if (newArray.length) {
      this.model.valueAccessor.writeValue(newArray.join(' '));
    }
  }

}
