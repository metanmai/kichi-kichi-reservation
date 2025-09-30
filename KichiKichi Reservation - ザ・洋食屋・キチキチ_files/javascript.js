// jQuery
$(function(){
  $('.global-nav_item').hover(function(){
    $(this).find('.global-nav_sub-contents').slideDown(100);
  },function(){
    $(this).find('.global-nav_sub-contents').hide();
  });
  $('.global-lower-nav_item').hover(function(){
    $(this).find('.global-lower-nav_sub-contents').slideDown(100);
  },function(){
    $(this).find('.global-lower-nav_sub-contents').hide();
  });
  $('.modal_sp-menu-item').click(function(){
    if($(this).find('.modal_sp-menu_sub-contents').css('display') == 'none'){
      $(this).find('.modal_sp-menu_sub-contents').slideDown(200);
    }else{
      $(this).find('.modal_sp-menu_sub-contents').slideUp(200);
    }
    
  });
  var $win = $(window),
      $global_nav = $('#global-nav'),
      heroBottom;
  $win.on('scroll',function(){
    heroBottom = $('#first-view').height();
    if($win.scrollTop() > heroBottom){
      $global_nav.addClass('is_header-fixed');
      $('#global-nav_item-img  ').addClass('is_hidden');
      $('#global-nav_item-img2 img ').addClass('is_hidden');
      $('#global-nav_item-access span ').removeClass('is_hidden-access');
    }else{
      $global_nav.removeClass('is_header-fixed');
      $('#global-nav_item-img ').removeClass('is_hidden');
      $('#global-nav_item-img2 img ').removeClass('is_hidden');
      $('#global-nav_item-access span ').addClass('is_hidden-access');
    }
  });

  $win.trigger('scroll');
  var biggestHeight = "0";
    $("#single-entry_title *").each(function(){
        if ($(this).height() > biggestHeight ) {
            biggestHeight = $(this).height()
        }
    });
    $("#single-entry_title").height(biggestHeight);

  $win.scroll(function(){
     $('.fadein-left , .fadein-right').each(function(){
    var elemPos = $(this).offset().top;
     var scroll = $win.scrollTop();
     var windowHeight = $win.height();
     if (scroll > elemPos - windowHeight * 0.6){
         $(this).addClass('scrollin');
      }
     });
   });
  var winScrollTop;
    $('.js-modal-open').each(function(){
        $(this).on('click',function(){
            winScrollTop = $win.scrollTop();
            var target = $(this).data('target');
            var modal = document.getElementById(target);
            $(modal).fadeIn();
            return false;
        });
    });
    $('.js-modal-open-menu').each(function(){
        $(this).on('click',function(){
            winScrollTop = $win.scrollTop();
            var target = $(this).data('target');
            var modal = document.getElementById(target);
            $(modal).fadeIn();
            return false;
        });
    });
    $('.js-modal-close').on('click',function(){
        $('.js-modal').fadeOut();
        $('body,html').stop().animate({scrollTop:winScrollTop}, 100);
        return false;
    }); 
    $('.js-modal-sw').on('click',function(){
      var target = $(this).data('target');
      var dismiss = $(this).data('dismiss');
      var dismissModal = document.getElementById(dismiss);
      var targetModal = document.getElementById(target);
      $(dismissModal).fadeOut();
      $(targetModal).fadeIn();
      return false;
    });
    if (location.hash){
    var target = location.hash;
    console.log(target);  // targetの値は「#sample01」
    $.fancybox.open(target);
  }

  $(document).ready( function(){
    $('#passion-loader').fadeOut();
  });
});

// swiper
var swiper = new Swiper('.swiper-container', {
  effect: 'coverflow',
  speed:600,
  loop: true,
  loopAdditionalSlides: 2,
  // autoplay:3000,
  resistance  :false,
  centeredSlides: true,
  slidesPerView: 3,
  initialSlide: 1,
  // grabCursor: true,
  lazyLoading: true,
  lazyLoadingInPrevNext: true,
  momentumRatio:3,
  noSwipingSelector: 'iframe',
  freeModeMomentumRatio: 100,
  coverflow: {
    rotate: 0,
    stretch: 0,
    depth: 400,
    modifier: 1,
    slideShadows : false,
  },
  pagination: '.swiper-pagination',
  paginationClickable: true,
  breakpoints: {
      767: {
        slidesPerView: 'auto',
        coverflowEffect: {
          rotate: 0,
          stretch: 0,
          depth: 250,
          modifier: 1,
          slideShadows: false,
        },
      },
    },
});
var swiper = new Swiper('.swiper-container_news', {
  effect: 'slide',
  loop: false,
  // centeredSlides: true,
  slidesPerView: 2.7,
  spaceBetween: 50,
  initialSlide: 0,
  keyboardControl: true,
  lazyLoading: true,
  preventClicks: false,
  preventClicksPropagation: false,
  lazyLoadingInPrevNext: true,
  calculateHeight:true,
  freeMode:true,
  touchRatio:.7,
  slideClass:'top-news_slide',
  breakpoints: {
      980: {
        slidesPerView: 1.7,
      },
      500:{
        slidesPerView:1.4,
        spaceBetween: 30,
      }
    }
});
// var swiper = new Swiper('.swiper-container_access', {
//   effect: 'slide',
//   loop: false,
//   centeredSlides: true,
//   slidesPerView: 'auto',
//   spaceBetween: 20,
//   slideClass:'swiper-slide_access',
//   hashNavigation: {
//     watchState: true,
//   },
//   pagination: '.swiper-pagination',
//   paginationClickable: true,
// });
var swiper = new Swiper('.swiper-container_about-us', {
  effect: 'slide',
  speed:800,
  autoplay:3000,
  loop: true,
  loopAdditionalSlides: 1,
  centeredSlides: true,
  slidesPerView: 'auto',
  spaceBetween: 50,
  initialSlide: 0,
  lazyLoading: true,
  lazyLoadingInPrevNext: true,
  calculateHeight:true,
  touchRatio:1,
  navigation: {
      nextEl: '.swiper-button-next', // 次のスライドボタンのセレクタ
      prevEl: '.swiper-button-prev', // 前のスライドボタンのセレクタ
    },
  nextButton: '.swiper-button-next',
  prevButton: '.swiper-button-prev',
  slideClass:'swiper-slide_about-us',
  hashNavigation: {
    watchState: true,
    replaceState:true,
  },
  breakpoints:{
    767:{
      spaceBetween:20,
    }
  }
});
var swiper = new Swiper('.swiper-container_recruit', {
  effect: 'coverflow',
  speed:600,
  loop: true,
  loopAdditionalSlides: 2,
  resistance  :false,
  centeredSlides: true,
  slidesPerView: 3,
  initialSlide: 1,
  grabCursor: true,
  lazyLoading: true,
  pagination: '.swiper-pagination',
  paginationClickable: true,
  lazyLoadingInPrevNext: true,
  momentumRatio:3,
  noSwipingSelector: 'iframe',
  freeModeMomentumRatio: 100,
  coverflow: {
    rotate: 0,
    stretch: 0,
    depth: 400,
    modifier: 1,
    slideShadows : false,
  },
  breakpoints: {
      767: {
        effect:'slide',
        loopAdditionalSlides: 1,
        pagination: false,
        spaceBetween: 10,
        slidesPerView: 1.8,
        coverflow: {
          rotate: 0,
          stretch: 0,
          depth: 0,
          modifier: 1,
          slideShadows : false,
        },
      },
      499:{
        effect:'slide',
        loopAdditionalSlides: 1,
        spaceBetween: 10,
        slidesPerView: 1.3,
        coverflow: {
          rotate: 0,
          stretch: 0,
          depth: 0,
          modifier: 1,
          slideShadows : false,
        },
     },
     374:{
        effect:'slide',
        loopAdditionalSlides: 1,
        spaceBetween: 10,
        slidesPerView: 1.15,
        coverflow: {
          rotate: 0,
          stretch: 0,
          depth: 0,
          modifier: 1,
          slideShadows : false,
        },
      },
    },
});
var swiper = new Swiper('.swiper-container_friends', {
  effect: 'slide',
  speed:800,
  autoplay:5000,
  loop: true,
  centeredSlides: true,
  slidesPerView: 1,
  spaceBetween: 10,
  initialSlide: 0,
  lazyLoading: true,
  lazyLoadingInPrevNext: true,
  calculateHeight:true,
  touchRatio:1,
  navigation: {
      nextEl: '.swiper-button-next', // 次のスライドボタンのセレクタ
      prevEl: '.swiper-button-prev', // 前のスライドボタンのセレクタ
    },
  nextButton: '.swiper-button-next',
  prevButton: '.swiper-button-prev',
  slideClass:'swiper-slide_friends',
  breakpoints:{
    767:{
      // spaceBetween:20,
    },
  },
});
var swiper = new Swiper('.swiper-container_menu', {
  effect: 'slide',
  speed:800,
  autoplay:5000,
  loop: true,
  centeredSlides: true,
  slidesPerView: 1,
  spaceBetween: 10,
  initialSlide: 0,
  lazyLoading: true,
  lazyLoadingInPrevNext: true,
  calculateHeight:true,
  touchRatio:1,
  slideClass:'swiper-slide_menu',
  breakpoints:{
    767:{
      // spaceBetween:20,
    },
  },
});
//google map
var info = {
  name:'ザ・洋食屋・キチキチ',
  lat:35.00727844238281,
  lng: 135.77081298828125,
};
var map;
var marker;
var infoWindow;

function initMap(){
  map = new google.maps.Map(document.getElementById('about-us_map'),{
    center : {
      lat:info.lat,
      lng:info.lng
    },
    zoom:16
  });
  marker = new google.maps.Marker({
    position:{
      lat:info.lat,
      lng:info.lng
    },
    map:map,
    icon:{
    }
  });
  infoWindow = new google.maps.InfoWindow({
    content:'<p><a href="https://www.google.co.jp/maps/place/%E3%82%B6%E3%83%BB%E6%B4%8B%E9%A3%9F%E5%B1%8B+%E3%82%AD%E3%83%81%E3%82%AD%E3%83%81/@35.0072788,135.7686168,17z/data=!3m1!4b1!4m5!3m4!1s0x60010894b20b41dd:0x98dd4445067a93b4!8m2!3d35.0072788!4d135.7708108?hl=ja">ザ・洋食屋・キチキチ</a></p>'
  });
  marker.addListener('click',function(){
    infoWindow.open(map,marker);
  });
}