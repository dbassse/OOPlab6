#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from models import InvalidInputError, UnknownCommandError
from storage import Library


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        filename="program.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    logging.info("=" * 50)
    logging.info("Запуск программы управления библиотекой")
    logging.info("=" * 50)


def print_help():
    """Вывод справки по командам"""
    print("\n📚 ДОСТУПНЫЕ КОМАНДЫ:")
    print("=" * 40)
    print("add         - добавить новую книгу")
    print("list        - вывести список всех книг")
    print("select <кр> - найти книги по автору, жанру или названию")
    print("save <файл> - сохранить данные в XML-файл")
    print("load <файл> - загрузить данные из XML-файла")
    print("help        - показать эту справку")
    print("exit        - выйти из программы")
    print("=" * 40)


def get_book_info():
    """Получение информации о книге от пользователя"""
    print("\n📖 ДОБАВЛЕНИЕ НОВОЙ КНИГИ")
    print("-" * 30)

    while True:
        try:
            title = input("Название книги: ").strip()
            if not title:
                print("Название не может быть пустым!")
                continue

            author = input("Автор: ").strip()
            if not author:
                print("Автор не может быть пустым!")
                continue

            try:
                year = int(input("Год издания: ").strip())
            except ValueError:
                print("Год должен быть числом!")
                continue

            genre = input("Жанр: ").strip()
            if not genre:
                print("Жанр не может быть пустым!")
                continue

            try:
                pages = int(input("Количество страниц: ").strip())
            except ValueError:
                print("Количество страниц должно быть числом!")
                continue

            return title, author, year, genre, pages

        except KeyboardInterrupt:
            print("\nОтмена ввода.")
            return None


def main():
    """Основная функция программы"""
    # Настройка логирования
    setup_logging()

    # Создание библиотеки
    library = Library()

    print("=" * 50)
    print("📚 ПРОГРАММА УПРАВЛЕНИЯ БИБЛИОТЕКОЙ")
    print("=" * 50)
    print("Введите 'help' для списка команд")
    print("Введите 'exit' для выхода")
    print("=" * 50)

    # Основной цикл обработки команд
    while True:
        try:
            # Запрос команды
            command = input("\n>>> ").strip()

            if not command:
                continue

            # Обработка команды выхода
            if command.lower() == "exit":
                print("Завершение работы программы...")
                logging.info("Программа завершена пользователем")
                break

            # Обработка команды помощи
            elif command.lower() == "help":
                print_help()
                logging.info("Выведена справка по командам")

            # Обработка команды добавления
            elif command.lower() == "add":
                book_info = get_book_info()
                if book_info:
                    try:
                        library.add(*book_info)
                        print("✅ Книга успешно добавлена!")
                    except InvalidInputError as e:
                        print(f"❌ Ошибка: {e}")

            # Обработка команды вывода списка
            elif command.lower() == "list":
                print("\n📚 СПИСОК КНИГ В БИБЛИОТЕКЕ:")
                print(library)
                logging.info("Выведен список всех книг")

            # Обработка команды выборки
            elif command.lower().startswith("select "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    criterion = parts[1]
                    selected_books = library.select(criterion)

                    if selected_books:
                        print(f"\n📖 НАЙДЕНО КНИГ ПО ЗАПРОСУ '{criterion}':")
                        temp_lib = Library(books=selected_books)
                        print(temp_lib)
                    else:
                        print(f"❌ Книги по запросу '{criterion}' не найдены.")
                else:
                    print("❌ Неверный формат команды. Используйте: select <критерий>")

            # Обработка команды сохранения
            elif command.lower().startswith("save "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    filename = parts[1]
                    if not filename.endswith(".xml"):
                        filename += ".xml"
                    try:
                        library.save(filename)
                    except Exception as e:
                        print(f"❌ Ошибка при сохранении: {e}")
                else:
                    print("❌ Неверный формат команды. Используйте: save <имя_файла>")

            # Обработка команды загрузки
            elif command.lower().startswith("load "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    filename = parts[1]
                    try:
                        library.load(filename)
                        print("✅ Данные успешно загружены!")
                    except Exception as e:
                        print(f"❌ Ошибка при загрузке: {e}")
                else:
                    print("❌ Неверный формат команды. Используйте: load <имя_файла>")

            # Обработка неизвестной команды
            else:
                raise UnknownCommandError(command)

        except UnknownCommandError as e:
            print(f"❌ Ошибка: {e}")
            logging.error(f"Неизвестная команда: {command}")

        except KeyboardInterrupt:
            print("\n\nЗавершение работы программы...")
            logging.info("Программа прервана пользователем (Ctrl+C)")
            break

        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            logging.error(f"Неожиданная ошибка: {e}")
            logging.error(f"Тип ошибки: {type(e).__name__}")


if __name__ == "__main__":
    main()
