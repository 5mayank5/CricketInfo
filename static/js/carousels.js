document.addEventListener('DOMContentLoaded', function() {
    function setupCarousel(wrapperId, prevButtonId, nextButtonId) {
        const wrapper = document.getElementById(wrapperId);
        const prevButton = document.getElementById(prevButtonId);
        const nextButton = document.getElementById(nextButtonId);
        let scrollAmount = 0;
        const scrollStep = 300; // Adjust this value to match the width of your cards

        prevButton.addEventListener('click', function() {
            scrollAmount -= scrollStep;
            if (scrollAmount < 0) {
                scrollAmount = 0;
            }
            wrapper.style.transform = `translateX(-${scrollAmount}px)`;
        });

        nextButton.addEventListener('click', function() {
            const maxScroll = wrapper.scrollWidth - wrapper.clientWidth;
            scrollAmount += scrollStep;
            if (scrollAmount > maxScroll) {
                scrollAmount = maxScroll;
            }
            wrapper.style.transform = `translateX(-${scrollAmount}px)`;
        });
    }

    setupCarousel('newsCarouselWrapper', 'newsPrev', 'newsNext');
    setupCarousel('videoCarouselWrapper', 'videoPrev', 'videoNext');
}); 