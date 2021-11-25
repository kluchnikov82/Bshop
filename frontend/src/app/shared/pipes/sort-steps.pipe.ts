import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'sortSteps'
})
export class SortStepsPipe implements PipeTransform {

  transform(value: any[], field: string): any {
    return value.sort((i1, i2) => {return i1[field] - i2[field]});
  }

}
