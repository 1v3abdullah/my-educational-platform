const elements = document.querySelectorAll('.fade-element');

const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('start-animation');
      observer.unobserve(entry.target); // تشغيل الأنميشن مرة واحدة فقط
    }
  });
});

elements.forEach(el => observer.observe(el));
