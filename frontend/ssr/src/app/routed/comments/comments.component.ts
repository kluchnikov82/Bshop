import { Component, OnInit } from '@angular/core';
import { GetDataService } from '../../services/get-data.service';

@Component({
  selector: 'app-comments',
  templateUrl: './comments.component.html',
  styleUrls: ['./comments.component.scss']
})
export class CommentsComponent implements OnInit {

  public comments: any;
  public showBtnMore = true;
  pageIndex = 0;
  pageSize = 10;

  constructor(
    private getDataService: GetDataService
  ) { }

  ngOnInit() {
    this.pageIndex = 0;
    this.comments = [];
    this.getComments();
  }

  getComments() {
    this.getDataService.getAllComments(this.pageSize, this.pageIndex * this.pageSize).subscribe((data) => {
      this.comments = [...this.comments, ...data.results];
      if (data.count < this.pageSize * (this.pageIndex + 1)) {
        this.showBtnMore = false;
      }
    });
  }

  showMore() {
    this.pageIndex++;
    this.getComments();
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
