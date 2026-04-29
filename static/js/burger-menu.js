// Бургер-меню функционал
(function () {
    function initBurgerMenu() {
        const burgerBtn = document.getElementById('burgerMenu');
        const mobileMenu = document.getElementById('mobileMenu');
        const overlay = document.getElementById('mobileMenuOverlay');
        const authWrapper = document.getElementById('authButtonsWrapper');
        const mobileAuth = document.getElementById('mobileAuthButtons');

        if (!burgerBtn || !mobileMenu || !overlay) return;

        // Копируем кнопки авторизации в мобильное меню
        if (authWrapper && mobileAuth) {
            mobileAuth.innerHTML = authWrapper.innerHTML;
        }

        // Функция открытия/закрытия
        function toggleMenu() {
            burgerBtn.classList.toggle('active');
            mobileMenu.classList.toggle('active');
            overlay.classList.toggle('active');

            if (mobileMenu.classList.contains('active')) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        }

        function closeMenu() {
            burgerBtn.classList.remove('active');
            mobileMenu.classList.remove('active');
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }

        burgerBtn.addEventListener('click', toggleMenu);
        overlay.addEventListener('click', closeMenu);

        // Закрытие при клике на ссылки
        const allLinks = mobileMenu.querySelectorAll('a');
        allLinks.forEach(link => {
            link.addEventListener('click', closeMenu);
        });

        // Закрытие при ресайзе
        window.addEventListener('resize', function () {
            if (window.innerWidth > 768 && mobileMenu.classList.contains('active')) {
                closeMenu();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', initBurgerMenu);
})();