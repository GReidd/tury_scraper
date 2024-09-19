import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randrange
import json

hotels_url_set = set()


def get_data(url):

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "ru,en;q=0.9",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
    }

    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()  # Проверяет успешность запроса (код 200)
    except requests.RequestException as e:
        print(f"Ошибка запроса данных: {e}")
        return

    result = r.content

    soup = BeautifulSoup(result, "lxml")

    # Находим все блоки с отелями (или турами)
    hotels = soup.find_all(class_="reviews-travel__info")

    print(f"Отелей записано:{len(hotels)}")

    for hotel in hotels:
        # Находим ссылку на отель
        hotel_link = hotel.find("a")
        if hotel_link:
            hotel_page_url = hotel_link.get("href")
            hotels_url_set.add(hotel_page_url)
        else:
            print("Не удалось найти ссылку на отель.")
    sleep(randrange(1, 3))  # Добавляем паузу между запросами, чтобы избежать блокировки


data_dict = []


def read_data():
    try:
        with open("hotels_url_list.txt", encoding="utf-8") as file:
            lines = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("Файл с URL не найден.")
        return
    except IOError as e:
        print(f"Ошибка чтения файла: {e}")
        return

    count = 0
    for line in lines:
        try:
            r = requests.get(line)
            r.raise_for_status()
        except requests.RecursionException as e:
            print(f"Ошибка запроса данных по URL {line}: {e}")
            continue

        result = r.content
        soup = BeautifulSoup(result, "lxml")

        hotel_name = (
            soup.find(class_="h1").text.strip()
            if soup.find(class_="h1")
            else "Нет имени"
        )
        hotel_tags = soup.find_all(class_="tag__item")

        hotel_tags_items = []

        for item in hotel_tags:
            hotel_tags_items.append(item.text.strip())

        hotel_address = (
            soup.find(class_="hotel-info__wrapp").find("span").text.strip()
            if soup.find(class_="hotel-info__wrapp")
            else "Нет адреса"
        )

        hotel_description = (
            soup.find(class_="hotel__text").text.strip()
            if soup.find(class_="hotel__text")
            else "Нет описания"
        )

        data = {
            "hotel_name": hotel_name,
            "hotel_tags": hotel_tags_items,
            "hotel_address": hotel_address,
            "hotel_description": hotel_description,
        }

        data_dict.append(data)
        count += 1
        print(f"Данные #{count} Отеля записаны!")

    sleep(randrange(1, 3))


def write_data():
    try:
        with open("hotels_info.json", "w", encoding="utf-8-sig") as json_file:
            json.dump(data_dict, json_file, indent=4, ensure_ascii=False)
            print(f"Запись данных завершена")
    except Exception as ex:
        print(f"Произошла ошибка записи данных!{ex}")


def save_urls_to_file():
    # Сохраняем уникальные ссылки в файл
    try:
        with open("hotels_url_list.txt", "w", encoding="utf-8") as file:
            for url in hotels_url_set:
                file.write(url + "\n")
        print(f"Всего отелей записано:{len(hotels_url_set)}")
    except Exception as ex:
        print(f"Произошла ошибка записи данных!{ex}")


def main():
    # Проходим по страницам сайта, изменяя параметры пагинации
    for i in range(0, 145, 20):
        get_data(f"https://tury.ru/hotel/?cn=0&ct=0&cat=1317&txt_geo=&srch=&s={i}")

    save_urls_to_file()
    read_data()
    write_data()


if __name__ == "__main__":
    main()
