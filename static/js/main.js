document.addEventListener('DOMContentLoaded', function () {
    // Получаем начальное количество тестов
    const initialTestCount = document.querySelectorAll('.test-item').length;

    // Инициализация менеджера тестов
    const testsManager = new TestsManager({
        containerId: 'tests-container',
        addButtonId: 'add-test',
        maxTests: 20,
        minTests: 1,
        initialIndex: initialTestCount
    });

    // Валидация формы перед отправкой
    const form = document.getElementById('taskForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            const validation = testsManager.validateTests();

            if (!validation.isValid) {
                e.preventDefault();
                showErrors(validation.errors);
            }
        });
    }

    // Функция показа ошибок
    function showErrors(errors) {
        // Удаляем старые ошибки
        const existingErrors = document.querySelector('.test-errors');
        if (existingErrors) {
            existingErrors.remove();
        }

        // Создаем блок с ошибками
        const errorDiv = document.createElement('div');
        errorDiv.className = 'test-errors alert alert-danger mt-3';
        errorDiv.innerHTML = '<strong>Ошибки валидации тестов:</strong><ul>' +
            errors.map(err => `<li>${err}</li>`).join('') +
            '</ul>';

        const testsContainer = document.getElementById('tests-container');
        if (testsContainer && testsContainer.parentNode) {
            testsContainer.parentNode.insertBefore(errorDiv, testsContainer.nextSibling);
            errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
});