document.addEventListener('DOMContentLoaded', () => {
    const carousels = document.querySelectorAll('.carousel-container');
    
    carousels.forEach(carousel => {
        const wrapper = carousel.querySelector('.carousel-wrapper');
        const prevButton = carousel.querySelector('.prev');
        const nextButton = carousel.querySelector('.next');

        let offset = 0;
        const itemWidth = 320; // including margin-right of 20px

        nextButton.addEventListener('click', () => {
            offset -= itemWidth;
            if (Math.abs(offset) >= wrapper.scrollWidth) {
                offset = 0; // Reset to start if we go past the end
            }
            wrapper.style.transform = `translateX(${offset}px)`;
        });

        prevButton.addEventListener('click', () => {
            offset += itemWidth;
            if (offset > 0) {
                offset = -(wrapper.scrollWidth - itemWidth); // Jump to the last slide
            }
            wrapper.style.transform = `translateX(${offset}px)`;
        });
    });
});
