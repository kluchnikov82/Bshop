import { Component, OnInit, Input, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { SwiperOptions } from 'swiper';
// import { SwiperComponent } from 'angular2-useful-swiper';

@Component({
  selector: 'slider',
  templateUrl: './slider.component.html',
  styleUrls: ['./slider.component.scss']
})
export class SliderComponent implements OnInit, AfterViewInit {

  @Input() sliderConfig: any;
  public swiperConfig: SwiperOptions;
  public arraySlides: any[];
  public isBrowser: boolean;
  public activeView: boolean;
  scrollLeft = 0;
  @ViewChild('slider') swSlider: ElementRef;

  constructor( ) { }

  ngOnInit() {
    this.activeView = false;
    if (this.sliderConfig) {
      this.arraySlides = this.sliderConfig.slides;
      let slidesPerView = 3;

      // if (screen.width < 801) {
      //   slidesPerView = 1;
      // }

      this.swiperConfig = {
        autoplay: true,
        // initialSlide: 0,
        allowTouchMove: true,
        loop: true,
        effect: 'slide',
        speed: 700,
        // centeredSlidesBounds: true,
        roundLengths: true,
        spaceBetween: 42,
        centeredSlides: true,
        slidesPerView: 'auto',
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev'
        },
      };

    }
  }

  ngAfterViewInit() {
    this.activeView = true;
  }

  nextSlide() {
    this.scrollLeft += 260;
    let maxScroll = (this.arraySlides.length * 260) - this.swSlider.nativeElement.clientWidth + (this.arraySlides.length * 40);
    if (this.scrollLeft > maxScroll) {
      this.scrollLeft = maxScroll;
    }
    this.swSlider.nativeElement.scrollTo({ left: this.scrollLeft, top: 0, behavior: 'smooth' });
    // this.swSlider;
  }

  prevSlide() {
    this.scrollLeft -= 260;
    if (this.scrollLeft < 0) {
      this.scrollLeft = 0;
    }
    this.swSlider.nativeElement.scrollTo({ left: this.scrollLeft, top: 0, behavior: 'smooth' });
  }

}
