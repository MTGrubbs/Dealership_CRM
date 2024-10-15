document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarLinks = document.querySelector('.navbar-links');

    navbarToggle.addEventListener('click', function() {
        navbarLinks.classList.toggle('active');
        navbarToggle.classList.toggle('active');
    });
});