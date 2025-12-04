#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List

from models import Book, DataFormatError, InvalidInputError


@dataclass
class Library:
    """Класс для коллекции книг"""

    books: List[Book] = field(default_factory=list)

    def add(self, title: str, author: str, year: int, genre: str, pages: int):
        """
        Добавление новой книги в библиотеку
        """
        try:
            book = Book(title=title, author=author, year=year, genre=genre, pages=pages)
            self.books.append(book)
            self.books.sort(key=lambda book: book.title)
            logging.info(f"Добавлена книга: '{title}' - {author} ({year})")
        except InvalidInputError as e:
            logging.error(f"Ошибка при добавлении книги: {e}")
            raise

    def __str__(self) -> str:
        """
        Вывод данных в табличном виде
        """
        if not self.books:
            return "Библиотека пуста."

        # Заголовок таблицы
        table = []
        line = "+{}+{}+{}+{}+{}+".format("-" * 4, "-" * 30, "-" * 25, "-" * 8, "-" * 8)
        table.append(line)

        table.append(
            "| {:^4} | {:^30} | {:^25} | {:^8} | {:^8} |".format(
                "№", "Название", "Автор", "Год", "Стр."
            )
        )
        table.append(line)

        # Данные книг
        for idx, book in enumerate(self.books, 1):
            # Обрезаем длинные названия и имена авторов
            title = book.title[:28] + ".." if len(book.title) > 30 else book.title
            author = book.author[:23] + ".." if len(book.author) > 25 else book.author

            table.append(
                "| {:^4} | {:<30} | {:<25} | {:^8} | {:^8} |".format(
                    idx, title, author, book.year, book.pages
                )
            )

        table.append(line)
        return "\n".join(table)

    def select(self, criterion: str) -> List[Book]:
        """
        Выборка книг по критерию (автору или жанру)
        """
        criterion = criterion.strip().lower()
        result = []

        for book in self.books:
            if (
                criterion in book.author.lower()
                or criterion in book.genre.lower()
                or criterion in book.title.lower()
            ):
                result.append(book)

        logging.info(f"Найдено {len(result)} книг по критерию '{criterion}'")
        return result

    def save(self, filename: str):
        """
        Сохранение данных в XML-файл
        """
        try:
            root = ET.Element("library")

            for book in self.books:
                book_element = ET.Element("book")

                ET.SubElement(book_element, "title").text = book.title
                ET.SubElement(book_element, "author").text = book.author
                ET.SubElement(book_element, "year").text = str(book.year)
                ET.SubElement(book_element, "genre").text = book.genre
                ET.SubElement(book_element, "pages").text = str(book.pages)

                root.append(book_element)

            tree = ET.ElementTree(root)

            # Добавляем XML декларацию с кодировкой
            tree.write(filename, encoding="utf-8", xml_declaration=True)

            logging.info(f"Данные сохранены в файл: {filename}")
            print(f"Данные успешно сохранены в файл: {filename}")

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

            loaded_books = []

            for book_element in root.findall("book"):
                try:
                    title = book_element.find("title").text
                    author = book_element.find("author").text
                    year = int(book_element.find("year").text)
                    genre = book_element.find("genre").text
                    pages = int(book_element.find("pages").text)

                    book = Book(
                        title=title, author=author, year=year, genre=genre, pages=pages
                    )
                    loaded_books.append(book)

                except (AttributeError, ValueError) as e:
                    logging.warning(
                        f"Пропущен некорректный элемент в файле {filename}: {e}"
                    )
                    continue

            self.books = loaded_books
            self.books.sort(key=lambda book: book.title)

            logging.info(f"Загружено {len(self.books)} книг из файла: {filename}")
            print(f"Загружено {len(self.books)} книг из файла: {filename}")

        except ET.ParseError as e:
            error_msg = f"Ошибка парсинга XML файла {filename}: {e}"
            logging.error(error_msg)
            raise DataFormatError(filename, error_msg)
        except FileNotFoundError:
            error_msg = f"Файл не найден: {filename}"
            logging.error(error_msg)
            raise DataFormatError(filename, error_msg)
