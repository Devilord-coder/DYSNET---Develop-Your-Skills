import requests
import os


def download_file(Auth_token, filename, disk_folder):
    """Функция для скачивания файла с Яндекс Диска

    Args:
        Auth_token(str): Уникальный токен авторизации
        filename(str): название файла
        disk_folder(str): папка на яндекс диске

    """
    headers = {"Authorization": Auth_token}
    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    params = {
        "path": f"{disk_folder}{filename}"  # Если файл лежит в папке «Загрузки», конечно
    }
    # Если почитаем документацию, то выясним, что придётся делать целых два запроса:
    # 1. Получить ссылку на скачивание файла
    # 2. Скачать файл
    print(f"Получаем ссылку на скачивание файла {filename} с облачного хранилища")
    data = requests.get(url, headers=headers, params=params)
    download_link = data.json()["href"]
    if download_link:
        print("Ссылка получена")
    else:
        print("Ошибка: сслыка не получена")
    print(f"Скачиваем файл {disk_folder}{filename}")
    download_response = requests.get(
        download_link, stream=True
    )  # stream=True — обязательно для больших файлов

    if download_response.status_code != 200:
        print(f"Ошибка скачивания файла {filename}: {download_response.status_code}")
        return
    else:
        download_path = f"static/downloads/{filename}"
        with open(download_path, "wb") as f:
            for chunk in download_response.iter_content(
                chunk_size=8192
            ):  # Скачиваем файл по кусочкам
                f.write(chunk)
        print(f"Файл {filename} успешно скачан в {download_path}")


def download_apps(Auth_token: str):
    """Функция скачивания приложений с Яндекс Диска

    Args:
        Auth_token(str): Уникальный токен авторизации,
        подробнее можно почитать тут ->
        https://lms.yandex.ru/courses/1461/groups/49997/lessons/10361/materials/25962#3
        или тут ->
        https://education.yandex.ru/handbook/python/article/modul-requests
    """
    disk_folder = "/Dysnet/"  # папка на Яндекс Диске
    filenames = ["Windows_Experimentarium.zip"]
    if os.path.exists("static/downloads"):
        continue_downloading = input(
            "Папка static/downloads уже существует. Нужно загружать файлы? (y/n)"
        )
        if continue_downloading.lower().strip() == "y":
            if os.listdir("static/downloads"):
                delete_files = input("Перезаписать все файлы в папке? (y/n)")
                if delete_files.lower().strip() == "y":
                    for file in os.listdir("static/downloads"):
                        os.remove(f"static/downloads/{file}")
        else:
            return
    else:
        os.mkdir("static/downloads")
    print(f"Скачивание приложений в static/downloads/")
    try:
        for filename in filenames:
            if filename in os.listdir("static/downloads"):
                delete_file = input(
                    f"Файл {filename} уже существует, перезаписать его? (y/n)"
                )
                if delete_file.lower().strip() == "y":
                    os.remove(f"static/downloads/{filename}")
                else:
                    continue
            download_file(Auth_token, filename, disk_folder)
    except requests.ConnectionError:
        print("Ошибка подключения к серверу . . .")
    print("Все приложения скачаны")
