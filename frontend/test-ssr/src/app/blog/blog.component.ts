import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { GetDataService } from './../services/get-data.service';

interface ArticleCategory {
  name: String;
  subcats: String[];
  active?: boolean;
}

@Component({
  selector: 'app-blog',
  templateUrl: './blog.component.html',
  styleUrls: ['./blog.component.scss']
})

export class BlogComponent implements OnInit {

  public bClist: any[];
  public blog: any[];
  private oldBlog: any[];
  public categories: ArticleCategory[];
  public pages = ['1','2','3'];
  public selectedFilter: any;
  public filterTypes = [
    {value: 'views', viewValue: 'По популярности'},
    {value: 'date', viewValue: 'По дате'}
  ];

  constructor(
    private getDataService: GetDataService,
    private router: Router
  ) { }

  ngOnInit() {
    this.blog = [];
    this.oldBlog = [];
    this.categories = [];
    this.selectedFilter = 'views';
    this.bClist = [{
      text: 'Главная',
      link: '/'
    },{
      text: 'Блог',
      link: null
    }]
    this.getDataService.getBlog().subscribe((data) => {
      //console.log(data);
      if (data.count > 0) {
        data.results.sort((a, b) => { return (b.hit_count - a.hit_count)});
        this.blog = data.results;
        this.oldBlog = data.results;
        for (let article of this.blog) {
          if (article.categories.length) {
            for (let cat of article.categories) {
              let findCat = this.categories.find(item => item.name == cat.category_name);
              if (!findCat) {
                this.categories.push({
                  name: cat.category_name,
                  subcats: article.subcategories.map(item => item = item.subcategory_name),
                  active: false
                })
              }else {
                for (let subcat of article.subcategories) {
                  let findSubcat = findCat.subcats.find(item => item == subcat.subcategory_name);
                  if (!findSubcat) {
                    findCat.subcats.push(subcat.subcategory_name);
                  }
                }
              }
            }
          }
        }
        //console.log(this.categories);
      }
    })

  }

  openArticle(id: string) {
    this.router.navigate(['blog/' + id]);
  }

  filterArticles(subcat: any) {
    if (subcat) {
      this.blog = [];
      for (let art of this.oldBlog) {
        if (art.subcategories) {
          for (let sub of art.subcategories) {
            if (sub.subcategory_name == subcat) {
              this.blog.push(art);
            }
          }
        }
      }
    }
  }

  sortArticles() {
    if (this.selectedFilter) {
      if (this.selectedFilter == 'views') {
        this.blog.sort((a, b) => { return (b.hit_count - a.hit_count)});
      }else {
        this.blog.sort((a, b) => { 
          let dateA = new Date(a.created);
          let dateB = new Date(b.created);
          return ( +dateB - +dateA );
        })
      }
    }
  }

  toggleActiveCategory(category: ArticleCategory) {
    // for (let cat of this.categories) {
    //   if (cat == category) {
    //     cat.active = !cat.active;
    //   }else {
    //     cat.active = false;
    //   }
    // }
  }

}
