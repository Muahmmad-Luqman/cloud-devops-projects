document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const target = document.querySelector(link.getAttribute('href'));
    if (target) {
      event.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

const status = document.querySelector('#status');
if (status) {
  status.textContent = `Delivered securely through AWS • ${new Date().getFullYear()}`;
}

