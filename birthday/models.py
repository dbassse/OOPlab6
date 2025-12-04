#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime


# ============ КЛАССЫ ИСКЛЮЧЕНИЙ ============
class InvalidMonthError(Exception):
    """Исключение для некорректного месяца"""

    def __init__(self, month: int, message="Недопустимый номер месяца"):
        self.month = month
        self.message = message
        super().__init__(f"{month} -> {message}")

    def __str__(self):
        return f"{self.month} -> {self.message}"


class InvalidDateError(Exception):
    """Исключение для некорректной даты"""

    def __init__(self, day: int, month: int, year: int, message="Некорректная дата"):
        self.day = day
        self.month = month
        self.year = year
        self.message = message
        super().__init__(f"{day:02d}.{month:02d}.{year} -> {message}")

    def __str__(self):
        return f"{self.day:02d}.{self.month:02d}.{self.year} -> {self.message}"


class DataFormatError(Exception):
    """Исключение для ошибок формата XML-файла"""

    def __init__(self, filename: str, message="Некорректный формат данных"):
        self.filename = filename
        self.message = message
        super().__init__(f"{filename} -> {message}")

    def __str__(self):
        return f"{self.filename} -> {self.message}"


class UnknownCommandError(Exception):
    """Исключение для неизвестной команды"""

    def __init__(self, command: str, message="Неизвестная команда"):
        self.command = command
        self.message = message
        super().__init__(f"{command} -> {message}")

    def __str__(self):
        return f"{self.command} -> {self.message}"


# ============ КЛАСС ДАННЫХ ============
@dataclass(frozen=True)
class Person:
    """Класс для хранения информации о человеке и его дне рождения"""

    last_name: str  # Фамилия
    first_name: str  # Имя
    phone: str  # Номер телефона
    day: int  # День рождения
    month: int  # Месяц рождения
    year: int  # Год рождения

    def __post_init__(self):
        """Валидация данных после инициализации"""
        current_year = datetime.now().year

        # Проверка года
        if self.year < 1900 or self.year > current_year:
            raise InvalidDateError(
                self.day,
                self.month,
                self.year,
                f"Год должен быть в диапазоне 1900-{current_year}",
            )

        # Проверка месяца
        if self.month < 1 or self.month > 12:
            raise InvalidMonthError(self.month)

        # Проверка дня в зависимости от месяца
        days_in_month = self._get_days_in_month()
        if self.day < 1 or self.day > days_in_month:
            raise InvalidDateError(
                self.day,
                self.month,
                self.year,
                f"День должен быть в диапазоне 1-{days_in_month} для месяца {self.month}",
            )

    def _get_days_in_month(self) -> int:
        """Возвращает количество дней в месяце с учетом високосного года"""
        if self.month == 2:  # Февраль
            # Проверка на високосный год
            if (self.year % 4 == 0 and self.year % 100 != 0) or (self.year % 400 == 0):
                return 29
            else:
                return 28
        elif self.month in [4, 6, 9, 11]:  # Апрель, июнь, сентябрь, ноябрь
            return 30
        else:  # Январь, март, май, июль, август, октябрь, декабрь
            return 31

    @property
    def full_name(self) -> str:
        """Полное имя (Фамилия Имя)"""
        return f"{self.last_name} {self.first_name}"

    @property
    def birth_date(self) -> str:
        """Дата рождения в формате ДД.ММ.ГГГГ"""
        return f"{self.day:02d}.{self.month:02d}.{self.year}"

    @property
    def age(self) -> int:
        """Возраст человека"""
        today = datetime.now()
        age = today.year - self.year
        # Если день рождения в этом году еще не наступил
        if (today.month, today.day) < (self.month, self.day):
            age -= 1
        return age

    def birthday_in_month(self, month: int) -> bool:
        """Проверяет, приходится ли день рождения на указанный месяц"""
        return self.month == month
