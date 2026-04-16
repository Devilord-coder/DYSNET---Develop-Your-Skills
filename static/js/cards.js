let currentTopic = 'Случайные слова из разных категорий';
let currentDirection = 'russian';

// Загрузка первой порции слов при старте
document.addEventListener('DOMContentLoaded', () => {
    loadNewBatch();
    setupEventListeners();
});

// Настройка обработчиков событий
function setupEventListeners() {
    document.getElementById('checkAnswerBtn').addEventListener('click', checkAnswer);
    document.getElementById('revealAnswerBtn').addEventListener('click', revealAnswer);
    
    document.getElementById('topicSelect').addEventListener('change', (e) => {
        currentTopic = e.target.value;
        loadNewBatch();
    });
    
    document.getElementById('languageSelect').addEventListener('change', async (e) => {
        currentDirection = e.target.value;
        
        // Отправляем новое направление на сервер
        await updateLanguage();
    });
    
    document.getElementById('answerInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') checkAnswer();
    });
}

// Обновление языка
async function updateLanguage() {
    try {
        const response = await fetch('/cards/current', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ direction: currentDirection })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayWord(data.current_word);
        } else if (data.empty) {
            loadNewBatch();
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Загрузка новой порции слов
async function loadNewBatch() {
    try {
        document.getElementById('word-display').textContent = 'Загрузка...';
        document.getElementById('checkAnswerBtn').disabled = true;
        
        const response = await fetch('/cards/next', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                topic: currentTopic,
                direction: currentDirection 
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('checkAnswerBtn').disabled = false;
            displayWord(data.current_word);
        } else {
            throw new Error('Ошибка загрузки');
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('word-display').textContent = 'Ошибка загрузки слов';
        alert('Не удалось загрузить слова. Попробуйте еще раз.');
    }
}

// Получение текущего слова (при смене языка)
async function getCurrentWord() {
    try {
        const response = await fetch('/cards/current', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayWord(data.current_word);
        } else if (data.empty) {
            loadNewBatch();
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

// Отображение слова на карточке
function displayWord(word) {
    document.getElementById('word-display').textContent = word;
    document.getElementById('answerInput').value = '';
    document.getElementById('answerFeedback').innerHTML = '';
    document.getElementById('translation-display').style.display = 'none';
    
    const input = document.getElementById('answerInput');
    input.style.borderColor = '';
    input.style.backgroundColor = '';
    input.focus();
    
    if (currentDirection === 'russian') {
        input.placeholder = 'Введите перевод на английский...';
    } else {
        input.placeholder = 'Введите перевод на русский...';
    }
}

// Проверка ответа
async function checkAnswer() {
    const answer = document.getElementById('answerInput').value.trim();
    const feedbackDiv = document.getElementById('answerFeedback');
    
    if (!answer) {
        feedbackDiv.innerHTML = '<div class="feedback-warning">⚠️ Введите перевод слова!</div>';
        return;
    }
    
    const checkBtn = document.getElementById('checkAnswerBtn');
    checkBtn.disabled = true;
    checkBtn.textContent = 'Проверка...';
    
    try {
        const response = await fetch('/cards/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                answer: answer,
                direction: currentDirection
            })
        });
        
        const data = await response.json();
        
        if (data.is_correct) {
            feedbackDiv.innerHTML = '<div class="feedback-correct">Правильно!</div>';
            showTranslation(data.correct_answer);
            
            setTimeout(() => {
                if (data.finished) {
                    loadNewBatch();
                } else {
                    displayWord(data.next_word);
                }
                checkBtn.disabled = false;
                checkBtn.textContent = 'Проверить';
            }, 1000);
            
        } else {
            feedbackDiv.innerHTML = `<div class="feedback-wrong">Неправильно! Правильный ответ: ${data.correct_answer}</div>`;
            showTranslation(data.correct_answer);
            
            const input = document.getElementById('answerInput');
            input.style.borderColor = '#dc3545';
            input.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
            
            setTimeout(() => {
                input.style.borderColor = '';
                input.style.backgroundColor = '';
                feedbackDiv.innerHTML = '';
                
                if (data.finished) {
                    loadNewBatch();
                } else {
                    displayWord(data.next_word);
                }
                checkBtn.disabled = false;
                checkBtn.textContent = 'Проверить';
            }, 2000);
        }
        
    } catch (error) {
        console.error('Ошибка:', error);
        feedbackDiv.innerHTML = '<div class="feedback-warning">Ошибка сервера. Попробуйте еще раз.</div>';
        checkBtn.disabled = false;
        checkBtn.textContent = 'Проверить';
    }
}

// Показать правильный перевод
function showTranslation(translation) {
    const translationBox = document.getElementById('translation-display');
    const translationSpan = translationBox.querySelector('span');
    translationSpan.textContent = translation;
    translationBox.style.display = 'flex';
    
    setTimeout(() => {
        if (translationBox.style.display === 'flex') {
            translationBox.style.display = 'none';
        }
    }, 3000);
}

// Показать ответ по запросу пользователя
async function revealAnswer() {
    try {
        // Получаем правильный ответ для текущего слова
        const response = await fetch('/cards/current', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success && data.correct_answer) {
            showTranslation(data.correct_answer);
            
            // Блокируем кнопку проверки
            const checkBtn = document.getElementById('checkAnswerBtn');
            checkBtn.disabled = true;
            
            // Переключаем на следующее слово
            setTimeout(async () => {
                const nextResponse = await fetch('/cards/next_word', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const nextData = await nextResponse.json();
                
                if (nextData.finished) {
                    loadNewBatch();
                } else {
                    displayWord(nextData.next_word);
                }
                checkBtn.disabled = false;
            }, 1500);
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}