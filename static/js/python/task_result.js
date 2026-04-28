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
    const total = results.length;
    const ok = results.filter(r => r.accept === true).length;
    const errors = results.filter(r => r.stderr && r.stderr.trim() !== "" && !r.accept).length;
    const wrong = total - ok - errors;

    document.getElementById('total-tests').textContent = total;
    document.getElementById('ok-tests').textContent = ok;
    document.getElementById('error-tests').textContent = errors;
    document.getElementById('wrong-tests').textContent = wrong;
}

// Функция для форматирования времени
function formatTime(seconds) {
    if (seconds < 0.001) {
        return `${(seconds * 1000000).toFixed(0)} мкс`;
    } else if (seconds < 0.1) {
        return `${(seconds * 1000).toFixed(2)} мс`;
    } else {
        return `${seconds.toFixed(3)} с`;
    }
}

// Функция для отображения таблицы
function renderTable(results) {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '';

    results.forEach(test => {
        const row = tbody.insertRow();
        const status = getStatus(test);

        // ID теста
        const idCell = row.insertCell(0);
        idCell.className = 'test-id';
        idCell.innerHTML = `<i class="fas fa-flask"></i> ${test.test_id}`;

        // Статус
        const statusCell = row.insertCell(1);
        const statusBadge = document.createElement('span');
        statusBadge.className = `status-badge ${status.class}`;
        statusBadge.innerHTML = status.text;
        statusCell.appendChild(statusBadge);

        // Время
        const timeCell = row.insertCell(2);
        timeCell.className = 'time-cell';
        timeCell.innerHTML = `<i class="far fa-clock"></i> ${formatTime(test.time)}`;

        // Добавляем обработчик клика на строку
        row.addEventListener('click', () => showErrorDetails(test));

        // Добавляем класс для строк с ошибками
        if (status.class === 'status-error') {
            row.classList.add('status-error-row');
        } else if (status.class === 'status-wrong') {
            row.classList.add('status-wrong-row');
        }
    });
}

// Функция для экранирования HTML
function escapeHtml(text) {
    if (!text) return '<пусто>';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Функция для отображения модального окна
function showErrorDetails(test) {
    const status = getStatus(test);
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');

    let content = '';

    content += `
        <div class="error-section">
            <h3><i class="fas fa-info-circle"></i> Информация о тесте #${test.test_id}</h3>
            <p><strong>Статус:</strong> ${status.text}</p>
            <p><strong>Время выполнения:</strong> ${formatTime(test.time)}</p>
            <p><strong>Код возврата:</strong>
                <span class="returncode ${test.returncode === 0 ? 'returncode-zero' : 'returncode-nonzero'}">
                    ${test.returncode}
                </span>
            </p>
        </div>
    `;

    // Входные данные
    if (test.stdin) {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-keyboard"></i> Входные данные (stdin):</h3>
                <div class="input-content">${escapeHtml(test.stdin)}</div>
            </div>
        `;
    }

    // Вывод программы (если есть и тест не пройден)
    if (test.stdout && !test.accept) {
        content += `
            <div class="error-section">
                <h3><i class="fas fa-terminal"></i> Фактический вывод (stdout):</h3>
                <div class="input-content">${escapeHtml(test.stdout)}</div>
            </div>
        `;
    }

    // Ошибка
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

// Закрытие модального окна
function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}

// Добавляем статистику в HTML
function addStatsHTML() {
    const statsDiv = document.getElementById('stats');
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

// Инициализация
function init() {
    addStatsHTML();
    updateStats(testResults);
    renderTable(testResults);

    // Настройка закрытия модального окна
    const modal = document.getElementById('modal');
    const closeBtn = document.querySelector('.close');

    closeBtn.onclick = closeModal;

    window.onclick = function (event) {
        if (event.target === modal) {
            closeModal();
        }
    };
}

// Запуск при загрузке
document.addEventListener('DOMContentLoaded', init);