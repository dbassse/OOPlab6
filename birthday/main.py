#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from models import InvalidDateError, InvalidMonthError, UnknownCommandError
from storage import BirthdayBook


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        filename="birthdays.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    logging.info("=" * 50)
    logging.info("Запуск программы учета дней рождения")
    logging.info("=" * 50)


def print_help():
    """Вывод справки по командам"""
    print("\n🎂 ДОСТУПНЫЕ КОМАНДЫ:")
    print("=" * 50)
    print("add           - добавить нового человека")
    print("list          - вывести список всех людей")
    print("filter <мес>  - показать именинников в указанном месяце (1-12)")
    print("save <файл>   - сохранить данные в XML-файл")
    print("load <файл>   - загрузить данные из XML-файла")
    print("help          - показать эту справку")
    print("exit          - выйти из программы")
    print("=" * 50)
    print("\n📅 Примеры использования фильтра:")
    print("  filter 1    - показать январских именинников")
    print("  filter 12   - показать декабрьских именинников")


def get_person_info():
    """Получение информации о человеке от пользователя"""
    print("\n👤 ДОБАВЛЕНИЕ НОВОГО ЧЕЛОВЕКА")
    print("-" * 35)

    while True:
        try:
            last_name = input("Фамилия: ").strip()
            if not last_name:
                print("Фамилия не может быть пустой!")
                continue

            first_name = input("Имя: ").strip()
            if not first_name:
                print("Имя не может быть пустым!")
                continue

            phone = input("Номер телефона: ").strip()
            if not phone:
                print("Номер телефона не может быть пустым!")
                continue

            print("\n📅 Введите дату рождения:")

            while True:
                try:
                    day = int(input("  День (1-31): ").strip())
                    break
                except ValueError:
                    print("  День должен быть числом!")

            while True:
                try:
                    month = int(input("  Месяц (1-12): ").strip())
                    if month < 1 or month > 12:
                        print("  Месяц должен быть от 1 до 12!")
                        continue
                    break
                except ValueError:
                    print("  Месяц должен быть числом!")

            while True:
                try:
                    year = int(input("  Год (1900-2024): ").strip())
                    break
                except ValueError:
                    print("  Год должен быть числом!")

            return last_name, first_name, phone, day, month, year

        except KeyboardInterrupt:
            print("\nОтмена ввода.")
            return None


def main():
    """Основная функция программы"""
    # Настройка логирования
    setup_logging()

    # Создание книги дней рождения
    book = BirthdayBook()

    print("=" * 60)
    print("🎂 ПРОГРАММА УЧЕТА ДНЕЙ РОЖДЕНИЯ С ФИЛЬТРАЦИЕЙ ПО МЕСЯЦУ")
    print("=" * 60)
    print("Введите 'help' для списка команд")
    print("Введите 'exit' для выхода")
    print("=" * 60)

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
                person_info = get_person_info()
                if person_info:
                    try:
                        book.add(*person_info)
                        print("✅ Человек успешно добавлен!")
                    except (InvalidDateError, InvalidMonthError) as e:
                        print(f"❌ Ошибка: {e}")

            # Обработка команды вывода списка
            elif command.lower() == "list":
                print("\n📖 СПИСОК ЛЮДЕЙ В КНИГЕ ДНЕЙ РОЖДЕНИЯ:")
                print(book)
                logging.info("Выведен список всех людей")

            # Обработка команды фильтрации по месяцу
            elif command.lower().startswith("filter "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    try:
                        month = int(parts[1].strip())
                        if month < 1 or month > 12:
                            print("❌ Месяц должен быть числом от 1 до 12")
                            logging.error(f"Некорректный месяц: {month}")
                            continue

                        result = book.display_filtered(month)
                        print(result)

                        # Если список пуст, выводим сообщение
                        if "не найдено" in result:
                            month_names = [
                                "январе",
                                "феврале",
                                "марте",
                                "апреле",
                                "мае",
                                "июне",
                                "июле",
                                "августе",
                                "сентябре",
                                "октябре",
                                "ноябре",
                                "декабре",
                            ]
                            month_name = month_names[month - 1]
                            print(f"\nℹ️  Именинников в {month_name} нет.")

                    except ValueError:
                        print("❌ Месяц должен быть числом от 1 до 12")
                        logging.error(f"Некорректный ввод месяца: {parts[1]}")
                else:
                    print(
                        "❌ Неверный формат команды. Используйте: filter <номер_месяца>"
                    )

            # Обработка команды сохранения
            elif command.lower().startswith("save "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    filename = parts[1]
                    if not filename.endswith(".xml"):
                        filename += ".xml"
                    try:
                        book.save(filename)
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
                        book.load(filename)
                    except Exception as e:
                        print(f"❌ Ошибка при загрузке: {e}")
                else:
                    print("❌ Неверный формат команды. Используйте: load <имя_файла>")

            # Обработка неизвестной команды
            else:
                raise UnknownCommandError(command)

        except UnknownCommandError as e:
            print(f"❌ Ошибка: {e}")
            print("ℹ️  Введите 'help' для списка доступных команд")
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
