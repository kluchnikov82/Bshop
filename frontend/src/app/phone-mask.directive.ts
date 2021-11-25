import { Directive, HostListener } from '@angular/core';
import { NgControl } from '@angular/forms';

@Directive({
  selector: '[phoneMask]',

})
export class PhoneMaskDirective {

  @HostListener('ngModelChange', ['$event']) onModelChange(event) {
    this.onInputChange(event);
  }

  constructor(
    public model: NgControl
  ) { }

  onInputChange(event) {
    let newValue: string = event;
    let empty: boolean = false;
    newValue = newValue.replace('(', '').replace(')', '');
    if (newValue.length >= 2 && newValue.includes('+7')) {
      newValue = newValue.substring(2).replace(/\D/g, '');
      empty = false;
    } else if (newValue.length > 1 && newValue.startsWith('8')) {
      newValue = newValue.substring(1);
      empty = false;
    } else if (newValue == '+') {
      newValue = '';
      empty = true;
    } else if (newValue == '8') {
      newValue = '';
      empty = false;
    } else if (!newValue) {
      empty = true;
    }

    switch (true) {
      case (newValue.length == 0): newValue = ''; break;
      case (newValue.length > 0 && newValue.length <= 3): newValue = newValue.replace(/^(\d{0,3})/, '($1'); break;
      case (newValue.length > 3 && newValue.length <= 6): newValue = newValue.replace(/^(\d{0,3})(\d{0,3})/, '($1)$2'); break;
      case (newValue.length > 6 && newValue.length <= 8): newValue = newValue.replace(/^(\d{0,3})(\d{0,3})(\d{0,2})/, '($1)$2-$3'); break;
      case (newValue.length > 8 && newValue.length <= 10): newValue = newValue.replace(/^(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/, '($1)$2-$3-$4'); break;
      case (newValue.length > 10): newValue = newValue.substring(0, 10); newValue = newValue.replace(/^(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/, '($1)$2-$3-$4'); break;
    }

    if (newValue) {
      this.model.valueAccessor.writeValue('+7' + newValue);
    } else if (empty) {
      this.model.valueAccessor.writeValue(newValue);
    } else {
      this.model.valueAccessor.writeValue('+7');
    }


  }

}
