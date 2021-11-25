import { Component, OnInit } from '@angular/core';
import { GetDataService } from '../../../shared/services/get-data.service';

@Component({
  selector: 'instafeed',
  templateUrl: './instafeed.component.html',
  styleUrls: ['./instafeed.component.scss']
})
export class InstafeedComponent implements OnInit {

  instaFeed: any;
  instaPosts: any[];

  constructor(
    private getDataService: GetDataService
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
      //console.log(this.instaFeed);
    })
  }

  openPost(post) {
    if (post) {
      let link = 'https://instagram.com/p/' + post.node.shortcode;
      window.open(link, '_blank');
    }
  }

}
