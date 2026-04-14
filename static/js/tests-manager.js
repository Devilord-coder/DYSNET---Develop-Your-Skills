// static/js/tests-manager.js

class TestsManager {
    constructor(options = {}) {
        this.containerId = options.containerId || 'tests-container';
        this.addButtonId = options.addButtonId || 'add-test';
        this.maxTests = options.maxTests || 20;
        this.minTests = options.minTests || 1;
        this.testIndex = options.initialIndex || 0;

        this.init();
    }

    init() {
        this.container = document.getElementById(this.containerId);
        this.addButton = document.getElementById(this.addButtonId);

        if (!this.container || !this.addButton) {
            console.error('Container or add button not found');
            return;
        }

        this.addButton.addEventListener('click', () => this.addTest());
        this.initRemoveButtons();
    }

    initRemoveButtons() {
        const removeButtons = this.container.querySelectorAll('.remove-test');
        removeButtons.forEach(btn => {
            // Удаляем старый обработчик, если есть
            btn.removeEventListener('click', this.handleRemoveClick);
            // Добавляем новый
            btn.addEventListener('click', (e) => this.handleRemoveClick(e));
        });
    }

    handleRemoveClick(e) {
        const testItem = e.target.closest('.test-item');
        if (testItem && this.container.children.length > this.minTests) {
            testItem.remove();
            this.reindexTests();
        } else if (this.container.children.length <= this.minTests) {
            alert(`Должен быть хотя бы один тест`);
        }
    }

    addTest() {
        if (this.container.children.length >= this.maxTests) {
            alert(`Максимум ${this.maxTests} тестов`);
            return;
        }

        const testHtml = this.createTestHtml(this.testIndex);
        this.container.insertAdjacentHTML('beforeend', testHtml);

        // Добавляем обработчик для новой кнопки удаления
        const newTest = this.container.lastElementChild;
        const removeBtn = newTest.querySelector('.remove-test');
        if (removeBtn) {
            removeBtn.addEventListener('click', (e) => this.handleRemoveClick(e));
        }

        this.testIndex++;
        this.reindexTests();
    }

    createTestHtml(index) {
        return `
            <div class="test-item card mb-3">
                <div class="card-body">
                    <div class="mb-2">
                        <label class="form-label">Ввод</label>
                        <textarea class="form-control"
                                  name="tests-${index}-input_data"
                                  rows="2"></textarea>
                    </div>
                    <div class="mb-2">
                        <label class="form-label">Ожидаемый результат</label>
                        <textarea class="form-control"
                                  name="tests-${index}-expected_output"
                                  rows="2"></textarea>
                    </div>
                    <button type="button" class="btn btn-danger btn-sm remove-test">
                        <i class="bi bi-trash me-1"></i>Удалить тест
                    </button>
                </div>
            </div>
        `;
    }

    reindexTests() {
        const tests = this.container.querySelectorAll('.test-item');
        tests.forEach((test, idx) => {
            const inputs = test.querySelectorAll('textarea');
            inputs.forEach(input => {
                const name = input.getAttribute('name');
                if (name) {
                    const newName = name.replace(/tests-\d+-(input_data|expected_output)/, `tests-${idx}-$1`);
                    input.setAttribute('name', newName);
                }
            });
        });
        this.testIndex = tests.length;
    }

    getTestCount() {
        return this.container.children.length;
    }

    validateTests() {
        const tests = this.container.querySelectorAll('.test-item');
        let hasValidTest = false;
        let errors = [];

        tests.forEach((test, index) => {
            const inputData = test.querySelector('textarea[name$="input_data"]');
            const expectedOutput = test.querySelector('textarea[name$="expected_output"]');

            if (inputData && expectedOutput) {
                const inputValue = inputData.value.trim();
                const outputValue = expectedOutput.value.trim();

                if (inputValue || outputValue) {
                    if (inputValue && outputValue) {
                        hasValidTest = true;
                    } else {
                        errors.push(`Тест ${index + 1}: заполнены не все поля`);
                    }
                }
            }
        });

        if (!hasValidTest && tests.length > 0) {
            errors.push('Необходимо добавить хотя бы один полностью заполненный тест');
        }

        return {
            isValid: errors.length === 0 && hasValidTest,
            errors: errors
        };
    }
}

// Экспортируем для использования в браузере
window.TestsManager = TestsManager;