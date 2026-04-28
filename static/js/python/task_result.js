console.log('Данные получены:', testResults);

// Функция для установки данных извне
function setTestResults(data) {
    console.log('setTestResults вызван, данные:', data);
    testResults = data;
    // Ждём загрузки DOM перед отрисовкой
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

// Функция для форматирования времени
function formatTime(seconds) {
    if (!seconds && seconds !== 0) return '0 с';
    if (seconds < 0.001) return `${(seconds * 1000000).toFixed(0)} мкс`;
    if (seconds < 0.1) return `${(seconds * 1000).toFixed(2)} мс`;
    return `${seconds.toFixed(3)} с`;
}

// Функция для определения статуса теста
function getStatus(test) {
    if (test.accept === true) {
        return { text: "✅ ОК", class: "status-ok" };
    } else if (test.stderr && test.stderr.trim() !== "") {
        return { text: "⚠️ Ошибка в работе программы", class: "status-error" };
    } else {
        return { text: "❌ Неверный ответ", class: "status-wrong" };
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
        
        // Номер теста - считаем с 1 (индекс + 1)
        const testNumber = index + 1;
        
        // Ячейка с номером теста (синий цвет)
        const idCell = row.insertCell(0);
        idCell.innerHTML = `<i class="fas fa-flask"></i> ${testNumber}`;
        idCell.style.color = '#2196f3';
        idCell.style.fontWeight = 'bold';
        idCell.style.fontSize = '16px';
        
        // Ячейка со статусом
        const statusCell = row.insertCell(1);
        const statusBadge = document.createElement('span');
        statusBadge.className = `status-badge ${status.class}`;
        statusBadge.innerHTML = status.text;
        statusCell.appendChild(statusBadge);
        
        // Ячейка со временем (синий цвет)
        const timeCell = row.insertCell(2);
        const timeValue = test.time !== undefined ? test.time : 0;
        timeCell.innerHTML = `<i class="far fa-clock"></i> ${formatTime(timeValue)}`;
        timeCell.style.color = '#2196f3';
        timeCell.style.fontWeight = '500';
        timeCell.style.fontFamily = 'monospace';
        
        // Добавляем обработчик клика на строку
        row.addEventListener('click', () => showErrorDetails(test, testNumber));
        
        // Добавляем класс для строк с ошибками
        if (status.class === 'status-error') {
            row.classList.add('status-error-row');
        } else if (status.class === 'status-wrong') {
            row.classList.add('status-wrong-row');
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

// Функция для отображения модального окна
function showErrorDetails(test, testNumber) {
    const status = getStatus(test);
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    
    if (!modal || !modalBody) return;
    
    let content = '';
    
    content += `
        <div class="error-section">
            <h3><i class="fas fa-info-circle"></i> Информация о тесте #${testNumber}</h3>
            <p><strong>Статус:</strong> ${status.text}</p>
            <p><strong>Время выполнения:</strong> ${formatTime(test.time)}</p>
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
    
    if (test.stdout && !test.accept) {
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
                <div class="error-content">${escapeHtml(test.stderr)}</div>
            </div>
        `;
    } else if (!test.accept && status.class === 'status-wrong') {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-question-circle"></i> Информация:</h3>
                <div class="error-content">Программа завершилась без ошибок, но результат не соответствует ожидаемому.</div>
            </div>
        `;
    }
    
    modalBody.innerHTML = content;
    modal.style.display = 'block';
}

// Функция закрытия модального окна
function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none';
    }
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

// Настройка модального окна
function setupModal() {
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');
    
    if (closeBtn) {
        closeBtn.onclick = closeModal;
    }
    
    window.onclick = function(event) {
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

// Автоматическая инициализация
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}