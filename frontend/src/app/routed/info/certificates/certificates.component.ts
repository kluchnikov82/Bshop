import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-certificates',
  templateUrl: './certificates.component.html',
  styleUrls: ['./certificates.component.scss']
})
export class CertificatesComponent implements OnInit {

  constructor() { }

  ngOnInit() {
  }

  openImg(link: string) {
    if (link) {
      window.open(link, '_blank');
    }
  }

}
