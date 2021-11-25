import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { GetDataService } from '../services/get-data.service';

@Component({
  selector: 'instafeed',
  templateUrl: './instafeed.component.html',
  styleUrls: ['./instafeed.component.scss']
})
export class InstafeedComponent implements OnInit {

  instaFeed: any;
  instaPosts: any[];

  constructor(
    private getDataService: GetDataService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) { }

  ngOnInit() {
    this.getDataService.getInstaFeed().subscribe((res) => {
      this.instaFeed = res;
      if (res.graphql){
        if (res.graphql.user) {
          if (res.graphql.user.edge_owner_to_timeline_media) {
            let timeline = res.graphql.user.edge_owner_to_timeline_media;
            if (timeline.count) {
              this.instaPosts = timeline.edges.slice(0,5);
              // console.log(this.instaPosts);
            }
          }
        }
      }
      // console.log(this.instaFeed);
    });
  }

  openPost(post) {
    if (post) {
      let link = 'https://instagram.com/p/' + post.node.shortcode;
      if (isPlatformBrowser) {
        window.open(link, '_blank');
      }
    }
  }

}
