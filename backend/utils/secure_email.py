from werkzeug.utils import secure_filename


def secure_email(user):
    """Возвращает почту пользователя переобразованную для названия файла"""

    return secure_filename(user.email.replace("@", "_at_").replace(".", "_dot_"))
