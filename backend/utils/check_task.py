from flask import g
from backend.database.__all_models import PythonTask, PythonTest
import os
import subprocess
import time
import sys


def check_task(code: str, task_id: int, filename: str) -> str:
    """Функция для проверки задания"""
    
    print(f"Проверяем задание {task_id}")

    def del_file():
        os.remove(filename + '.py')

    db_sess = g.db_session

    with open(filename + '.py', 'w', encoding='utf-8') as solution:
        solution.write(code)

    results = []
    for test in db_sess.query(PythonTest).filter(PythonTest.task_id == task_id).all():
        # Замеряем время выполнения
        start_time = time.perf_counter()
        print(f"test {test.id} - {start_time}")

        input_data = test.args
        result_data = ""
        accept = False
        try:
            # Запускаем процесс solution.py, передаём input_data в stdin
            result = subprocess.run(
                [sys.executable, filename + '.py'],  # sys.executable для кросс-платформенности
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,          # Работаем с текстом (строки), а не с байтами
                encoding='utf-8',
                check=False         # Не вызывать исключение при ненулевом коде возврата
            )
        except Exception as e:
            elapsed_time = time.perf_counter() - start_time
            result_data += f"""Критическая ошибка при запуске процесса: {e}
"Время до ошибки: {elapsed_time:.6f} сек\n"""
            print(result_data)
            results.append(result_data)
            del_file()
            return results

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        stdin = input_data
        stdout = result.stdout
        stderr = result.stderr
        time_remained = f"{elapsed_time:.6f} сек"
        returncode = result.returncode

        if result.stdout.strip() == test.result.strip():
            accept = True
        results.append({
                "test_id": test.id,
                "accept": accept,
                "stdin": stdin,
                "stdout": stdout,
                "stderr": stderr,
                "time": time_remained,
                'returncode': returncode,
                "answer": test.result

            })
        if not accept:
            print("Данные не сходятся")
            del_file()
            return results
        del_file()
        return results


def run_solution_with_input(solution_file, input_file, output_file):
    """
    Запускает solution_file, передавая ему содержимое input_file как stdin.
    Записывает stdout, stderr и время выполнения в output_file.
    """
    try:
        # Читаем входные данные
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = f.read()
    except FileNotFoundError:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Ошибка: файл {input_file} не найден.\n")
        return
    except Exception as e:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Ошибка при чтении {input_file}: {e}\n")
        return

    # Замеряем время выполнения
    start_time = time.perf_counter()

    try:
        # Запускаем процесс solution.py, передаём input_data в stdin
        result = subprocess.run(
            [sys.executable, solution_file],  # sys.executable для кросс-платформенности
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,          # Работаем с текстом (строки), а не с байтами
            encoding='utf-8',
            check=False         # Не вызывать исключение при ненулевом коде возврата
        )
    except FileNotFoundError:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Ошибка: файл {solution_file} не найден.\n")
        return
    except Exception as e:
        elapsed_time = time.perf_counter() - start_time
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Критическая ошибка при запуске процесса: {e}\n")
            f.write(f"Время до ошибки: {elapsed_time:.6f} сек\n")
        return

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # Записываем результат в output.txt
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=== РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ ===\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\n=== СТАНДАРТНЫЙ ПОТОК ОШИБОК ===\n")
            f.write(result.stderr)
        f.write(f"\n=== ВРЕМЯ ВЫПОЛНЕНИЯ ===\n")
        f.write(f"{elapsed_time:.6f} сек\n")
        if result.returncode != 0:
            f.write(f"\n=== КОД ВОЗВРАТА ===\n")
            f.write(f"{result.returncode}\n")

    # Опционально: вывести в консоль сообщение об успехе
    print(f"Готово. Результат записан в {output_file}")
    print(f"Время выполнения: {elapsed_time:.6f} сек")

if __name__ == "__main__":
    # Укажите имена файлов (можно изменить)
    SOLUTION_FILE = "solution.py"
    INPUT_FILE = "input.txt"
    OUTPUT_FILE = "output.txt"

    run_solution_with_input(SOLUTION_FILE, INPUT_FILE, OUTPUT_FILE)