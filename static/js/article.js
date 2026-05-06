// JavaScript для страницы статьи (обработка AJAX для лайков и комментариев)

document.addEventListener('DOMContentLoaded', function () {
    // Обработка лайков через AJAX
    const likeForm = document.getElementById('likeForm');
    if (likeForm) {
        likeForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const form = e.target;
            const url = form.action;
            const likeButton = document.getElementById('likeButton');
            const likesSpan = document.getElementById('likesValue');
            const likeText = document.getElementById('likeText');

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                });

                const data = await response.json();

                if (data.success) {
                    // Обновляем UI
                    likesSpan.textContent = data.likes_count;

                    if (data.liked) {
                        likeButton.classList.add('liked');
                        likeText.textContent = 'Лайкнут';
                    } else {
                        likeButton.classList.remove('liked');
                        likeText.textContent = 'Нравится';
                    }
                }
            } catch (error) {
                console.error('Ошибка при лайке:', error);
                // Если AJAX не работает, отправляем форму обычным способом
                window.location.href = url;
            }
        });
    }

    // Обработка комментариев через AJAX
    const commentForm = document.getElementById('commentForm');
    if (commentForm) {
        commentForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const form = e.target;
            const url = form.action;
            const formData = new FormData(form);
            const commentText = formData.get('comment_text');
            const commentsList = document.getElementById('commentsList');
            const commentsCountSpan = document.getElementById('commentsCount');

            if (!commentText.trim()) {
                showFlashMessage('Введите текст комментария', 'error');
                return;
            }

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ comment_text: commentText })
                });

                const data = await response.json();

                if (data.success) {
                    // Добавляем новый комментарий в список
                    const newComment = data.comment;
                    const commentHtml = `
                        <div class="comment-item" data-comment-id="${newComment.id}">
                            <div class="comment-author">
                                <i class="fas fa-user-circle"></i>
                                ${escapeHtml(newComment.author_name)}
                                <span class="comment-date">${newComment.created_date}</span>
                            </div>
                            <div class="comment-text">${escapeHtml(newComment.text)}</div>
                        </div>
                    `;

                    // Удаляем заглушку "нет комментариев" если она есть
                    const noComments = commentsList.querySelector('.no-comments');
                    if (noComments) {
                        commentsList.innerHTML = '';
                    }

                    commentsList.insertAdjacentHTML('beforeend', commentHtml);

                    // Обновляем счетчик
                    commentsCountSpan.textContent = data.total_comments;

                    // Очищаем форму
                    form.reset();

                    // Прокручиваем к новому комментарию
                    const newCommentEl = commentsList.lastElementChild;
                    if (newCommentEl) {
                        newCommentEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }

                    showFlashMessage('Комментарий добавлен!', 'success');
                } else {
                    showFlashMessage(data.error || 'Ошибка при добавлении комментария', 'error');
                }
            } catch (error) {
                console.error('Ошибка при отправке комментария:', error);
                // Отправляем форму обычным способом
                window.location.href = url + '?comment=' + encodeURIComponent(commentText);
            }
        });
    }
});

// Функция экранирования HTML
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Показ flash сообщений
function showFlashMessage(message, type) {
    // Удаляем старые сообщения
    const oldMessages = document.querySelectorAll('.flash-message');
    oldMessages.forEach(msg => msg.remove());

    const container = document.querySelector('.article-container');
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash-message ${type}`;
    flashDiv.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i> ${escapeHtml(message)}`;

    container.insertBefore(flashDiv, container.firstChild);

    setTimeout(() => {
        flashDiv.style.opacity = '0';
        setTimeout(() => flashDiv.remove(), 300);
    }, 3000);
}