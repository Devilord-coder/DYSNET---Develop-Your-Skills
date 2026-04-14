from ..db_session import *
from ..__all_models import PythonTask, PythonTest

Task = PythonTask
Test = PythonTest
DATABASE_PATH = "data/server.db"

"""
from server import DATABASE_PATH
from backend.database import db_session, __all_models

Task = __all_models.PythonTask
Test = __all_models.PythonTest

{
    "name": "Котики",
    "task_type": "junior",
    "text": "Напишите программу, которая считывает одну строку, после чего выводит «МЯУ», если в введённой строке есть подстрока «кот», и «ГАВ» в противном случае.",
    "tests": [
        ["Извините, пожалуйста, вы не подскажете, который час?", "МЯУ"],
        ["Кто я? кто", "ГАВ"]
    ]
}

tasks = [
    (Task(
        ""
    ))
]

db_session.global_init(DATABASE_PATH)
db_sess = db_session.create_session()
for t in tasks:
    task = t.copy()
    del task["tests"]
    task = Task(**task)
    db_sess.add(task)
    for tst in t["tests"]:
        test = Test(task_id=task.id, args=tst[0], result=tst[1])
        db_sess.add(test)
    db_sess.commit()

"""