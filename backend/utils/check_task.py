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

        if test.args:
            input_data = '\n'.join(list(map(lambda x: x.strip(), test.args.split('\n'))))
        else:
            input_data = ""
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
                "answer": test.result,
                "code": code

            })
        if not accept:
            print("Данные не сходятся")
            del_file()
            return results
    del_file()
    return results