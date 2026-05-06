"""Все модели для работы с БД"""

from .models.users_model import User
from .models.cursive_printing_models.modes_model import CursivePrintingModes
from .models.cursive_printing_models.words_model import CursivePrintingWords
from .models.cursive_printing_models.statistics_model import CursivePrintingStatistics
from .models.python_models.task_model import PythonTask
from .models.python_models.test_model import PythonTest
from .models.english_models.words_model import EnglishWords
from .models.english_models.topics_model import EnglishTopics
from .models.english_models.texts_model import EnglishTexts
from .models.english_models.statistic_model import EnglishStatistics
from .models.clicker_models.statistics_model import ClickerStatistics
from .models.news_model import News
from .models.articles_model import Article
from .models.themes_model import Theme
from .models.python_models.python_statistics_model import PythonStatistics
