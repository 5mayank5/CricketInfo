document.addEventListener('DOMContentLoaded', function() {
    // News Carousel
    const newsWrapper = document.getElementById('newsCarouselWrapper');
    const newsPrev = document.getElementById('newsPrev');
    const newsNext = document.getElementById('newsNext');
    let newsPosition = 0;
    const newsCards = document.querySelectorAll('.news-card');
    const newsCardWidth = newsCards.length > 0 ? newsCards[0].offsetWidth + 20 : 0; // Including margin

    if (newsPrev && newsNext) {
        newsPrev.addEventListener('click', () => {
            if (newsPosition < 0) {
                newsPosition += newsCardWidth;
                newsWrapper.style.transform = `translateX(${newsPosition}px)`;
            }
        });

        newsNext.addEventListener('click', () => {
            const maxScroll = -(newsCards.length * newsCardWidth - newsWrapper.parentElement.offsetWidth);
            if (newsPosition > maxScroll) {
                newsPosition -= newsCardWidth;
                newsWrapper.style.transform = `translateX(${newsPosition}px)`;
            }
        });
    }

    // Video Carousel
    const videoWrapper = document.getElementById('videoCarouselWrapper');
    const videoPrev = document.getElementById('videoPrev');
    const videoNext = document.getElementById('videoNext');
    let videoPosition = 0;
    const videoItems = document.querySelectorAll('.carousel-item');
    const videoItemWidth = videoItems.length > 0 ? videoItems[0].offsetWidth + 20 : 0; // Including margin

    if (videoPrev && videoNext) {
        videoPrev.addEventListener('click', () => {
            if (videoPosition < 0) {
                videoPosition += videoItemWidth;
                videoWrapper.style.transform = `translateX(${videoPosition}px)`;
            }
        });

        videoNext.addEventListener('click', () => {
            const maxScroll = -(videoItems.length * videoItemWidth - videoWrapper.parentElement.offsetWidth);
            if (videoPosition > maxScroll) {
                videoPosition -= videoItemWidth;
                videoWrapper.style.transform = `translateX(${videoPosition}px)`;
            }
        });
    }

    // Optional: Auto-play functionality
    function autoPlayCarousels() {
        setInterval(() => {
            // Auto-play news carousel
            const maxNewsScroll = -(newsCards.length * newsCardWidth - newsWrapper.parentElement.offsetWidth);
            if (newsPosition > maxNewsScroll) {
                newsPosition -= newsCardWidth;
            } else {
                newsPosition = 0;
            }
            newsWrapper.style.transform = `translateX(${newsPosition}px)`;

            // Auto-play video carousel
            const maxVideoScroll = -(videoItems.length * videoItemWidth - videoWrapper.parentElement.offsetWidth);
            if (videoPosition > maxVideoScroll) {
                videoPosition -= videoItemWidth;
            } else {
                videoPosition = 0;
            }
            videoWrapper.style.transform = `translateX(${videoPosition}px)`;
        }, 5000); // Change slides every 5 seconds
    }

    // Uncomment the following line if you want auto-play
    // autoPlayCarousels();
}); 