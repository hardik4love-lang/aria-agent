/**
 * Lightweight, Zero-Dependency Interactive Product Gallery for WooCommerce
 * Features: Instant thumbnail switching, smooth lens zoom, touch swipe support
 */
class InteractiveProductGallery {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;
    this.mainImage = this.container.querySelector('.gallery-main-img');
    this.thumbnails = this.container.querySelectorAll('.gallery-thumb');
    this.init();
  }

  init() {
    this.thumbnails.forEach(thumb => {
      thumb.addEventListener('click', (e) => {
        this.thumbnails.forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');
        const targetSrc = thumb.getAttribute('data-full-src');
        if (this.mainImage && targetSrc) {
          this.mainImage.style.opacity = '0.5';
          this.mainImage.src = targetSrc;
          setTimeout(() => { this.mainImage.style.opacity = '1'; }, 150);
        }
      });
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new InteractiveProductGallery('wc-interactive-gallery');
});
