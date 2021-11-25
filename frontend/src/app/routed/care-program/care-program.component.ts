import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import { GetDataService } from './../../shared/services/get-data.service';

interface CareProgram {
  categories: any[];
  formula: string;
  id: string;
  is_available: boolean;
  kit_no: number;
  name: string;
  preferences: any[];
  price: number;
  primary_image: string;
  problem: string;
  target: string;
  usage_period: string;
}

@Component({
  selector: 'app-care-program',
  templateUrl: './care-program.component.html',
  styleUrls: ['./care-program.component.scss']
})
export class CareProgramComponent implements OnInit {

  public programs: CareProgram[];
  public filteredPrograms: CareProgram[];
  public categories: String[];

  constructor(
    private getDataService: GetDataService,
    public sanitizer: DomSanitizer,
    private router: Router
  ) { }

  ngOnInit() {
    this.getData();
  }

  getData() {
    this.programs = [];
    this.categories = [];
    this.getDataService.getAllPrograms(100).subscribe((data) => {
      // console.log(data);
      if (data) {
        if (data.count > 0) {
          this.programs = data.results;
          this.filteredPrograms = data.results;
          for (let prog of this.programs) {
            prog.preferences.sort((i1, i2) => {return i1.seq_no - i2.seq_no});
            if (prog.categories.length) {
              for (let cat of prog.categories) {
                let findCat = this.categories.find(item => item == cat.category_name);
                if (!findCat) {
                  this.categories.push(cat.category_name);
                }
              }
            }
          }
        }
      }
    })
  }

  openProgram(program) {
    if (program) {
      this.router.navigate(['care-program/' + program.id]);
    }
  }

  changeTab(tab: string) {
    this.filteredPrograms = [];
    for (let prog of this.programs) {
      prog.preferences.sort((i1, i2) => {return i1.seq_no - i2.seq_no});
      if (prog.categories.length) {
          let findCat = prog.categories.find(item => item.category_name == tab);
          if (findCat) {
            this.filteredPrograms.push(prog);
          }     
      }
    }
  }

  getBkgImg(program: any) {
    if (program) {
      if (program.primary_image) {
        return this.sanitizer.bypassSecurityTrustStyle('url(' + program.primary_image + ')');
      }else {
        return '';
      }      
    }
  }

  getBkgSize(program: any) {
    if (program) {
      if (program.name == "3D-УВЛАЖНЕНИЕ") {
        return this.sanitizer.bypassSecurityTrustStyle('50% 50%');
      }else {
        return this.sanitizer.bypassSecurityTrustStyle('70% 50%');
      }      
    }
  }

}
