import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { isPlatformBrowser } from '@angular/common';
import { Subscription, from } from 'rxjs';
import { GetDataService } from '../../services/get-data.service';
import { AppDataService } from '../../services/app-data.service';

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
    private router: Router,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {
    this.subscription = activateRoute.params.subscribe((params) => {
      this.id = params['id'];
    });
  }

  ngOnInit() {
    if (this.id) {
      this.getDataService.getComponentInfo(this.id).subscribe((res) => {
        if (res) {
          this.data = res;
        }
      });
    }
  }

  openPage(page: string) {
    this.router.navigate([page]);
  }

  openProduct() {
    if (isPlatformBrowser(this.platformId)) {
      window.history.back();
    }
  }

}
