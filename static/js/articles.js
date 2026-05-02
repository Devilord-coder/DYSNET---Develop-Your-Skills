// Поиск статей
document.getElementById('searchArticles').addEventListener('input', function (e) {
    const searchTerm = e.target.value.toLowerCase();
    const articles = document.querySelectorAll('.article-card');

    articles.forEach(article => {
        const title = article.dataset.title.toLowerCase();
        if (title.includes(searchTerm)) {
            article.style.display = '';
        } else {
            article.style.display = 'none';
        }
    });
});

// Переход на страницу статьи при клике
document.querySelectorAll('.article-card').forEach(card => {
    card.addEventListener('click', function (e) {
        // Предотвращаем клик по тегам и другим интерактивным элементам
        if (e.target.closest('.tag')) return;
        if (e.target.closest('.page-link')) return;

        const articleId = this.dataset.articleId;
        window.location.href = "{{ url_for('articles.show', article_id=0) }}".replace('0', articleId);
    });
});
