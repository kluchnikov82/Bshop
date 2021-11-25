import { Component, OnInit } from '@angular/core';
import { GetDataService } from '../services/get-data.service';

@Component({
  selector: 'app-comments',
  templateUrl: './comments.component.html'
})
export class CommentsComponent implements OnInit {

  public comments: any;

  constructor(
    private getDataService: GetDataService
  ) { }

  ngOnInit() {
    this.getDataService.getComments().subscribe((data) => {
      this.comments = data;
      // console.log(this.comments);
    })
  }

  getUserName(comment) {
    if (comment) {
      if (comment.user.last_name) {
        return comment.user.first_name + ' ' + comment.user.last_name;
      } else {
        return '';
      }
    } else {
      return '';
    }
  }

  getCommentImg(comment) {
    if (comment.user.avatar) {
      return comment.user.avatar;
    } else {
      return 'https://dari-cosmetics.ru/assets/otzyvy.jpg';
    }
  }

}
