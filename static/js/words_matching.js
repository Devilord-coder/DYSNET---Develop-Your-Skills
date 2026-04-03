let selectedPairs = [];
let russianWordsList = [];
let englishWordsList = [];
let currentTopic = 'Случайные слова из разных категорий';
let tempRussian = null;
let tempEnglish = null;

// Цветовая палитра для 8 пар
const pairColors = [
    { bg: '#E8F5E9', border: '#4CAF50', dark: '#2E7D32' },
    { bg: '#E3F2FD', border: '#2196F3', dark: '#1565C0' },
    { bg: '#FFF3E0', border: '#FF9800', dark: '#E65100' },
    { bg: '#F3E5F5', border: '#9C27B0', dark: '#6A1B9A' },
    { bg: '#FFEBEE', border: '#F44336', dark: '#C62828' },
    { bg: '#E0F7FA', border: '#00BCD4', dark: '#00838F' },
    { bg: '#FFF8E1', border: '#FFC107', dark: '#FF8F00' },
    { bg: '#F1F8E9', border: '#8BC34A', dark: '#558B2F' }
];

// Функция загрузки слов с сервера
function loadWords(topic) {
    currentTopic = topic;

    fetch(`/get_words?topic=${encodeURIComponent(topic)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ошибка: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Получено слов:', data.russian_words.length);
            russianWordsList = data.russian_words;
            englishWordsList = data.english_words;
            renderWords(russianWordsList, englishWordsList);
        })
        .catch(error => console.error('Ошибка загрузки слов:', error));
}

// Функция отрисовки слов на странице
function renderWords(russianWords, englishWords) {
    const russianContainer = document.getElementById('russian-words-list');
    const englishContainer = document.getElementById('english-words-list');
    const selectedContainer = document.getElementById('selectedPairsList');
    const pairsCountSpan = document.getElementById('pairsCount');

    if (!russianContainer || !englishContainer) return;

    russianContainer.innerHTML = '';
    englishContainer.innerHTML = '';

    selectedPairs = [];
    tempRussian = null;
    tempEnglish = null;

    if (pairsCountSpan) {
        pairsCountSpan.textContent = '0';
    }
    if (selectedContainer) {
        selectedContainer.innerHTML = '<p class="text-muted">Пока нет выбранных пар. Нажмите на русское и английское слово, чтобы создать пару.</p>';
    }

    russianWords.forEach((word, index) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'word-btn russian-btn';
        btn.dataset.word = word;
        btn.dataset.idx = index;
        btn.textContent = word;
        btn.addEventListener('click', () => onRussianClick(btn));
        russianContainer.appendChild(btn);
    });

    englishWords.forEach((word, index) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'word-btn english-btn';
        btn.dataset.word = word;
        btn.dataset.idx = index;
        btn.textContent = word;
        btn.addEventListener('click', () => onEnglishClick(btn));
        englishContainer.appendChild(btn);
    });
}

// Обработка клика на кнопку с русским словом
function onRussianClick(btn) {
    if (btn.disabled) return;

    document.querySelectorAll('.russian-btn').forEach(b => b.classList.remove('temp-selected'));
    btn.classList.add('temp-selected');
    tempRussian = btn.dataset.word;

    if (tempEnglish) {
        addPair(tempRussian, tempEnglish);
        tempRussian = null;
        tempEnglish = null;
        document.querySelectorAll('.russian-btn').forEach(b => b.classList.remove('temp-selected'));
        document.querySelectorAll('.english-btn').forEach(b => b.classList.remove('temp-selected'));
    }
}

// Обработка клика на кнопку с английским словом
function onEnglishClick(btn) {
    if (btn.disabled) return;

    document.querySelectorAll('.english-btn').forEach(b => b.classList.remove('temp-selected'));
    btn.classList.add('temp-selected');
    tempEnglish = btn.dataset.word;

    if (tempRussian) {
        addPair(tempRussian, tempEnglish);
        tempRussian = null;
        tempEnglish = null;
        document.querySelectorAll('.russian-btn').forEach(b => b.classList.remove('temp-selected'));
        document.querySelectorAll('.english-btn').forEach(b => b.classList.remove('temp-selected'));
    }
}

// Обновление отображения пар
function updateSelectedPairsDisplay() {
    const container = document.getElementById('selectedPairsList');
    const pairsCountSpan = document.getElementById('pairsCount');

    if (!container) return;

    if (pairsCountSpan) {
        pairsCountSpan.textContent = selectedPairs.length;
    }

    if (selectedPairs.length === 0) {
        container.innerHTML = '<p class="text-muted">Пока нет выбранных пар. Нажмите на русское и английское слово, чтобы создать пару.</p>';
        return;
    }

    let html = '<div class="pairs-grid">';
    selectedPairs.forEach((pair, idx) => {
        const color = pairColors[idx % pairColors.length];
        html += `
            <div class="pair-card" data-idx="${idx}" style="background: ${color.bg}; border-left: 4px solid ${color.border};">
                <span class="pair-russian" style="color: ${color.dark};">${escapeHtml(pair.russian)}</span>
                <span class="pair-arrow" style="color: ${color.dark};">→</span>
                <span class="pair-english" style="color: ${color.dark};">${escapeHtml(pair.english)}</span>
                <button class="btn-remove-pair" data-idx="${idx}" style="background: ${color.border};">✖</button>
            </div>`;
    });
    html += '</div>';

    container.innerHTML = html;

    document.querySelectorAll('.btn-remove-pair').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const idx = parseInt(btn.dataset.idx);
            removePair(idx);
        });
    });
}

// Безопасное изменение html
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Добавляем пару слов, если они с разных языков
function addPair(russianWord, englishWord) {
    if (selectedPairs.some(p => p.russian === russianWord)) {
        alert('Это русское слово уже выбрано!');
        return false;
    }

    if (selectedPairs.some(p => p.english === englishWord)) {
        alert('Это английское слово уже выбрано!');
        return false;
    }

    const pairIndex = selectedPairs.length;
    const color = pairColors[pairIndex % pairColors.length];

    selectedPairs.push({
        russian: russianWord,
        english: englishWord,
        color: color
    });

    updateButtonsState();
    updateSelectedPairsDisplay();
    highlightMatchingWords(pairIndex);
    return true;
}

// Подсветка клавиш при составлении пар
function highlightMatchingWords(pairIndex) {
    const pair = selectedPairs[pairIndex];
    if (!pair) return;

    const color = pair.color;

    document.querySelectorAll('.russian-btn').forEach(btn => {
        if (btn.dataset.word === pair.russian) {
            btn.style.background = color.bg;
            btn.style.border = `2px solid ${color.border}`;
            btn.style.color = color.dark;
        }
    });

    document.querySelectorAll('.english-btn').forEach(btn => {
        if (btn.dataset.word === pair.english) {
            btn.style.background = color.bg;
            btn.style.border = `2px solid ${color.border}`;
            btn.style.color = color.dark;
        }
    });
}

// Удаление пары слов
function removePair(index) {
    selectedPairs.splice(index, 1);

    selectedPairs.forEach((pair, idx) => {
        pair.color = pairColors[idx % pairColors.length];
    });

    updateButtonsState();
    updateSelectedPairsDisplay();
    resetButtonsColors();

    selectedPairs.forEach((_, idx) => {
        highlightMatchingWords(idx);
    });
}

function resetButtonsColors() {
    document.querySelectorAll('.russian-btn, .english-btn').forEach(btn => {
        btn.style.background = '';
        btn.style.border = '';
        btn.style.color = '';
        btn.classList.remove('matched', 'selected', 'temp-selected', 'permanent-correct', 'permanent-incorrect');
    });
}

// Блокировка кнопок, с которыми уже составлена пара
function updateButtonsState() {
    document.querySelectorAll('.russian-btn').forEach(btn => {
        const word = btn.dataset.word;
        if (selectedPairs.some(p => p.russian === word)) {
            btn.disabled = true;
            btn.classList.add('matched');
        } else {
            btn.disabled = false;
            btn.classList.remove('matched');
            btn.classList.remove('selected');
        }
    });

    document.querySelectorAll('.english-btn').forEach(btn => {
        const word = btn.dataset.word;
        if (selectedPairs.some(p => p.english === word)) {
            btn.disabled = true;
            btn.classList.add('matched');
        } else {
            btn.disabled = false;
            btn.classList.remove('matched');
            btn.classList.remove('selected');
        }
    });
}

// Отправка всех пар на сервер
function submitAllPairs() {
    if (selectedPairs.length !== 8) {
        alert(`Вы выбрали ${selectedPairs.length} пар из 8. Нужно собрать все 8 пар!`);
        return;
    }

    console.log('Отправка пар:', selectedPairs);

    const submitBtn = document.getElementById('submitAllBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Проверка...';
    }

    fetch('/check_words', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pairs: selectedPairs })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Результат:', data);
            window.location.href = '/words_matching/results';
        })
        .catch(error => {
            console.error('Ошибка отправки:', error);
            alert('Произошла ошибка при проверке. Попробуйте ещё раз.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Отправить все пары';
            }
        });
}

// Инициализация
document.addEventListener('DOMContentLoaded', function () {
    const topicSelect = document.getElementById('topicSelect');
    const refreshBtn = document.getElementById('refreshBtn');
    const submitBtn = document.getElementById('submitAllBtn');
    const clearBtn = document.getElementById('clearAllBtn');

    window.getCurrentTopic = function () {
        return topicSelect ? topicSelect.value : 'Случайные слова из разных категорий';
    };

    if (topicSelect) {
        topicSelect.addEventListener('change', function () {
            loadWords(this.value);
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', function () {
            loadWords(window.getCurrentTopic());
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener('click', submitAllPairs);
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Очистить все выбранные пары?')) {
                selectedPairs = [];
                tempRussian = null;
                tempEnglish = null;
                resetButtonsColors();
                updateButtonsState();
                updateSelectedPairsDisplay();
            }
        });
    }

    loadWords(window.getCurrentTopic());
});