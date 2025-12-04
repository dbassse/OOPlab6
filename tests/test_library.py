#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile

import pytest

# Добавляем пути к проектам в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

library_path = os.path.join(parent_dir, "library")
sys.path.insert(0, library_path)

# Теперь импортируем модули
from library.models import Book, DataFormatError, InvalidInputError, UnknownCommandError
from library.storage import Library


class TestBook:
    """Тесты класса Book"""

    def test_create_valid_book(self):
        """Тест создания корректной книги"""
        book = Book(
            title="Мастер и Маргарита",
            author="Михаил Булгаков",
            year=1967,
            genre="Роман",
            pages=480,
        )

        assert book.title == "Мастер и Маргарита"
        assert book.author == "Михаил Булгаков"
        assert book.year == 1967
        assert book.genre == "Роман"
        assert book.pages == 480

    def test_create_book_with_invalid_year(self):
        """Тест создания книги с некорректным годом"""
        with pytest.raises(InvalidInputError):
            Book(
                title="Книга",
                author="Автор",
                year=3000,  # Будущий год
                genre="Жанр",
                pages=100,
            )

    def test_create_book_with_invalid_pages(self):
        """Тест создания книги с некорректным количеством страниц"""
        with pytest.raises(InvalidInputError):
            Book(
                title="Книга",
                author="Автор",
                year=2000,
                genre="Жанр",
                pages=-10,  # Отрицательное количество страниц
            )

    def test_book_frozen(self):
        """Тест неизменяемости книги (frozen dataclass)"""
        book = Book(
            title="Название", author="Автор", year=2000, genre="Жанр", pages=100
        )

        # Попытка изменить атрибут должна вызвать ошибку
        with pytest.raises(AttributeError):
            book.title = "Новое название"


class TestLibrary:
    """Тесты класса Library"""

    @pytest.fixture
    def empty_library(self):
        """Создание пустой библиотеки"""
        return Library()

    @pytest.fixture
    def library_with_books(self):
        """Создание библиотеки с тестовыми книгами"""
        library = Library()
        library.books = [
            Book("Книга A", "Автор A", 2000, "Жанр A", 100),
            Book("Книга B", "Автор B", 2005, "Жанр B", 200),
            Book("Книга C", "Автор C", 2010, "Жанр C", 300),
        ]
        return library

    def test_add_book(self, empty_library):
        """Тест добавления книги"""
        empty_library.add(
            title="Тестовая книга",
            author="Тестовый автор",
            year=2020,
            genre="Тестовый жанр",
            pages=150,
        )

        assert len(empty_library.books) == 1
        assert empty_library.books[0].title == "Тестовая книга"

    def test_add_book_invalid_year(self, empty_library):
        """Тест добавления книги с некорректным годом"""
        with pytest.raises(InvalidInputError):
            empty_library.add(
                title="Книга",
                author="Автор",
                year=3000,  # Некорректный год
                genre="Жанр",
                pages=100,
            )

        assert len(empty_library.books) == 0

    def test_str_empty_library(self, empty_library):
        """Тест строкового представления пустой библиотеки"""
        result = str(empty_library)
        assert "Библиотека пуста" in result

    def test_str_library_with_books(self, library_with_books):
        """Тест строкового представления библиотеки с книгами"""
        result = str(library_with_books)
        assert "Книга A" in result
        assert "Автор A" in result
        assert "2000" in result

    def test_select_by_author(self, library_with_books):
        """Тест поиска книг по автору"""
        result = library_with_books.select("автор a")
        assert len(result) == 1
        assert result[0].author == "Автор A"

    def test_select_by_genre(self, library_with_books):
        """Тест поиска книг по жанру"""
        result = library_with_books.select("жанр b")
        assert len(result) == 1
        assert result[0].genre == "Жанр B"

    def test_select_by_title(self, library_with_books):
        """Тест поиска книг по названию"""
        result = library_with_books.select("книга c")
        assert len(result) == 1
        assert result[0].title == "Книга C"

    def test_select_no_results(self, library_with_books):
        """Тест поиска книг - нет результатов"""
        result = library_with_books.select("несуществующий")
        assert len(result) == 0

    def test_save_and_load(self, library_with_books):
        """Тест сохранения и загрузки библиотеки"""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            temp_file = f.name

        try:
            # Сохраняем библиотеку
            library_with_books.save(temp_file)

            # Проверяем, что файл создан
            assert os.path.exists(temp_file)

            # Создаем новую пустую библиотеку и загружаем данные
            new_library = Library()
            new_library.load(temp_file)

            # Проверяем, что данные загрузились корректно
            assert len(new_library.books) == len(library_with_books.books)

            # Проверяем, что книги те же
            for i in range(len(library_with_books.books)):
                assert new_library.books[i].title == library_with_books.books[i].title
                assert new_library.books[i].author == library_with_books.books[i].author

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_load_nonexistent_file(self, empty_library):
        """Тест загрузки несуществующего файла"""
        with pytest.raises(DataFormatError):
            empty_library.load("nonexistent_file.xml")


class TestExceptions:
    """Тесты пользовательских исключений"""

    def test_invalid_input_error(self):
        """Тест исключения InvalidInputError"""
        error = InvalidInputError(3000, "Некорректное значение")
        assert str(error) == "3000 -> Некорректное значение"

    def test_data_format_error(self):
        """Тест исключения DataFormatError"""
        error = DataFormatError("test.xml", "Некорректный формат")
        assert str(error) == "test.xml -> Некорректный формат"

    def test_unknown_command_error(self):
        """Тест исключения UnknownCommandError"""
        error = UnknownCommandError("unknown", "Неизвестная команда")
        assert str(error) == "unknown -> Неизвестная команда"


if __name__ == "__main__":
    # Для запуска без pytest
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "library_project"))

    # Простые тесты
    print("Запуск тестов для библиотеки...")

    # Тест 1: Создание книги
    try:
        book = Book("Тест", "Автор", 2000, "Жанр", 100)
        print("✓ Тест 1 пройден: создание книги")
    except Exception as e:
        print(f"✗ Тест 1 не пройден: {e}")

    # Тест 2: Добавление в библиотеку
    try:
        library = Library()
        library.add("Тест", "Автор", 2000, "Жанр", 100)
        assert len(library.books) == 1
        print("✓ Тест 2 пройден: добавление в библиотеку")
    except Exception as e:
        print(f"✗ Тест 2 не пройден: {e}")

    print("\nВсе тесты завершены!")
