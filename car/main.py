#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from models import InvalidSpeedError, SpeedLimitExceededError, UnknownCommandError
from storage import CarRegistry


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        filename="car_speed.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8",
    )
    logging.info("=" * 50)
    logging.info("Запуск программы учета скорости автомобилей")
    logging.info("=" * 50)


def print_help():
    """Вывод справки по командам"""
    print("\n🚗 ДОСТУПНЫЕ КОМАНДЫ:")
    print("=" * 60)
    print("add             - добавить новый автомобиль")
    print("list            - вывести список всех автомобилей")
    print("check <скорость>- проверить скорость по стандарту (200 км/ч)")
    print("speeding        - показать автомобили, превышающие скорость")
    print("brand <марка>   - найти автомобили по марке")
    print("save <файл>     - сохранить данные в XML-файл")
    print("load <файл>     - загрузить данные из XML-файла")
    print("help            - показать эту справку")
    print("exit            - выйти из программы")
    print("=" * 60)


def get_car_info():
    """Получение информации об автомобиле от пользователя"""
    print("\n🚗 ДОБАВЛЕНИЕ НОВОГО АВТОМОБИЛЯ")
    print("-" * 40)

    while True:
        try:
            brand = input("Марка автомобиля: ").strip()
            if not brand:
                print("Марка не может быть пустой!")
                continue

            model = input("Модель: ").strip()
            if not model:
                print("Модель не может быть пустой!")
                continue

            license_plate = input("Государственный номер: ").strip()
            if not license_plate:
                print("Госномер не может быть пустым!")
                continue

            try:
                max_speed = int(
                    input("Максимальная допустимая скорость (км/ч): ").strip()
                )
                if max_speed <= 0:
                    print("Максимальная скорость должна быть положительной!")
                    continue
            except ValueError:
                print("Скорость должна быть числом!")
                continue

            try:
                current_speed = int(input("Текущая скорость (км/ч): ").strip())
                if current_speed < 0:
                    print("Текущая скорость не может быть отрицательной!")
                    continue
            except ValueError:
                print("Скорость должна быть числом!")
                continue

            return brand, model, license_plate, max_speed, current_speed

        except KeyboardInterrupt:
            print("\nОтмена ввода.")
            return None


def main():
    """Основная функция программы"""
    # Настройка логирования
    setup_logging()

    # Создание реестра автомобилей
    registry = CarRegistry()

    print("=" * 70)
    print("🚗 ПРОГРАММА УЧЕТА СКОРОСТИ АВТОМОБИЛЕЙ")
    print("=" * 70)
    print("Стандартная максимальная скорость: 200 км/ч")
    print("Введите 'help' для списка команд")
    print("Введите 'exit' для выхода")
    print("=" * 70)

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
                car_info = get_car_info()
                if car_info:
                    try:
                        registry.add(*car_info)
                        print("✅ Автомобиль успешно добавлен!")
                    except (InvalidSpeedError, SpeedLimitExceededError) as e:
                        print(f"❌ Ошибка: {e}")

            # Обработка команды вывода списка
            elif command.lower() == "list":
                print("\n🚗 СПИСОК АВТОМОБИЛЕЙ В РЕЕСТРЕ:")
                print(registry)
                logging.info("Выведен список всех автомобилей")

            # Обработка команды проверки скорости
            elif command.lower().startswith("check "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    try:
                        speed = int(parts[1].strip())
                        result = registry.check_speed(speed)
                        print(f"✅ {result}")
                        logging.info(
                            f"Проверка скорости: {speed} км/ч - в пределах нормы"
                        )
                    except ValueError:
                        print("❌ Скорость должна быть числом!")
                    except SpeedLimitExceededError as e:
                        print(f"🚨 SpeedLimitExceededError: {e}")
                        logging.warning(f"Превышение скорости: {speed} км/ч")
                else:
                    print("❌ Неверный формат команды. Используйте: check <скорость>")

            # Обработка команды показа превышающих скорость
            elif command.lower() == "speeding":
                speeding_cars = registry.select_speeding()

                if speeding_cars:
                    print(
                        f"\n🚨 АВТОМОБИЛИ, ПРЕВЫШАЮЩИЕ СКОРОСТЬ ({len(speeding_cars)} шт.):"
                    )
                    temp_registry = CarRegistry(cars=speeding_cars)
                    print(temp_registry)
                else:
                    print("✅ Нет автомобилей, превышающих скорость.")

            # Обработка команды поиска по марке
            elif command.lower().startswith("brand "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    brand = parts[1]
                    selected_cars = registry.select_by_brand(brand)

                    if selected_cars:
                        print(
                            f"\n🔍 АВТОМОБИЛИ МАРКИ '{brand.upper()}' ({len(selected_cars)} шт.):"
                        )
                        temp_registry = CarRegistry(cars=selected_cars)
                        print(temp_registry)
                    else:
                        print(f"❌ Автомобили марки '{brand}' не найдены.")
                else:
                    print("❌ Неверный формат команды. Используйте: brand <марка>")

            # Обработка команды сохранения
            elif command.lower().startswith("save "):
                parts = command.split(maxsplit=1)
                if len(parts) == 2:
                    filename = parts[1]
                    if not filename.endswith(".xml"):
                        filename += ".xml"
                    try:
                        registry.save(filename)
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
                        registry.load(filename)
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
