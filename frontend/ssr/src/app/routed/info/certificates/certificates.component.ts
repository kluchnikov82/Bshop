import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-certificates',
  templateUrl: './certificates.component.html',
  styleUrls: ['./certificates.component.scss']
})
export class CertificatesComponent implements OnInit {

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object
  ) { }

  ngOnInit() {
  }

  openImg(link: string) {
    if (link) {
      if (isPlatformBrowser(this.platformId)) {
        window.open(link, '_blank');
      }
    }
  }

}
