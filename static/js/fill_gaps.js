let resultsData = null;

// Проверка, что все поля заполнены
function validateForm() {
    let allFilled = true;
    document.querySelectorAll('.gap-select').forEach((select) => {
        if (!select.value) {
            allFilled = false;
            select.style.borderColor = 'red';
        } else {
            select.style.borderColor = '#3498db';
        }
    });
    return allFilled;
}

// Подсветка результатов
function highlightResults(results) {
    console.log('Подсветка результатов:', results);

    const selects = document.querySelectorAll('.gap-select');

    selects.forEach((select, index) => {
        const result = results.find(r => r.index === index);
        if (!result) return;

        if (result.is_correct) {
            select.classList.add('correct');
            select.classList.remove('incorrect');
        } else {
            select.classList.add('incorrect');
            select.classList.remove('correct');

            const oldTooltip = select.parentElement.querySelector('.correct-answer-tooltip');
            if (oldTooltip) oldTooltip.remove();

            const tooltip = document.createElement('div');
            tooltip.className = 'correct-answer-tooltip';
            tooltip.innerHTML = `Правильный ответ: <strong>${result.correct_answer}</strong>`;
            tooltip.style.display = 'none';
            select.parentElement.appendChild(tooltip);
        }

        select.disabled = true;
    });

    const resultsDiv = document.getElementById('results-summary');
    const correctCountSpan = document.getElementById('correct-count');
    const totalCountSpan = document.getElementById('total-count');
    const percentSpan = document.getElementById('percent');

    if (resultsDiv && correctCountSpan && totalCountSpan && percentSpan) {
        const correctCount = results.filter(r => r.is_correct).length;
        const total = results.length;
        const percent = resultsData.percent || Math.round(correctCount / total * 100);

        correctCountSpan.textContent = correctCount;
        totalCountSpan.textContent = total;
        percentSpan.textContent = percent;

        resultsDiv.style.display = 'block';
    }
}

// Сброс формы для новой попытки
function resetForm() {
    const selects = document.querySelectorAll('.gap-select');
    selects.forEach((select) => {
        select.value = '';
        select.disabled = false;
        select.classList.remove('correct', 'incorrect');
        select.style.borderColor = '#3498db';

        const tooltip = select.parentElement.querySelector('.correct-answer-tooltip');
        if (tooltip) tooltip.remove();
    });

    const checkBtn = document.getElementById('checkBtn');
    const resultsDiv = document.getElementById('results-summary');

    if (checkBtn) checkBtn.style.display = 'inline-block';
    if (resetBtn) resetBtn.style.display = 'none';
    if (resultsDiv) resultsDiv.style.display = 'none';

    resultsData = null;
}

// Отправка на проверку
async function submitCheck() {
    if (!validateForm()) {
        alert('Пожалуйста, заполните все пропуски!');
        return;
    }

    const gapInputs = document.querySelectorAll('.gap-select');
    const formData = new FormData();

    gapInputs.forEach((select, idx) => {
        formData.append(`gap_${idx}`, select.value);
    });

    const checkBtn = document.getElementById('checkBtn');
    const originalText = checkBtn?.textContent;
    if (checkBtn) checkBtn.textContent = 'Проверка...';

    try {
        const response = await fetch('/check_fill_gaps', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Ответ сервера:', data);

        if (data.results) {
            resultsData = data;
            highlightResults(data.results);
        } else {
            console.error('Неверный формат ответа:', data);
            alert('Ошибка: сервер вернул неверный формат данных');
        }

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при проверке: ' + error.message);
    } finally {
        if (checkBtn) checkBtn.textContent = originalText;
    }
}

// Инициализация обработчиков
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM загружен, инициализация обработчиков');

    const checkBtn = document.getElementById('checkBtn');
    const resetBtn = document.getElementById('resetBtn');
    const newTextBtn = document.getElementById('newTextBtn');

    if (checkBtn) {
        checkBtn.addEventListener('click', submitCheck);
        console.log('Обработчик кнопки "Проверить" добавлен');
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
        console.log('Обработчик кнопки "Новая попытка" добавлен');
    }

    if (newTextBtn) {
        newTextBtn.addEventListener('click', function () {
            window.location.reload();
        });
        console.log('Обработчик кнопки "Новый текст" добавлен');
    }
});