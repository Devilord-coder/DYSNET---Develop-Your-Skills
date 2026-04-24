from flask import (
    Blueprint, render_template,
    request, redirect, session,
    g, jsonify, make_response,
    url_for
)

# Формы
from backend.forms import AddTaskForm, CodeForm

# БД
from backend.database.__all_models import PythonTask, PythonTest
from backend.database import db_session

# Работа с admin_api
from .admin_api import admin_required

# Отдельная ветка
bp = Blueprint("python", __name__, template_folder="templates")


@bp.route("/tasks/debug", methods=['POST'])
def debug_form():
    return jsonify(dict(request.form))


@bp.route("/tasks/check", methods=["GET", "POST"])
def check_answer():
    return ""


@bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    db_sess = g.db_session
    task = db_sess.get(PythonTask, task_id)
    if not task:
        return make_response(jsonify({'error': 'Not found'}), 404)
    form = CodeForm()
    return render_template(
        "python/task.html", task_title=task.name,
        task_text=task.text, form=form
        )


@bp.route("/api/tasks/<string:level>", methods=["GET"])
def get_tasks(level):
    db_sess = g.db_session
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == level).all()
    if not tasks:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'tasks': [task.to_dict(only=(
                "name", "task_type", "text"
            )) for task in tasks]
        }
    )


@bp.route("/choose_level")
def choose_level():
    """Выбор уровня сложности"""

    return render_template("python/choose_level.html", title="Выбор режима")


@bp.route("/tasks", methods=["POST", "GET"])
def tasks():
    """Просмотр заданий"""

    if request.method == "POST":
        level = request.form.get("level")
        session['level'] = level
        print(session['level'])
        return redirect(f"tasks/{session['level']}")

    db_sess = g.db_session
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == session['level']).all()

    ...

    return render_template(
        "python/tasks.html",
        tasks=tasks,
        level=session['level']
    )


@bp.route("/tasks/add", methods=['GET', 'POST'])
@admin_required
def add_task():
    """Добавление заданий"""
    
    # Проверяем, выбран ли уровень
    if 'level' not in session:
        return redirect(url_for('python.choose_level'))
    
    form = AddTaskForm()
    db_sess = g.db_session
    
    # При GET-запросе добавляем один пустой тест
    if request.method == 'GET' and len(form.tests) == 0:
        form.tests.append_entry()
    
    if request.method == 'POST':
        # Вручную валидируем CSRF
        from flask_wtf.csrf import validate_csrf
        try:
            validate_csrf(request.form.get('csrf_token'))
        except:
            form.csrf_token.errors.append('CSRF token missing or invalid')
            print()
            return render_template("python/add_task.html", level=session['level'], form=form)
        
        # Валидируем основные поля
        form.name.data = request.form.get('name')
        form.text.data = request.form.get('text')
        
        name_error = None
        text_error = None
        
        if not form.name.data or len(form.name.data) < 3:
            name_error = 'Название должно содержать минимум 3 символа'
            form.name.errors = list(form.name.errors)
            form.name.errors.append(name_error)
        
        if not form.text.data or len(form.text.data) < 10:
            text_error = 'Текст задания должен содержать минимум 10 символов'
            form.text.errors = list(form.text.errors)
            form.text.errors.append(text_error)
        
        # Собираем тесты из формы
        tests_data = []
        
        # Проходим по всем полям формы
        for key, value in request.form.items():
            # Ищем поля с input_data
            if key.endswith('input_data'):
                import re
                # Извлекаем индекс: tests-0-input_data -> 0
                match = re.search(r'tests-(\d+)-input_data', key)
                if match:
                    idx = int(match.group(1))
                    # Убеждаемся, что список достаточно большой
                    while len(tests_data) <= idx:
                        tests_data.append({'input': '', 'output': ''})
                    tests_data[idx]['input'] = value.strip()
            
            # Ищем поля с expected_output
            elif key.endswith('expected_output'):
                import re
                match = re.search(r'tests-(\d+)-expected_output', key)
                if match:
                    idx = int(match.group(1))
                    while len(tests_data) <= idx:
                        tests_data.append({'input': '', 'output': ''})
                    tests_data[idx]['output'] = value.strip()
        
        # Отладка: выводим собранные тесты
        print(f"Собрано тестов: {len(tests_data)}")
        for i, test in enumerate(tests_data):
            print(f"Тест {i}: input='{test['input']}', output='{test['output']}'")
        
                # Валидируем тесты
        has_valid_test = False
        test_errors = []
        has_errors = False
        
        for idx, test_data in enumerate(tests_data):
            input_val = test_data.get('input', '')
            output_val = test_data.get('output', '')
            
            # Проверяем, заполнен ли тест (хотя бы одно поле не пустое)
            if input_val or output_val:
                if input_val and output_val:
                    has_valid_test = True
                else:
                    test_errors.append(f'Тест {idx + 1}: заполнены не все поля (ввод: {"есть" if input_val else "пусто"}, вывод: {"есть" if output_val else "пусто"})')
        
        if not has_valid_test and len(tests_data) > 0:
            test_errors.append('Необходимо добавить хотя бы один полностью заполненный тест')
        
        if test_errors:
            form.tests.errors = test_errors
            has_errors = True
        
        # Если есть ошибки, показываем форму снова
        if has_errors:
            return render_template("python/add_task.html", level=session['level'], form=form)
        
        # Если есть ошибки, показываем форму
        if not form.is_submitted():
            return render_template("python/add_task.html", level=session['level'], form=form)
        """
        if name_error or text_error or test_errors:
            # Добавляем ошибки тестов в форму
            if test_errors:
                form.tests.errors = test_errors
            print("THERE ARE ERRORS IN FORM")
            return render_template("python/add_task.html", level=session['level'], form=form)
        """
        
        # Сохраняем задание
        task = PythonTask(
            name=form.name.data,
            task_type=session['level'],
            text=form.text.data
        )
        db_sess.add(task)
        print(f"Добавлено задание {task.name}")
        db_sess.flush()  # Получаем task.id
        
        saved_tests_count = 0
        for test_data in tests_data:
            input_val = test_data.get('input', '').strip()
            output_val = test_data.get('output', '').strip()
            
            if input_val and output_val:  # Сохраняем только полностью заполненные тесты
                test = PythonTest(
                    task_id=task.id,
                    args=input_val,
                    result=output_val
                )
                db_sess.add(test)
                saved_tests_count += 1
                print(f"Добавлен тест {saved_tests_count}: {input_val} -> {output_val}")
        
        db_sess.commit()
        return redirect(url_for('python.tasks'))
    
    return render_template("python/add_task.html", level=session['level'], form=form)


@bp.route("/tasks/junior")
def junior():
    """Уровень сложности Junior"""
    
    db_sess = g.db_session
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == 'junior').all()

    return render_template(
        "python/tasks.html",
        tasks=tasks,
        level="junior"
    )


@bp.route("/tasks/middle")
def middle():
    """Уровень сложности Middle"""
    
    db_sess = g.db_session
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == 'middle').all()

    return render_template(
        "python/tasks.html",
        tasks=tasks,
        level="middle"
    )


@bp.route("/tasks/senior")
def senior():
    """Уровень сложности Senior"""
    
    db_sess = g.db_session
    tasks = db_sess.query(PythonTask).filter(PythonTask.task_type == 'senior').all()

    return render_template(
        "python/tasks.html",
        tasks=tasks,
        level="senior"
    )