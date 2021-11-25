import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription, from } from 'rxjs';
import { GetDataService } from '../../../shared/services/get-data.service';
import { AppDataService } from '../../../shared/services/app-data.service';

@Component({
  selector: 'app-ingredient',
  templateUrl: './ingredient.component.html',
  styleUrls: ['./ingredient.component.scss']
})
export class IngredientComponent implements OnInit {

  public id: string;
  private subscription: Subscription;
  public data: any;

  constructor(
    
    private activateRoute: ActivatedRoute,
    private getDataService: GetDataService,
    private router: Router
  ) { 
    this.subscription = activateRoute.params.subscribe((params) => {
      this.id = params['id'];
    })
  }

  ngOnInit() {
    //console.log(this.id);
    if (this.id) {
      this.getDataService.getComponentInfo(this.id).subscribe((res) => {
        if (res) {
          this.data = res;
          //console.log(this.data);
        }        
      })
    }
  }

  openPage(page: string) {
    this.router.navigate([page]);
  }

  openProduct() {
    // let page = 'catalog';
    // if (AppDataService.currentProduct) {
    //   page = 'product/' + AppDataService.currentProduct.id;
    // }
    // this.openPage(page);
    window.history.back();
  }

}
