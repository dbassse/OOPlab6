#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List

from models import DataFormatError, InvalidDateError, InvalidMonthError, Person


@dataclass
class BirthdayBook:
    """Класс для коллекции дней рождения"""

    people: List[Person] = field(default_factory=list)

    def add(
        self,
        last_name: str,
        first_name: str,
        phone: str,
        day: int,
        month: int,
        year: int,
    ):
        """
        Добавление нового человека в книгу дней рождения
        """
        try:
            # Проверяем валидность месяца
            if month < 1 or month > 12:
                raise InvalidMonthError(month)

            person = Person(
                last_name=last_name,
                first_name=first_name,
                phone=phone,
                day=day,
                month=month,
                year=year,
            )

            self.people.append(person)
            self.people.sort(key=lambda p: (p.last_name.lower(), p.first_name.lower()))

            logging.info(
                f"Добавлен: {person.full_name}, дата рождения: {person.birth_date}"
            )

        except (InvalidDateError, InvalidMonthError) as e:
            logging.error(f"Ошибка при добавлении: {e}")
            raise

    def __str__(self) -> str:
        """
        Вывод данных в табличном виде
        """
        if not self.people:
            return "Книга дней рождения пуста."

        # Заголовок таблицы
        table = []
        line = "+{}+{}+{}+{}+".format("-" * 4, "-" * 25, "-" * 20, "-" * 15)
        table.append(line)

        table.append(
            "| {:^4} | {:^25} | {:^20} | {:^15} |".format(
                "№", "Фамилия Имя", "Телефон", "Дата рождения"
            )
        )
        table.append(line)

        # Данные людей
        for idx, person in enumerate(self.people, 1):
            # Обрезаем длинные имена
            full_name = (
                person.full_name[:23] + ".."
                if len(person.full_name) > 25
                else person.full_name
            )

            table.append(
                "| {:^4} | {:<25} | {:<20} | {:^15} |".format(
                    idx, full_name, person.phone, person.birth_date
                )
            )

        table.append(line)

        # Добавляем подсказку о фильтрации по месяцу
        table.append(
            "\nДля поиска именинников по месяцу используйте команду: filter <номер_месяца>"
        )

        return "\n".join(table)

    def filter_by_month(self, month: int) -> List[Person]:
        """
        Фильтрация людей по месяцу рождения
        Возвращает список людей, у которых день рождения в указанном месяце
        """
        # Проверяем валидность месяца
        if month < 1 or month > 12:
            raise InvalidMonthError(month)

        result = [person for person in self.people if person.birthday_in_month(month)]
        result.sort(key=lambda p: p.day)  # Сортируем по дню рождения в месяце

        # Логируем результат поиска
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

        if result:
            logging.info(
                f"Найдено {len(result)} человек с днем рождения в {month_name}"
            )
        else:
            logging.info(f"Людей с днем рождения в {month_name} не найдено")

        return result

    def display_filtered(self, month: int) -> str:
        """
        Вывод отфильтрованных данных в табличном виде
        """
        result = self.filter_by_month(month)

        if not result:
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
            return f"Людей с днем рождения в {month_name} не найдено."

        # Заголовок таблицы для отфильтрованных данных
        table = []
        month_names = [
            "январь",
            "февраль",
            "март",
            "апрель",
            "май",
            "июнь",
            "июль",
            "август",
            "сентябрь",
            "октябрь",
            "ноябрь",
            "декабрь",
        ]
        month_name = month_names[month - 1]

        table.append(
            f"\n🎂 ИМЕНИННИКИ В МЕСЯЦЕ: {month_name.upper()} ({len(result)} человек)"
        )
        line = "+{}+{}+{}+{}+{}+".format("-" * 4, "-" * 25, "-" * 20, "-" * 15, "-" * 6)
        table.append(line)

        table.append(
            "| {:^4} | {:^25} | {:^20} | {:^15} | {:^6} |".format(
                "№", "Фамилия Имя", "Телефон", "Дата рождения", "Возраст"
            )
        )
        table.append(line)

        # Данные отфильтрованных людей
        for idx, person in enumerate(result, 1):
            full_name = (
                person.full_name[:23] + ".."
                if len(person.full_name) > 25
                else person.full_name
            )

            table.append(
                "| {:^4} | {:<25} | {:<20} | {:^15} | {:^6} |".format(
                    idx, full_name, person.phone, person.birth_date, person.age
                )
            )

        table.append(line)
        return "\n".join(table)

    def save(self, filename: str):
        """
        Сохранение данных в XML-файл
        """
        try:
            root = ET.Element("birthdays")

            for person in self.people:
                person_element = ET.Element("person")

                ET.SubElement(person_element, "last_name").text = person.last_name
                ET.SubElement(person_element, "first_name").text = person.first_name
                ET.SubElement(person_element, "phone").text = person.phone
                ET.SubElement(person_element, "day").text = str(person.day)
                ET.SubElement(person_element, "month").text = str(person.month)
                ET.SubElement(person_element, "year").text = str(person.year)

                root.append(person_element)

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

            loaded_people = []
            errors = 0

            for person_element in root.findall("person"):
                try:
                    last_name = person_element.find("last_name").text
                    first_name = person_element.find("first_name").text
                    phone = person_element.find("phone").text
                    day = int(person_element.find("day").text)
                    month = int(person_element.find("month").text)
                    year = int(person_element.find("year").text)

                    person = Person(
                        last_name=last_name,
                        first_name=first_name,
                        phone=phone,
                        day=day,
                        month=month,
                        year=year,
                    )
                    loaded_people.append(person)

                except (
                    AttributeError,
                    ValueError,
                    InvalidDateError,
                    InvalidMonthError,
                ) as e:
                    errors += 1
                    logging.warning(
                        f"Пропущен некорректный элемент в файле {filename}: {e}"
                    )
                    continue

            self.people = loaded_people
            self.people.sort(key=lambda p: (p.last_name.lower(), p.first_name.lower()))

            logging.info(
                f"Загружено {len(self.people)} записей из файла: {filename} (ошибок: {errors})"
            )
            print(f"✅ Загружено {len(self.people)} записей из файла: {filename}")
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
