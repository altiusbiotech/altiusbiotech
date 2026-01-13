// Hamburger Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    const navLinksItems = document.querySelectorAll('.nav-links a');

    if (hamburger) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking on a nav link
        navLinksItems.forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Product Image Carousel functionality
    document.querySelectorAll('.product-carousel').forEach(carousel => {
        const items = carousel.querySelectorAll('.carousel-item');
        const prevBtn = carousel.querySelector('.carousel-prev');
        const nextBtn = carousel.querySelector('.carousel-next');
        const indicators = carousel.querySelectorAll('.indicator');
        let currentIndex = 0;

        if (items.length <= 1) return; // Skip if only one image

        function showSlide(index) {
            // Remove active class from all items and indicators
            items.forEach(item => item.classList.remove('active'));
            indicators.forEach(ind => ind.classList.remove('active'));

            // Add active class to current item and indicator
            items[index].classList.add('active');
            indicators[index].classList.add('active');
        }

        function nextSlide() {
            currentIndex = (currentIndex + 1) % items.length;
            showSlide(currentIndex);
        }

        function prevSlide() {
            currentIndex = (currentIndex - 1 + items.length) % items.length;
            showSlide(currentIndex);
        }

        // Button click events
        if (nextBtn) nextBtn.addEventListener('click', nextSlide);
        if (prevBtn) prevBtn.addEventListener('click', prevSlide);

        // Indicator click events
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                currentIndex = index;
                showSlide(currentIndex);
            });
        });

        // Optional: Auto-play (uncomment if you want auto-rotation)
        // setInterval(nextSlide, 4000); // Change image every 4 seconds
    });

    // Learn More button functionality
    document.querySelectorAll('.product-card').forEach(card => {
        const description = card.querySelector('.product-description');
        const learnMoreBtn = card.querySelector('.learn-more-btn');

        if (description && learnMoreBtn) {
            // Check if text is truncated (scrollHeight > clientHeight means text is cut off)
            const isTruncated = description.scrollHeight > description.clientHeight;

            if (!isTruncated) {
                // Hide button if text is not truncated
                learnMoreBtn.classList.add('hidden');
            } else {
                // Add click event to expand/collapse
                learnMoreBtn.addEventListener('click', function(e) {
                    e.preventDefault();

                    if (description.classList.contains('expanded')) {
                        // Collapse
                        description.classList.remove('expanded');
                        this.innerHTML = 'Learn More →';
                    } else {
                        // Expand
                        description.classList.add('expanded');
                        this.innerHTML = 'Show Less ←';
                    }
                });
            }
        }
    });
});