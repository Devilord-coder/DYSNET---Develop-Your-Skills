// данные о клавиатуре для дальнейшей отрисовки
const russianKeyboardLayout = [
    ['Ё', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '+', '\\', '←'],
    ['Tab', 'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', '\\'],
    ['Caps', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э', 'Enter'],
    ['Shift', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '.', 'Shift'],
    ['Ctrl', '', 'Alt', ' ', 'Alt', '', 'Ctrl']
];

const englishKeyboardLayout = [
    ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\\', '←'],
    ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
    ['Caps', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
    ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
    ['Ctrl', '', 'Alt', ' ', 'Alt', '', 'Ctrl']
];

// цветовая разметка клавиш
const fingerZones = {
    'pinky_left': {
        keys: { russian: ['Ё', '1', 'Й', 'Ф', 'Я'], english: ['`', '1', 'Q', 'A', 'Z'] },
        borderColor: '#ff0000ff'
    },
    'ring_left': {
        keys: { russian: ['2', 'Ц', 'Ы', 'Ч'], english: ['2', 'W', 'S', 'X'] },
        borderColor: '#f6ff00ff'
    },
    'middle_left': {
        keys: { russian: ['3', 'У', 'В', 'С'], english: ['3', 'E', 'D', 'C'] },
        borderColor: '#0033ffff'
    },
    'index_left': {
        keys: { russian: ['4', '5', 'К', 'Е', 'А', 'П', 'М', 'И'], english: ['4', '5', 'R', 'T', 'F', 'G', 'V', 'B'] },
        borderColor: '#ffa600ff'
    },
    'index_right': {
        keys: { russian: ['6', '7', 'Н', 'Г', 'Р', 'О', 'Т', 'Ь'], english: ['6', '7', 'Y', 'U', 'H', 'J', 'N', 'M'] },
        borderColor: '#fffb00ff'
    },
    'middle_right': {
        keys: { russian: ['8', 'Ш', 'Л', 'Б'], english: ['8', 'I', 'K', ','] },
        borderColor: '#1eff00ff'
    },
    'ring_right': {
        keys: { russian: ['9', 'Щ', 'Д', 'Ю'], english: ['9', 'O', 'L', '.'] },
        borderColor: '#fd00cbff'
    },
    'pinky_right': {
        keys: { russian: ['0', 'З', 'Х', 'Ъ', 'Ж', 'Э', '-', '+', '.'], english: ['0', 'P', ';', '-', '=', '/', '[', ']', "'"] },
        borderColor: '#3300ffff'
    },
    'thumbs': {
        keys: { russian: [' '], english: [' '] },
        borderColor: '#000000ff'
    }
};

const specialKeys = ['Tab', 'Caps', 'Shift', 'Ctrl', 'Alt', 'Enter', '←', '\\'];

// данные для отображения (берутся с сервера)
let currentText = "";
let currentIndex = 0;
let correctCount = 0;
let errorCount = 0;
let currentLanguage = 'russian';
let isWaitingForResponse = false;

// получение цвета границ клавиш
function getKeyBorderColor(keyText) {
    for (const zone of Object.values(fingerZones)) {
        const zoneKeys = zone.keys[currentLanguage];
        if (zoneKeys && zoneKeys.includes(keyText)) {
            return zone.borderColor;
        }
    }
    return '#cccccc';
}

// изменение языка
function setLanguage(lang) {
    currentLanguage = lang;
    const layout = lang === 'russian' ? russianKeyboardLayout : englishKeyboardLayout;
    createKeyboard(layout);
    updateKeyboardHighlight();
}

// создание клавиатуры
function createKeyboard(layout) {
    const keyboardDiv = document.getElementById('keyboard');
    if (!keyboardDiv) return;

    keyboardDiv.innerHTML = '';

    layout.forEach((row) => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'key-row';

        row.forEach(keyText => {
            if (keyText === '') return;

            const keyDiv = document.createElement('div');
            keyDiv.className = 'key';

            const borderColor = getKeyBorderColor(keyText);

            keyDiv.style.backgroundColor = '#ffffff';
            keyDiv.style.color = '#2c3e50';
            keyDiv.style.border = `3px solid ${borderColor}`;
            keyDiv.style.borderRadius = '8px';
            keyDiv.style.boxSizing = 'border-box';

            if (specialKeys.includes(keyText)) {
                keyDiv.style.backgroundColor = '#e9ecef';
                keyDiv.classList.add('special');
            }

            if (keyText === ' ') {
                keyDiv.classList.add('key-space');
                keyDiv.textContent = 'ПРОБЕЛ';
                keyDiv.style.minWidth = '300px';
            } else if (keyText === '←') {
                keyDiv.classList.add('key-backspace');
                keyDiv.textContent = '⌫';
            } else if (keyText === 'Enter') {
                keyDiv.classList.add('key-enter');
                keyDiv.textContent = '⏎';
            } else if (specialKeys.includes(keyText)) {
                keyDiv.textContent = keyText;
            } else {
                keyDiv.textContent = keyText;
            }

            rowDiv.appendChild(keyDiv);
        });
        keyboardDiv.appendChild(rowDiv);
    });
}

// изменения состояния прогресса
function updateStats() {
    const progressEl = document.getElementById('progress');
    const correctEl = document.getElementById('correctCount');
    const errorEl = document.getElementById('errorCount');

    if (progressEl) progressEl.textContent = currentIndex > 0 ? Math.round((currentIndex / currentText.length) * 100) : 0;
    if (correctEl) correctEl.textContent = correctCount;
    if (errorEl) errorEl.textContent = errorCount;
}

// изменение отрисовки текста
function updateSentenceDisplay() {
    const container = document.getElementById('sentenceText');
    if (!container) return;

    container.innerHTML = '';

    for (let i = 0; i < currentText.length; i++) {
        const span = document.createElement('span');
        span.textContent = currentText[i];
        span.setAttribute('data-index', i);

        if (i < currentIndex) {
            span.classList.add('correct');
        } else if (i === currentIndex) {
            span.classList.add('current');
        }

        container.appendChild(span);
    }
}

// подсветка на клавиатуре текущей клавиши, которую надо нажать
function updateKeyboardHighlight() {
    if (currentIndex >= currentText.length) return;

    const expectedChar = currentText[currentIndex];

    const keys = document.querySelectorAll('.key');
    keys.forEach(key => {
        const keyText = key.textContent.trim();

        key.style.backgroundColor = '#ffffff';
        key.style.borderWidth = '3px';

        if (specialKeys.includes(keyText)) {
            key.style.backgroundColor = '#e9ecef';
        }

        const isExpected = (keyText === expectedChar ||
            keyText === expectedChar.toUpperCase() ||
            keyText === expectedChar.toLowerCase() ||
            (expectedChar === ' ' && keyText === 'ПРОБЕЛ'));

        if (isExpected) {
            key.style.backgroundColor = '#ff0000';
            key.style.color = '#ffffff';
        } else {
            const borderColor = getKeyBorderColor(keyText);
            key.style.borderColor = borderColor;
            key.style.color = '#2c3e50';
        }
    });
}

// подсветка ошибки
function highlightError() {
    const currentSpan = document.querySelector(`.sentence-text span[data-index='${currentIndex}']`);
    if (currentSpan) {
        currentSpan.classList.add('incorrect');
        setTimeout(() => currentSpan.classList.remove('incorrect'), 300);
    }
}

// обновление визуального отображения страницы
function updateAllDisplay() {
    updateSentenceDisplay();
    updateStats();
    updateKeyboardHighlight();
}

// отправление данных о нажатой клавише на сервер
async function sendToServer(url, data = null) {
    if (isWaitingForResponse && url === '/api/check_key') return null;

    isWaitingForResponse = true;

    try {
        const options = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        };
        if (data) options.body = JSON.stringify(data);

        const response = await fetch(url, options);
        const result = await response.json();
        isWaitingForResponse = false;
        return result;

    } catch (error) {
        console.error('Ошибка:', error);
        isWaitingForResponse = false;
        return null;
    }
}

// отправляем нажатие, получаем все данные с сервера, меняем визуальное отображение
async function sendKey(key) {
    console.log('Отправляем на сервер:', key);
    const result = await sendToServer('/api/check_key', { key: key });
    if (result) {
        updateFromServer(result);
    }
}

// сброс тренировки, новые данные получаем с сервера
async function resetTraining() {
    const result = await sendToServer('/api/reset_training', {
        mode: 'all',
        language: currentLanguage
    });

    if (result?.status === 'ok') {
        currentText = result.text;
        currentIndex = 0;
        correctCount = 0;
        errorCount = 0;
        updateAllDisplay();
    }
}

// получение данных с сервера, вывод сообщения об окончании тренировки
function updateFromServer(data) {
    console.log('Ответ сервера:', data);

    if (data.finished) {
        alert(`Поздравляем! Тренировка завершена!\nПравильно: ${data.correct_clicks}\nОшибок: ${data.error_clicks}`);
        resetTraining();
        return;
    }

    currentIndex = data.current_index;
    correctCount = data.correct_clicks;
    errorCount = data.error_clicks;

    updateAllDisplay();

    if (!data.is_correct) {
        highlightError();
    }
}

// обработка нажатий пользователем на клавиши
function handleKeyPress(event) {
    sendKey(event.key);
}

// инициализация
function initTraining(texts, language) {
    console.log('initTraining:', { texts, language });

    if (typeof texts === 'string') {
        currentText = texts;
    } else if (Array.isArray(texts) && texts.length > 0) {
        currentText = texts[0];
    } else {
        console.error('Неверный формат texts');
        return;
    }

    currentLanguage = language;
    currentIndex = 0;
    correctCount = 0;
    errorCount = 0;

    setLanguage(language);
    updateAllDisplay();

    document.addEventListener('keydown', handleKeyPress);
    console.log('Тренажёр готов, текст:', currentText.substring(0, 50));
}

// Экспорт
window.initTraining = initTraining;
window.resetTraining = resetTraining;
window.setLanguage = setLanguage;