

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

$(function () {

    $(".js-modal-open").on('click', function () {
        var swiper = new Swiper('.swiper-container_access', {
          effect: 'slide',
          loop: false,
          centeredSlides: false,
          slidesPerView: 'auto',
          spaceBetween: 20,
          slideClass:'swiper-slide_access',
          direction:'vertical',
          hashNavigation: {
            watchState: true,
          },
          pagination: '.swiper-pagination',
          paginationClickable: true,
          breakpoints: {
            767: {
              direction:'horizontal',
              centeredSlides: true,
            },
          },
        });

    });

    $(".js-modal-open-menu").on('click', function () {
        var swiper = new Swiper('.swiper-container_modal-menu', {
          effect: 'slide',
          loop: false,
          speed:1000,
          centeredSlides: true,
          slidesPerView: 'auto',
          spaceBetween: 20,
          slideClass:'swiper-slide_modal-menu',
          direction:'horizontal',
          hashNavigation: {
            watchState: true,
          },
          pagination: '.swiper-pagination',
          paginationClickable: true,
          nextButton: '.swiper-button-next',
          prevButton: '.swiper-button-prev',
          navigation: {
            nextEl: '.swiper-button-next', // 次のスライドボタンのセレクタ
            prevEl: '.swiper-button-prev', // 前のスライドボタンのセレクタ
          },
        });
        var id = $(this).data('id');
        location.href = '#'+id ;
    });


});


