#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from dataclasses import dataclass


# ============ КЛАССЫ ИСКЛЮЧЕНИЙ ============
class InvalidInputError(Exception):
    """Исключение для некорректного ввода"""

    def __init__(self, value, message="Некорректное значение"):
        self.value = value
        self.message = message
        super().__init__(f"{value} -> {message}")

    def __str__(self):
        return f"{self.value} -> {self.message}"


class DataFormatError(Exception):
    """Исключение для ошибок формата XML-файла"""

    def __init__(self, filename, message="Некорректный формат данных"):
        self.filename = filename
        self.message = message
        super().__init__(f"{filename} -> {message}")

    def __str__(self):
        return f"{self.filename} -> {self.message}"


class UnknownCommandError(Exception):
    """Исключение для неизвестной команды"""

    def __init__(self, command, message="Неизвестная команда"):
        self.command = command
        self.message = message
        super().__init__(f"{command} -> {message}")

    def __str__(self):
        return f"{self.command} -> {self.message}"


# ============ КЛАСС ДАННЫХ ============
@dataclass(frozen=True)
class Book:
    """Класс для хранения информации о книге"""

    title: str  # Название книги
    author: str  # Автор
    year: int  # Год издания
    genre: str  # Жанр
    pages: int  # Количество страниц

    def __post_init__(self):
        """Валидация данных после инициализации"""
        current_year = 2024  # Текущий год

        if self.year < 0 or self.year > current_year:
            raise InvalidInputError(
                self.year, f"Год издания должен быть в диапазоне 0-{current_year}"
            )

        if self.pages <= 0:
            raise InvalidInputError(
                self.pages, "Количество страниц должно быть положительным"
            )
