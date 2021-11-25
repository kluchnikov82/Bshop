import { Component, OnInit, Input } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'breadcrumbs',
  templateUrl: './breadcrumbs.component.html',
  styleUrls: ['./breadcrumbs.component.scss']
})
export class BreadcrumbsComponent implements OnInit {

  @Input() list: any[];

  constructor(
    private router: Router
  ) { }

  ngOnInit() {
  }

  openPage(page) {
    if (page) {
      if (page.link) {
        this.router.navigate([page.link]);
      }
    }
  }

}
