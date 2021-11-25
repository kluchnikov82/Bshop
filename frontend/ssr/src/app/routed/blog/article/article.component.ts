import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { GetDataService } from '../../../services/get-data.service';
import { DomSanitizer, Title, Meta } from '@angular/platform-browser';
import { isNullOrUndefined } from 'util';

@Component({
  selector: 'app-article',
  templateUrl: './article.component.html',
  styleUrls: ['./article.component.scss']
})
export class ArticleComponent implements OnInit {

  private subscription: Subscription;
  public id: string;
  public articleData: any;
  public articleArray: any[];
  public blog: any[];
  public bClist: any[];

  constructor(
    private router: Router,
    private activateRoute: ActivatedRoute,
    private getDataService: GetDataService,
    private sanitizer: DomSanitizer,
    private title: Title,
    private meta: Meta
  ) {
    this.subscription = activateRoute.params.subscribe((params) => {
      this.id = this.activateRoute.snapshot.params['id'];
      this.articleArray = [];
      this.loadData(this.id);
    });
   }

  ngOnInit() {
    this.articleArray = [];
    this.id = this.activateRoute.snapshot.params['id'];
    // this.loadData(this.id);
  }

  loadData(id: string) {
    this.articleArray = [];
    if (!isNullOrUndefined(id)) {
      this.getDataService.getArticleData(id).subscribe((data) => {
        this.articleData = data;
        this.title.setTitle(this.articleData.header + ' | DARI-COSMETICS');
        this.meta.updateTag({ name: 'description', content: this.articleData.teaser });
        if (data) {
          this.bClist = [{
            text: 'Главная',
            link: '/'
          }, {
            text: 'Блог',
            link: '/blog'
          }, {
            text: 'Статья: ' + data.header,
            link: null
          }];
          this.getDataService.getBlog().subscribe((res) => {
            // console.log(res);
            if (res.count > 0) {
              this.blog = res.results;
              for (let art of res.results) {
                if (art.id != id) {
                  this.articleArray.push(art);
                }
              }
            }
          });
        }
      });
    } else {
      this.router.navigate(['']);
    }
  }

  openArticle(id: string) {
    this.router.navigate(['blog/' + id]);
  }

  prevArticle() {
    if (this.blog) {
      if (this.blog.length) {
        let artInd = this.blog.findIndex(item => item.id == this.id);
        if (artInd > -1) {
          if (artInd == 0) {
            this.openArticle(this.blog[this.blog.length - 1].id);
          } else {
            this.openArticle(this.blog[artInd - 1].id);
          }
        } else {
          this.openArticle(this.blog[0].id);
        }
      }
    }
  }

  nextArticle() {
    if (this.blog) {
      if (this.blog.length) {
        let artInd = this.blog.findIndex(item => item.id == this.id);
        if (artInd > -1) {
          if (artInd == (this.blog.length - 1)) {
            this.openArticle(this.blog[0].id);
          } else {
            this.openArticle(this.blog[artInd + 1].id);
          }
        } else {
          this.openArticle(this.blog[0].id);
        }
      }
    }
  }

}
