// JavaScript для страницы контактов
document.addEventListener('DOMContentLoaded', function () {
    // Инициализация FAQ
    initFaq();

    // Инициализация формы
    initContactForm();
});

// FAQ аккордеон
function initFaq() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            // Закрыть другие
            faqItems.forEach(other => {
                if (other !== item && other.classList.contains('active')) {
                    other.classList.remove('active');
                }
            });

            // Открыть/закрыть текущий
            item.classList.toggle('active');
        });
    });
}

// Форма обратной связи
function initContactForm() {
    const form = document.getElementById('contactForm');
    const messageDiv = document.getElementById('formMessage');

    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        // Собрать данные формы
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            subject: document.getElementById('subject').value,
            message: document.getElementById('message').value,
            agree: document.getElementById('agree').checked
        };

        // Валидация
        if (!formData.name || !formData.email || !formData.subject || !formData.message) {
            showMessage('Пожалуйста, заполните все обязательные поля', 'error');
            return;
        }

        if (!formData.agree) {
            showMessage('Пожалуйста, согласитесь на обработку персональных данных', 'error');
            return;
        }

        if (!validateEmail(formData.email)) {
            showMessage('Пожалуйста, введите корректный email', 'error');
            return;
        }

        // Показать загрузку
        const submitBtn = form.querySelector('.submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отправка...';
        submitBtn.disabled = true;

        try {
            // Отправка данных на сервер
            const response = await fetch('/api/contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('Сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.', 'success');
                form.reset();
            } else {
                showMessage(result.error || 'Ошибка при отправке. Попробуйте позже.', 'error');
            }
        } catch (error) {
            console.error('Ошибка:', error);
            showMessage('Ошибка соединения. Проверьте интернет и попробуйте снова.', 'error');
        } finally {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

// Валидация email
function validateEmail(email) {
    const re = /^[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}$/;
    return re.test(email);
}

// Показать сообщение
function showMessage(text, type) {
    const messageDiv = document.getElementById('formMessage');
    messageDiv.textContent = text;
    messageDiv.className = `form-message ${type}`;

    setTimeout(() => {
        messageDiv.style.display = 'none';
        messageDiv.className = 'form-message';
    }, 5000);
}

// Получить CSRF токен (для Flask-WTF)
function getCsrfToken() {
    const token = document.querySelector('input[name="csrf_token"]');
    return token ? token.value : '';
}

// Анимация при скролле
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Применяем анимацию к карточкам
document.querySelectorAll('.info-card, .social-card, .form-card, .map-card, .faq-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'all 0.6s ease';
    observer.observe(card);
});

// Маска для телефона (опционально)
document.getElementById('phone')?.addEventListener('input', function (e) {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 11) value = value.slice(0, 11);

    let formatted = '';
    if (value.length > 0) formatted = '+7';
    if (value.length > 1) formatted += ` (${value.slice(1, 4)}`;
    if (value.length > 4) formatted += `) ${value.slice(4, 7)}`;
    if (value.length > 7) formatted += `-${value.slice(7, 9)}`;
    if (value.length > 9) formatted += `-${value.slice(9, 11)}`;

    e.target.value = formatted;
});