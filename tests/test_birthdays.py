#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from datetime import datetime

import pytest

# Добавляем пути к проектам в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

birthday_path = os.path.join(parent_dir, "birthday")
sys.path.insert(0, birthday_path)

# Теперь импортируем модули
from birthday.models import DataFormatError, InvalidDateError, InvalidMonthError, Person
from birthday.storage import BirthdayBook


class TestPerson:
    """Тесты класса Person"""

    def test_create_valid_person(self):
        """Тест создания корректного человека"""
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="+7-123-456-7890",
            day=15,
            month=5,
            year=1990,
        )

        assert person.last_name == "Иванов"
        assert person.first_name == "Иван"
        assert person.phone == "+7-123-456-7890"
        assert person.day == 15
        assert person.month == 5
        assert person.year == 1990

    def test_full_name_property(self):
        """Тест свойства full_name"""
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=1,
            month=1,
            year=2000,
        )

        assert person.full_name == "Иванов Иван"

    def test_birth_date_property(self):
        """Тест свойства birth_date"""
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=5,
            month=12,
            year=2000,
        )

        assert person.birth_date == "05.12.2000"

    def test_age_property(self):
        """Тест свойства age"""
        current_year = datetime.now().year
        birth_year = current_year - 25

        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=1,
            month=1,
            year=birth_year,
        )

        # Возраст должен быть 25 (или 24, если день рождения еще не наступил)
        # Проверяем, что возраст в разумных пределах
        assert 24 <= person.age <= 25

    def test_create_person_with_invalid_month(self):
        """Тест создания человека с некорректным месяцем"""
        with pytest.raises(InvalidMonthError) as exc_info:
            Person(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=15,
                month=13,  # Некорректный месяц
                year=1990,
            )

        assert "13 -> Недопустимый номер месяца" in str(exc_info.value)

    def test_create_person_with_invalid_day(self):
        """Тест создания человека с некорректным днем"""
        with pytest.raises(InvalidDateError) as exc_info:
            Person(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=31,
                month=2,  # В феврале максимум 29 дней
                year=2000,
            )

        assert "31.02.2000 ->" in str(exc_info.value)

    def test_create_person_with_invalid_year(self):
        """Тест создания человека с некорректным годом"""
        current_year = datetime.now().year

        with pytest.raises(InvalidDateError) as exc_info:
            Person(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=1,
                month=1,
                year=1800,  # Слишком старый год
            )

        assert f"Год должен быть в диапазоне 1900-{current_year}" in str(exc_info.value)

    def test_leap_year_feb_29(self):
        """Тест создания человека с 29 февраля в високосном году"""
        # 2000 год был високосным
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=29,
            month=2,
            year=2000,
        )

        assert person.day == 29
        assert person.month == 2
        assert person.year == 2000

    def test_non_leap_year_feb_29(self):
        """Тест создания человека с 29 февраля в невисокосном году"""
        # 2001 год не был високосным
        with pytest.raises(InvalidDateError) as exc_info:
            Person(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=29,
                month=2,
                year=2001,
            )

        assert "День должен быть в диапазоне 1-28" in str(exc_info.value)

    def test_birthday_in_month_true(self):
        """Тест метода birthday_in_month - день рождения в указанном месяце"""
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=15,
            month=5,
            year=1990,
        )

        assert person.birthday_in_month(5) == True
        assert person.birthday_in_month(6) == False

    def test_person_frozen(self):
        """Тест неизменяемости человека (frozen dataclass)"""
        person = Person(
            last_name="Иванов",
            first_name="Иван",
            phone="123",
            day=1,
            month=1,
            year=2000,
        )

        # Попытка изменить атрибут должна вызвать ошибку
        with pytest.raises(AttributeError):
            person.last_name = "Петров"


class TestBirthdayBook:
    """Тесты класса BirthdayBook"""

    @pytest.fixture
    def empty_book(self):
        """Создание пустой книги"""
        return BirthdayBook()

    @pytest.fixture
    def book_with_people(self):
        """Создание книги с тестовыми людьми"""
        book = BirthdayBook()
        book.people = [
            Person("Иванов", "Иван", "111", 15, 5, 1990),
            Person("Петрова", "Мария", "222", 3, 1, 1985),
            Person("Сидоров", "Алексей", "333", 22, 8, 1995),
            Person("Козлова", "Анна", "444", 7, 12, 1988),
            Person("Михайлов", "Дмитрий", "555", 15, 5, 1992),
        ]
        return book

    def test_add_person(self, empty_book):
        """Тест добавления человека"""
        empty_book.add(
            last_name="Иванов",
            first_name="Иван",
            phone="+7-123-456-7890",
            day=15,
            month=5,
            year=1990,
        )

        assert len(empty_book.people) == 1
        assert empty_book.people[0].full_name == "Иванов Иван"

    def test_add_person_invalid_month(self, empty_book):
        """Тест добавления человека с некорректным месяцем"""
        with pytest.raises(InvalidMonthError):
            empty_book.add(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=15,
                month=13,  # Некорректный месяц
                year=1990,
            )

        assert len(empty_book.people) == 0

    def test_add_person_invalid_date(self, empty_book):
        """Тест добавления человека с некорректной датой"""
        with pytest.raises(InvalidDateError):
            empty_book.add(
                last_name="Иванов",
                first_name="Иван",
                phone="123",
                day=31,
                month=2,  # Некорректная дата
                year=2000,
            )

        assert len(empty_book.people) == 0

    def test_str_empty_book(self, empty_book):
        """Тест строкового представления пустой книги"""
        result = str(empty_book)
        assert "Книга дней рождения пуста" in result

    def test_str_book_with_people(self, book_with_people):
        """Тест строкового представления книги с людьми"""
        result = str(book_with_people)
        assert "Иванов Иван" in result
        assert "15.05.1990" in result

    def test_filter_by_month_single_result(self, book_with_people):
        """Тест фильтрации по месяцу - один результат"""
        result = book_with_people.filter_by_month(1)  # Январь
        assert len(result) == 1
        assert result[0].full_name == "Петрова Мария"

    def test_filter_by_month_multiple_results(self, book_with_people):
        """Тест фильтрации по месяцу - несколько результатов"""
        result = book_with_people.filter_by_month(5)  # Май
        assert len(result) == 2
        # Проверяем сортировку по дню (должны быть в порядке возрастания дня)
        assert result[0].full_name == "Иванов Иван"  # 15 мая
        assert result[1].full_name == "Михайлов Дмитрий"  # 15 мая

    def test_filter_by_month_no_results(self, book_with_people):
        """Тест фильтрации по месяцу - нет результатов"""
        result = book_with_people.filter_by_month(2)  # Февраль
        assert len(result) == 0

    def test_filter_by_month_invalid_month(self, book_with_people):
        """Тест фильтрации по некорректному месяцу"""
        with pytest.raises(InvalidMonthError):
            book_with_people.filter_by_month(13)

    def test_display_filtered_with_results(self, book_with_people):
        """Тест отображения отфильтрованных данных с результатами"""
        result = book_with_people.display_filtered(5)
        assert "ИМЕНИННИКИ В МЕСЯЦЕ: МАЙ" in result
        assert "Иванов Иван" in result
        assert "Михайлов Дмитрий" in result

    def test_display_filtered_no_results(self, book_with_people):
        """Тест отображения отфильтрованных данных без результатов"""
        result = book_with_people.display_filtered(2)
        assert "не найдено" in result

    def test_save_and_load(self, book_with_people):
        """Тест сохранения и загрузки книги"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_file = f.name

        try:
            # Сохраняем книгу
            book_with_people.save(temp_file)

            # Проверяем, что файл создан
            assert os.path.exists(temp_file)

            # Создаем новую пустую книгу и загружаем данные
            new_book = BirthdayBook()
            new_book.load(temp_file)

            # Проверяем, что данные загрузились корректно
            assert len(new_book.people) == len(book_with_people.people)

            # Проверяем, что люди те же
            for i in range(len(book_with_people.people)):
                assert (
                    new_book.people[i].full_name == book_with_people.people[i].full_name
                )
                assert (
                    new_book.people[i].birth_date
                    == book_with_people.people[i].birth_date
                )

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_load_invalid_xml(self, empty_book):
        """Тест загрузки некорректного XML файла"""
        # Создаем временный файл с некорректным XML
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write("<invalid>Not a birthday book</invalid>")
            temp_file = f.name

        try:
            # Попытка загрузки должна вызвать исключение
            with pytest.raises(DataFormatError):
                empty_book.load(temp_file)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_sorting_alphabetical(self):
        """Тест алфавитной сортировки людей"""
        book = BirthdayBook()

        # Добавляем людей в разном порядке
        book.add("Яковлев", "Алексей", "111", 1, 1, 1990)
        book.add("Абрамов", "Борис", "222", 2, 2, 1991)
        book.add("Смирнов", "Владимир", "333", 3, 3, 1992)

        # Проверяем, что они отсортированы по фамилии, затем по имени
        assert book.people[0].last_name == "Абрамов"
        assert book.people[1].last_name == "Смирнов"
        assert book.people[2].last_name == "Яковлев"


class TestExceptions:
    """Тесты пользовательских исключений для второго задания"""

    def test_invalid_month_error(self):
        """Тест исключения InvalidMonthError"""
        error = InvalidMonthError(13, "Недопустимый номер месяца")
        assert str(error) == "13 -> Недопустимый номер месяца"

    def test_invalid_date_error(self):
        """Тест исключения InvalidDateError"""
        error = InvalidDateError(31, 2, 2000, "Некорректная дата")
        assert str(error) == "31.02.2000 -> Некорректная дата"

    def test_data_format_error(self):
        """Тест исключения DataFormatError"""
        error = DataFormatError("test.xml", "Некорректный формат")
        assert str(error) == "test.xml -> Некорректный формат"


if __name__ == "__main__":
    # Для запуска без pytest
    import sys

    sys.path.insert(
        0, os.path.join(os.path.dirname(__file__), "..", "birthday_project")
    )

    # Простые тесты
    print("Запуск тестов для дней рождения...")

    # Тест 1: Создание человека
    try:
        person = Person("Иванов", "Иван", "123", 1, 1, 2000)
        assert person.full_name == "Иванов Иван"
        print("✓ Тест 1 пройден: создание человека")
    except Exception as e:
        print(f"✗ Тест 1 не пройден: {e}")

    # Тест 2: Добавление в книгу
    try:
        book = BirthdayBook()
        book.add("Иванов", "Иван", "123", 1, 1, 2000)
        assert len(book.people) == 1
        print("✓ Тест 2 пройден: добавление в книгу")
    except Exception as e:
        print(f"✗ Тест 2 не пройден: {e}")

    print("\nВсе тесты завершены!")
