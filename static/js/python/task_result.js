console.log('Данные получены:', testResults);

// Функция для установки данных извне
function setTestResults(data) {
    console.log('setTestResults вызван, данные:', data);
    testResults = data;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => renderAll());
    } else {
        renderAll();
    }
}

// Главная функция отрисовки всего
function renderAll() {
    console.log('renderAll вызван, testResults:', testResults);

    if (!testResults || testResults.length === 0) {
        console.warn('Нет данных для отображения');
        const tbody = document.getElementById('table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="3">Нет данных для отображения</td></tr>';
        }
        return;
    }

    addStatsHTML();
    updateStats(testResults);
    renderTable(testResults);
    setupModal();
}

// Функция для форматирования времени (ИСПРАВЛЕНА)
function formatTime(seconds) {
    // Проверяем входное значение
    if (seconds === undefined || seconds === null) {
        return '0 с';
    }

    // Преобразуем в число, если пришла строка
    let timeValue = seconds;
    if (typeof seconds === 'string') {
        timeValue = parseFloat(seconds);
    }

    // Проверяем, что получилось число
    if (isNaN(timeValue)) {
        console.warn('formatTime получил не число:', seconds);
        return '0 с';
    }

    // Форматируем время
    if (timeValue < 0.001) {
        return `${(timeValue * 1000000).toFixed(0)} мкс`;
    }
    if (timeValue < 0.1) {
        return `${(timeValue * 1000).toFixed(2)} мс`;
    }
    return `${timeValue.toFixed(3)} с`;
}

// Функция для определения статуса теста
function getStatus(test) {
    if (test.accept === true) {
        return { text: "ОК", class: "status-ok", icon: "✅" };
    } else if (test.stderr && test.stderr.trim() !== "") {
        return { text: "Ошибка в работе программы", class: "status-error", icon: "⚠️" };
    } else {
        return { text: "Неверный ответ", class: "status-wrong", icon: "❌" };
    }
}

// Функция для обновления статистики
function updateStats(results) {
    console.log('updateStats вызван');
    const total = results.length;
    const ok = results.filter(r => r.accept === true).length;
    const errors = results.filter(r => r.stderr && r.stderr.trim() !== "" && !r.accept).length;
    const wrong = total - ok - errors;

    const statsDiv = document.getElementById('stats');
    if (statsDiv) {
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value" id="total-tests">${total}</div>
                <div class="stat-label"><i class="fas fa-chart-simple"></i> Всего тестов</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="ok-tests">${ok}</div>
                <div class="stat-label"><i class="fas fa-check-circle"></i> Пройдено</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-tests">${errors}</div>
                <div class="stat-label"><i class="fas fa-times-circle"></i> С ошибками</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="wrong-tests">${wrong}</div>
                <div class="stat-label"><i class="fas fa-exclamation-circle"></i> Неверный ответ</div>
            </div>
        `;
    }
}

// Функция для отображения таблицы
function renderTable(results) {
    console.log('renderTable вызван, количество:', results.length);

    const tbody = document.getElementById('table-body');
    if (!tbody) {
        console.error("Элемент table-body не найден!");
        return;
    }

    if (!results || results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">Нет данных для отображения</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    results.forEach((test, index) => {
        const row = tbody.insertRow();
        const status = getStatus(test);

        // Номер теста - считаем с 1
        const testNumber = index + 1;

        // Ячейка 1: Номер теста (синий)
        const idCell = row.insertCell(0);
        idCell.innerHTML = `<i class="fas fa-flask"></i> ${testNumber}`;
        idCell.style.color = '#2196f3';
        idCell.style.fontWeight = 'bold';
        idCell.style.fontSize = '16px';

        // Ячейка 2: Статус с иконкой
        const statusCell = row.insertCell(1);

        // Создаём контейнер для статуса
        const statusContainer = document.createElement('div');
        statusContainer.style.display = 'flex';
        statusContainer.style.alignItems = 'center';
        statusContainer.style.gap = '8px';

        // Иконка статуса
        const iconSpan = document.createElement('span');
        iconSpan.textContent = status.icon;
        iconSpan.style.fontSize = '18px';

        // Текст статуса
        const textSpan = document.createElement('span');
        textSpan.textContent = status.text;

        // Кнопка с деталями ошибки (только если есть ошибка)
        if (!test.accept) {
            const detailsBtn = document.createElement('button');
            detailsBtn.innerHTML = '<i class="fas fa-info-circle"></i>';
            detailsBtn.title = 'Показать детали ошибки';
            detailsBtn.style.cssText = `
                background: none;
                border: none;
                cursor: pointer;
                font-size: 16px;
                color: #ff9800;
                margin-left: 8px;
                padding: 4px 8px;
                border-radius: 50%;
                transition: all 0.3s ease;
            `;

            // Эффект при наведении
            detailsBtn.addEventListener('mouseenter', () => {
                detailsBtn.style.backgroundColor = 'rgba(255, 152, 0, 0.2)';
                detailsBtn.style.transform = 'scale(1.1)';
            });
            detailsBtn.addEventListener('mouseleave', () => {
                detailsBtn.style.backgroundColor = 'transparent';
                detailsBtn.style.transform = 'scale(1)';
            });

            // Обработчик клика по кнопке деталей
            detailsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showErrorDetails(test, testNumber);
            });

            statusContainer.appendChild(iconSpan);
            statusContainer.appendChild(textSpan);
            statusContainer.appendChild(detailsBtn);
        } else {
            statusContainer.appendChild(iconSpan);
            statusContainer.appendChild(textSpan);
        }

        statusCell.appendChild(statusContainer);

        // Ячейка 3: Время выполнения (синий)
        const timeCell = row.insertCell(2);
        const timeValue = test.time !== undefined ? test.time : 0;
        timeCell.innerHTML = `<i class="far fa-clock"></i> ${formatTime(timeValue)}`;
        timeCell.style.color = '#2196f3';
        timeCell.style.fontWeight = '500';
        timeCell.style.fontFamily = 'monospace';

        // Добавляем класс для строк с ошибками
        if (status.class === 'status-error') {
            row.classList.add('status-error-row');
        } else if (status.class === 'status-wrong') {
            row.classList.add('status-wrong-row');
        }

        // Добавляем обработчик клика на всю строку
        if (!test.accept) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    showErrorDetails(test, testNumber);
                }
            });
        } else {
            row.style.cursor = 'default';
        }
    });

    console.log(`✅ Отображено ${results.length} тестов`);
}

// Функция для экранирования HTML
function escapeHtml(text) {
    if (!text) return '<пусто>';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Функция для копирования кода в буфер обмена
function copyCodeToClipboard() {
    const codeElement = document.querySelector('.python-code');
    if (!codeElement) return;

    // Получаем оригинальный код без HTML-тегов
    const originalCode = codeElement.textContent || codeElement.innerText;

    navigator.clipboard.writeText(originalCode).then(() => {
        // Показываем уведомление
        const btn = document.querySelector('.copy-code-btn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Скопировано!';
        btn.style.background = '#4caf50';

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '#2196f3';
        }, 2000);
    }).catch(err => {
        console.error('Ошибка копирования:', err);
        alert('Не удалось скопировать код');
    });
}

// Функция для отображения модального окна с деталями ошибки
function showErrorDetails(test, testNumber) {
    const status = getStatus(test);
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');

    if (!modal || !modalBody) return;

    let timeValue = test.time;
    if (typeof timeValue === 'string') {
        timeValue = parseFloat(timeValue);
    }
    if (isNaN(timeValue)) {
        timeValue = 0;
    }

    let content = `
        <div class="error-section">
            <h3><i class="fas fa-info-circle"></i> Информация о тесте #${testNumber}</h3>
            <p><strong>Статус:</strong> ${status.icon} ${status.text}</p>
            <p><strong>Время выполнения:</strong> ${formatTime(timeValue)}</p>
            <p><strong>Код возврата:</strong>
                <span class="returncode ${test.returncode === 0 ? 'returncode-zero' : 'returncode-nonzero'}">
                    ${test.returncode !== undefined ? test.returncode : '—'}
                </span>
            </p>
        </div>
    `;

    if (test.stdin) {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-keyboard"></i> Входные данные (stdin):</h3>
                <div class="input-content">${escapeHtml(test.stdin)}</div>
            </div>
        `;
    }

    if (test.stdout && test.stdout.trim() !== "") {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-terminal"></i> Фактический вывод (stdout):</h3>
                <div class="input-content">${escapeHtml(test.stdout)}</div>
            </div>
        `;
    }

    if (test.stderr && test.stderr.trim() !== "") {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-exclamation-triangle"></i> Текст ошибки (stderr):</h3>
                <div class="error-content" style="background: #0a0a0a; border-left-color: #f44336; color: #ff6b6b;">
                    ${escapeHtml(test.stderr)}
                </div>
            </div>
        `;
    }

    if (test.code) {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-code"></i> Код решения:</h3>
                <div class="code-container" style="background: #0a0a0a; border-radius: 8px; overflow: hidden; margin-top: 10px;">
                    <div class="code-header" style="background: #1a1a1a; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333;">
                        <span style="color: #fff; font-family: monospace;">
                            <i class="fab fa-python"></i> Python
                        </span>
                        <button class="copy-code-btn" onclick="copyCodeToClipboard()" style="background: #2196f3; border: none; color: white; padding: 5px 12px; border-radius: 5px; cursor: pointer; font-size: 12px;">
                            <i class="fas fa-copy"></i> Копировать код
                        </button>
                    </div>
                    <pre class="python-code" style="margin: 0; padding: 15px; overflow-x: auto; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.5; color: #fff;">${escapeHtmlWithHighlighting(test.code)}</pre>
                </div>
            </div>
        `;
    }

    if (!test.accept && (!test.stderr || test.stderr.trim() === "")) {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-question-circle"></i> Информация:</h3>
                <div class="error-content" style="background: #fff8e1; border-left-color: #ff9800; color: #856404;">
                    Программа завершилась без ошибок, но результат не соответствует ожидаемому.
                </div>
            </div>
        `;
    }

    // ВАЖНО: НЕТ ДОБАВЛЕНИЯ modal-buttons!
    modalBody.innerHTML = content;
    modal.style.display = 'block';
}

// Функция для экранирования HTML с подсветкой Python (простая версия)
function escapeHtmlWithHighlighting(code) {
    if (!code) return '<пусто>';

    // Сначала экранируем HTML
    let escaped = code.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Простая подсветка синтаксиса Python
    // Ключевые слова Python
    const keywords = ['def', 'class', 'return', 'import', 'from', 'as', 'if', 'elif', 'else', 'for', 'while', 'break', 'continue', 'pass', 'try', 'except', 'finally', 'raise', 'with', 'lambda', 'yield', 'assert', 'async', 'await', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'];

    keywords.forEach(keyword => {
        const regex = new RegExp(`\\b(${keyword})\\b`, 'g');
        escaped = escaped.replace(regex, '<span style="color: #c792ea; font-weight: bold;">$1</span>');
    });

    // Строки
    escaped = escaped.replace(/(".*?"|'.*?')/g, '<span style="color: #c3e88d;">$1</span>');

    // Комментарии
    escaped = escaped.replace(/(#.*$)/gm, '<span style="color: #546e7a; font-style: italic;">$1</span>');

    // Числа
    escaped = escaped.replace(/\b(\d+)\b/g, '<span style="color: #f78c6c;">$1</span>');

    // Функции
    escaped = escaped.replace(/\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/g, '<span style="color: #82aaff;">$1</span>(');

    return escaped;
}

// Инициализация статистики
function addStatsHTML() {
    const statsDiv = document.getElementById('stats');
    if (statsDiv && statsDiv.children.length === 0) {
        statsDiv.innerHTML = `
            <div class="stat-card">
                <div class="stat-value" id="total-tests">0</div>
                <div class="stat-label"><i class="fas fa-chart-simple"></i> Всего тестов</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="ok-tests">0</div>
                <div class="stat-label"><i class="fas fa-check-circle"></i> Пройдено</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="error-tests">0</div>
                <div class="stat-label"><i class="fas fa-times-circle"></i> С ошибками</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="wrong-tests">0</div>
                <div class="stat-label"><i class="fas fa-exclamation-circle"></i> Неверный ответ</div>
            </div>
        `;
    }
}

// Функция закрытия модального окна (оставляем только крестик в шапке)
function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Настройка модального окна (только крестик)
function setupModal() {
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');

    if (closeBtn) {
        closeBtn.onclick = closeModal;
    }

    // Клик вне модального окна тоже закрывает
    window.onclick = function (event) {
        if (event.target === modal) {
            closeModal();
        }
    };
}

// Главная функция инициализации
function init() {
    console.log('init() вызван');
    console.log('testResults глобальные:', window.testResults);

    if (window.testResults && window.testResults.length > 0) {
        testResults = window.testResults;
        renderAll();
    } else if (testResults && testResults.length > 0) {
        renderAll();
    } else {
        console.warn('Нет данных для отображения');
        const tbody = document.getElementById('table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="3">Нет данных для отображения</td></tr>';
        }
    }
}

// Экспортируем в глобальную область
window.init = init;
window.setTestResults = setTestResults;
window.closeModal = closeModal;
// Экспортируем функцию копирования в глобальную область
window.copyCodeToClipboard = copyCodeToClipboard;

// Автоматическая инициализация
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}