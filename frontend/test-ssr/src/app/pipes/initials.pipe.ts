import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'initials'
})
export class InitialsPipe implements PipeTransform {

  transform(fullname: string): any {
    let arrayName = fullname.split(' ');
    let surname = arrayName[0];
    let firstName = arrayName[1];
    let middleName = arrayName[2];
    if (firstName) {
      firstName = firstName.substr(0,1) + '.';
    }else {
      firstName = '';
    }
    if (middleName) {
      middleName = middleName.substr(0,1) + '.';
    }else {
      middleName = '';
    }
    return surname + ' ' + firstName + ' ' + middleName;
  }

}
