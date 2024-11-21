document.addEventListener('DOMContentLoaded', () => {
    const newsCarouselWrapper = document.querySelector('.news-carousel-wrapper');
    const newsPrevButton = document.querySelector('.carousel-button-prev');
    const newsNextButton = document.querySelector('.carousel-button-next');

    let newsOffset = 0;
    const newsItemWidth = 330; // Card width + margin

    newsNextButton.addEventListener('click', () => {
        newsOffset -= newsItemWidth;
        if (Math.abs(newsOffset) >= newsCarouselWrapper.scrollWidth) {
            newsOffset = 0;
        }
        newsCarouselWrapper.style.transform = `translateX(${newsOffset}px)`;
    });

    newsPrevButton.addEventListener('click', () => {
        newsOffset += newsItemWidth;
        if (newsOffset > 0) {
            newsOffset = -(newsCarouselWrapper.scrollWidth - newsItemWidth);
        }
        newsCarouselWrapper.style.transform = `translateX(${newsOffset}px)`;
    });

    const videoCarouselWrapper = document.querySelector('.carousel-wrapper');
    const videoPrevButton = document.querySelector('.prev');
    const videoNextButton = document.querySelector('.next');

    let videoOffset = 0;
    const videoItemWidth = 340;

    videoNextButton.addEventListener('click', () => {
        videoOffset -= videoItemWidth;
        if (Math.abs(videoOffset) >= videoCarouselWrapper.scrollWidth) {
            videoOffset = 0;
        }
        videoCarouselWrapper.style.transform = `translateX(${videoOffset}px)`;
    });

    videoPrevButton.addEventListener('click', () => {
        videoOffset += videoItemWidth;
        if (videoOffset > 0) {
            videoOffset = -(videoCarouselWrapper.scrollWidth - videoItemWidth);
        }
        videoCarouselWrapper.style.transform = `translateX(${videoOffset}px)`;
    });
});
