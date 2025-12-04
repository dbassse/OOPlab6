#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass


# ============ КЛАССЫ ИСКЛЮЧЕНИЙ ============
class SpeedLimitExceededError(Exception):
    """Исключение при превышении скорости"""

    def __init__(self, current_speed: int, max_speed: int = 200, car_info: str = ""):
        self.current_speed = current_speed
        self.max_speed = max_speed
        self.car_info = car_info
        self.message = f"Превышена максимальная скорость {max_speed} км/ч"
        super().__init__(self.message)

    def __str__(self):
        if self.car_info:
            return f"{self.car_info}: {self.current_speed} -> {self.message}"
        return f"{self.current_speed} -> {self.message}"


class InvalidSpeedError(Exception):
    """Исключение для некорректной скорости"""

    def __init__(self, speed: int, message="Некорректное значение скорости"):
        self.speed = speed
        self.message = message
        super().__init__(f"{speed} -> {message}")

    def __str__(self):
        return f"{self.speed} -> {self.message}"


class InvalidCarError(Exception):
    """Исключение для некорректных данных автомобиля"""

    def __init__(self, car_data: str, message="Некорректные данные автомобиля"):
        self.car_data = car_data
        self.message = message
        super().__init__(f"{car_data} -> {message}")

    def __str__(self):
        return f"{self.car_data} -> {self.message}"


class DataFormatError(Exception):
    """Исключение для ошибок формата XML-файла"""

    def __init__(self, filename: str, message="Некорректный формат данных"):
        self.filename = filename
        self.message = message
        super().__init__(f"{filename} -> {message}")

    def __str__(self):
        return f"{self.filename} -> {self.message}"


# ============ КЛАСС ДАННЫХ ============
@dataclass(frozen=True)
class Car:
    """Класс для хранения информации об автомобиле"""

    brand: str  # Марка автомобиля
    model: str  # Модель автомобиля
    license_plate: str  # Госномер
    max_speed: int  # Максимальная допустимая скорость
    current_speed: int  # Текущая скорость

    def __post_init__(self):
        """Валидация данных после инициализации"""
        # Проверка скорости
        if self.max_speed <= 0:
            raise InvalidSpeedError(
                self.max_speed, "Максимальная скорость должна быть положительной"
            )

        if self.current_speed < 0:
            raise InvalidSpeedError(
                self.current_speed, "Текущая скорость не может быть отрицательной"
            )

        # Проверка превышения скорости
        if self.current_speed > self.max_speed:
            raise SpeedLimitExceededError(
                self.current_speed,
                self.max_speed,
                f"{self.brand} {self.model} ({self.license_plate})",
            )

    @property
    def full_name(self) -> str:
        """Полное название автомобиля"""
        return f"{self.brand} {self.model}"

    @property
    def speed_status(self) -> str:
        """Статус скорости"""
        if self.current_speed > self.max_speed:
            return "ПРЕВЫШЕНИЕ"
        elif self.current_speed == 0:
            return "ОСТАНОВЛЕН"
        else:
            return "В ПРЕДЕЛАХ"

    def is_speeding(self) -> bool:
        """Проверяет, превышает ли автомобиль скорость"""
        return self.current_speed > self.max_speed
