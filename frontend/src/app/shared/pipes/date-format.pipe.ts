import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'dateFormat'
})
export class DateFormatPipe implements PipeTransform {

  transform(value: string, type: string = ''): any {
    let d = new Date(value);
    if (d) {
      let day: string;
      day = (d.getDate() < 10)? '0' + d.getDate() : d.getDate().toString();
      let m = d.getMonth();
      let month: string;
      switch (m) {
        case 0: month = ' января '; break;
        case 1: month = ' февраля '; break;
        case 2: month = ' марта '; break;
        case 3: month = ' апреля '; break;
        case 4: month = ' мая '; break;
        case 5: month = ' июня '; break;
        case 6: month = ' июля '; break;
        case 7: month = ' августа '; break;
        case 8: month = ' сентября '; break;
        case 9: month = ' октября '; break;
        case 10: month = ' ноября '; break;
        case 11: month = ' декабря '; break;
      }

      if (type) {
        if (type == 'ddMM') {
          return day + month;
        }
        if (type == 'ddMMYYYY') {
          return day + month + d.getFullYear().toString();
        }
      }else {
        return day + month + d.getFullYear().toString();
      }      
    }else {
      return '';
    }    
  }

}
