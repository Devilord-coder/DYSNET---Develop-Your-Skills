class Autocomplete {
    constructor(inputId, options = {}) {
        this.input = document.getElementById(inputId);
        if (!this.input) {
            console.error(`Элемент с id "${inputId}" не найден`);
            return;
        }

        this.options = {
            data: [],
            maxItems: 10,
            minChars: 1,
            onSelect: null,
            ...options
        };

        this.dropdown = null;
        this.selectedIndex = -1;
        this.currentValue = '';

        this.init();
    }

    init() {
        // Создаем dropdown если его нет
        const existingDropdown = this.input.parentElement.querySelector('.autocomplete-dropdown');
        if (!existingDropdown) {
            this.createDropdown();
        } else {
            this.dropdown = existingDropdown;
        }

        // Добавляем обработчики событий
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('focus', () => this.handleFocus());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('click', (e) => this.handleClickOutside(e));

        // Добавляем CSS класс
        this.input.classList.add('autocomplete-input');
    }

    createDropdown() {
        const wrapper = this.input.parentElement;
        const dropdown = document.createElement('div');
        dropdown.className = 'autocomplete-dropdown';
        dropdown.style.display = 'none';
        dropdown.innerHTML = `
            <div class="autocomplete-header">
                <i class="bi bi-lightbulb"></i> Предлагаемые темы
            </div>
            <div class="autocomplete-options"></div>
            <div class="autocomplete-footer">
                <small><i class="bi bi-plus-circle"></i> Можно ввести свою тему, если её нет в списке</small>
            </div>
        `;
        wrapper.appendChild(dropdown);
        this.dropdown = dropdown;
    }

    handleInput() {
        const value = this.input.value;
        this.currentValue = value;

        if (value.length >= this.options.minChars) {
            this.filterSuggestions(value);
        } else {
            this.hideDropdown();
        }
    }

    handleFocus() {
        const value = this.input.value;
        if (value.length >= this.options.minChars) {
            this.filterSuggestions(value);
        }
    }

    filterSuggestions(query) {
        const filtered = this.options.data
            .filter(item => item.toLowerCase().includes(query.toLowerCase()))
            .slice(0, this.options.maxItems);

        if (filtered.length > 0) {
            this.renderSuggestions(filtered, query);
            this.showDropdown();
        } else {
            this.renderNoResults(query);
            this.showDropdown();
        }

        this.selectedIndex = -1;
    }

    renderSuggestions(suggestions, query) {
        const optionsContainer = this.dropdown.querySelector('.autocomplete-options');
        if (!optionsContainer) return;

        optionsContainer.innerHTML = '';

        suggestions.forEach((suggestion, index) => {
            const option = document.createElement('div');
            option.className = 'autocomplete-option';
            option.setAttribute('data-value', suggestion);
            option.setAttribute('data-index', index);

            // Подсвечиваем совпадения
            const highlightedText = this.highlightMatches(suggestion, query);

            option.innerHTML = `
                <i class="bi bi-tag"></i>
                <span>${highlightedText}</span>
            `;

            option.addEventListener('click', () => this.selectSuggestion(suggestion));
            optionsContainer.appendChild(option);
        });
    }

    renderNoResults(query) {
        const optionsContainer = this.dropdown.querySelector('.autocomplete-options');
        if (!optionsContainer) return;

        optionsContainer.innerHTML = `
            <div class="autocomplete-no-results">
                <i class="bi bi-emoji-frown"></i>
                <p>Ничего не найдено для "<strong>${this.escapeHtml(query)}</strong>"</p>
                <small>Вы можете ввести свою тему</small>
            </div>
        `;
    }

    highlightMatches(text, query) {
        if (!query) return text;

        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    escapeHtml(string) {
        const div = document.createElement('div');
        div.textContent = string;
        return div.innerHTML;
    }

    selectSuggestion(value) {
        this.input.value = value;
        this.currentValue = value;
        this.hideDropdown();

        // Триггерим событие input для форм
        const event = new Event('input', { bubbles: true });
        this.input.dispatchEvent(event);

        if (this.options.onSelect && typeof this.options.onSelect === 'function') {
            this.options.onSelect(value);
        }
    }

    handleKeydown(e) {
        const options = this.dropdown.querySelectorAll('.autocomplete-option');
        if (options.length === 0) return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, options.length - 1);
                this.updateSelectedOption(options);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.updateSelectedOption(options);
                break;

            case 'Enter':
                if (this.selectedIndex >= 0 && options[this.selectedIndex]) {
                    e.preventDefault();
                    const selectedValue = options[this.selectedIndex].getAttribute('data-value');
                    this.selectSuggestion(selectedValue);
                }
                break;

            case 'Escape':
                this.hideDropdown();
                break;
        }
    }

    updateSelectedOption(options) {
        options.forEach((option, index) => {
            if (index === this.selectedIndex) {
                option.classList.add('selected');
                option.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            } else {
                option.classList.remove('selected');
            }
        });
    }

    showDropdown() {
        if (this.dropdown) {
            this.dropdown.style.display = 'block';
        }
    }

    hideDropdown() {
        if (this.dropdown) {
            this.dropdown.style.display = 'none';
        }
    }

    handleClickOutside(e) {
        if (this.dropdown && !this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
            this.hideDropdown();
        }
    }

    // Обновить данные автодополнения
    updateData(newData) {
        this.options.data = newData;
    }

    // Получить текущее значение
    getValue() {
        return this.input.value;
    }

    // Очистить поле
    clear() {
        this.input.value = '';
        this.currentValue = '';
        this.hideDropdown();
    }
}

// Экспортируем для использования в браузере
window.Autocomplete = Autocomplete;