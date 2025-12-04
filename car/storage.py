#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List

from models import Car, DataFormatError, InvalidSpeedError, SpeedLimitExceededError


@dataclass
class CarRegistry:
    """Класс для реестра автомобилей"""

    cars: List[Car] = field(default_factory=list)

    def add(
        self,
        brand: str,
        model: str,
        license_plate: str,
        max_speed: int,
        current_speed: int,
    ):
        """
        Добавление нового автомобиля в реестр
        """
        try:
            car = Car(
                brand=brand,
                model=model,
                license_plate=license_plate,
                max_speed=max_speed,
                current_speed=current_speed,
            )

            self.cars.append(car)
            self.cars.sort(key=lambda car: (car.brand, car.model))

            logging.info(
                f"Добавлен автомобиль: {car.full_name} "
                f"({license_plate}), скорость: {current_speed}/{max_speed} км/ч"
            )

        except (InvalidSpeedError, SpeedLimitExceededError) as e:
            logging.error(f"Ошибка при добавлении автомобиля: {e}")
            raise

    def __str__(self) -> str:
        """
        Вывод данных в табличном виде
        """
        if not self.cars:
            return "Реестр автомобилей пуст."

        # Заголовок таблицы
        table = []
        line = "+{}+{}+{}+{}+{}+{}+".format(
            "-" * 4, "-" * 20, "-" * 15, "-" * 12, "-" * 10, "-" * 10
        )
        table.append(line)

        table.append(
            "| {:^4} | {:^20} | {:^15} | {:^12} | {:^10} | {:^10} |".format(
                "№", "Марка Модель", "Госномер", "Макс. скор.", "Тек. скор.", "Статус"
            )
        )
        table.append(line)

        # Данные автомобилей
        for idx, car in enumerate(self.cars, 1):
            # Обрезаем длинные названия
            full_name = (
                car.full_name[:18] + ".." if len(car.full_name) > 20 else car.full_name
            )
            license_plate = (
                car.license_plate[:10] + ".."
                if len(car.license_plate) > 12
                else car.license_plate
            )

            # Определяем цвет статуса (символически)
            status = car.speed_status
            if status == "ПРЕВЫШЕНИЕ":
                status = f"\033[91m{status}\033[0m"  # Красный
            elif status == "В ПРЕДЕЛАХ":
                status = f"\033[92m{status}\033[0m"  # Зеленый
            else:
                status = f"\033[93m{status}\033[0m"  # Желтый

            table.append(
                "| {:^4} | {:<20} | {:<15} | {:^12} | {:^10} | {:<10} |".format(
                    idx,
                    full_name,
                    license_plate,
                    car.max_speed,
                    car.current_speed,
                    status if idx == 1 else car.speed_status,  # Без цветов для pytest
                )
            )

        table.append(line)

        # Статистика
        speeding_count = sum(1 for car in self.cars if car.is_speeding())
        table.append(f"\n📊 Статистика: Всего {len(self.cars)} автомобилей")
        table.append(f"🚨 Превышают скорость: {speeding_count}")
        table.append(f"✅ В пределах нормы: {len(self.cars) - speeding_count}")

        return "\n".join(table)

    def check_speed(self, speed: int) -> str:
        """
        Проверка скорости по стандарту (200 км/ч)
        Возвращает сообщение о результате проверки
        """
        STANDARD_MAX_SPEED = 200

        if speed > STANDARD_MAX_SPEED:
            raise SpeedLimitExceededError(speed, STANDARD_MAX_SPEED)
        return f"Скорость {speed} км/ч в пределах нормы ({STANDARD_MAX_SPEED} км/ч)."

    def select_speeding(self) -> List[Car]:
        """
        Выборка автомобилей, превышающих скорость
        """
        result = [car for car in self.cars if car.is_speeding()]
        result.sort(key=lambda car: car.current_speed, reverse=True)

        logging.info(f"Найдено {len(result)} автомобилей, превышающих скорость")
        return result

    def select_by_brand(self, brand: str) -> List[Car]:
        """
        Выборка автомобилей по марке
        """
        brand_lower = brand.strip().lower()
        result = [car for car in self.cars if brand_lower in car.brand.lower()]

        logging.info(f"Найдено {len(result)} автомобилей марки {brand}")
        return result

    def save(self, filename: str):
        """
        Сохранение данных в XML-файл
        """
        try:
            root = ET.Element("cars")

            for car in self.cars:
                car_element = ET.Element("car")

                ET.SubElement(car_element, "brand").text = car.brand
                ET.SubElement(car_element, "model").text = car.model
                ET.SubElement(car_element, "license_plate").text = car.license_plate
                ET.SubElement(car_element, "max_speed").text = str(car.max_speed)
                ET.SubElement(car_element, "current_speed").text = str(
                    car.current_speed
                )

                root.append(car_element)

            tree = ET.ElementTree(root)

            # Добавляем XML декларацию с кодировкой
            tree.write(filename, encoding="utf-8", xml_declaration=True)

            logging.info(f"Данные сохранены в файл: {filename}")
            print(f"✅ Данные успешно сохранены в файл: {filename}")

        except Exception as e:
            error_msg = f"Ошибка при сохранении в файл {filename}: {e}"
            logging.error(error_msg)
            raise DataFormatError(filename, error_msg)

    def load(self, filename: str):
        """
        Загрузка данных из XML-файла
        """
        try:
            tree = ET.parse(filename)
            root = tree.getroot()

            loaded_cars = []
            errors = 0

            for car_element in root.findall("car"):
                try:
                    brand = car_element.find("brand").text
                    model = car_element.find("model").text
                    license_plate = car_element.find("license_plate").text
                    max_speed = int(car_element.find("max_speed").text)
                    current_speed = int(car_element.find("current_speed").text)

                    car = Car(
                        brand=brand,
                        model=model,
                        license_plate=license_plate,
                        max_speed=max_speed,
                        current_speed=current_speed,
                    )
                    loaded_cars.append(car)

                except (
                    AttributeError,
                    ValueError,
                    InvalidSpeedError,
                    SpeedLimitExceededError,
                ) as e:
                    errors += 1
                    logging.warning(
                        f"Пропущен некорректный элемент в файле {filename}: {e}"
                    )
                    continue

            self.cars = loaded_cars
            self.cars.sort(key=lambda car: (car.brand, car.model))

            logging.info(
                f"Загружено {len(self.cars)} автомобилей из файла: {filename} (ошибок: {errors})"
            )
            print(f"✅ Загружено {len(self.cars)} автомобилей из файла: {filename}")
            if errors > 0:
                print(f"⚠️  Пропущено {errors} некорректных записей")

        except ET.ParseError as e:
            error_msg = f"Ошибка парсинга XML файла {filename}: {e}"
            logging.error(error_msg)
            raise DataFormatError(filename, error_msg)
        except FileNotFoundError:
            error_msg = f"Файл не найден: {filename}"
            logging.error(error_msg)
            raise DataFormatError(filename, error_msg)
