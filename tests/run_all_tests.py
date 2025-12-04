#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys


def run_pytest(test_file, project_name):
    """Запуск тестов с помощью pytest"""
    print(f"\n{'='*60}")
    print(f"Запуск тестов для проекта: {project_name}")
    print("=" * 60)

    # Добавляем путь к проекту в sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_path = os.path.join(parent_dir, project_name)

    # Создаем список аргументов для pytest
    args = [
        sys.executable,
        "-m",
        "pytest",
        test_file,
        "-v",
        "--tb=short",  # короткий traceback
    ]

    try:
        # Запускаем pytest
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30,
            env={
                **os.environ,
                "PYTHONPATH": f'{project_path}:{os.environ.get("PYTHONPATH", "")}',
            },
        )

        print(result.stdout)
        if result.stderr:
            print("Ошибки:")
            print(result.stderr)

        return result.returncode == 0

    except FileNotFoundError:
        print("✗ Pytest не установлен! Установите: pip install pytest")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Тесты выполняются слишком долго (таймаут 30 секунд)")
        return False


def main():
    """Основная функция запуска тестов"""
    print("Запуск всех тестов...")

    # Определяем пути к тестовым файлам
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_library = os.path.join(current_dir, "test_library.py")
    test_birthdays = os.path.join(current_dir, "test_birthdays.py")

    all_passed = True

    # Запускаем тесты для библиотеки
    if os.path.exists(test_library):
        if run_pytest(test_library, "library_project"):
            print("✓ Тесты для библиотеки прошли успешно")
        else:
            print("✗ Тесты для библиотеки не прошли")
            all_passed = False
    else:
        print("✗ Файл test_library.py не найден")
        all_passed = False

    # Запускаем тесты для дней рождения
    if os.path.exists(test_birthdays):
        if run_pytest(test_birthdays, "birthday_project"):
            print("✓ Тесты для дней рождения прошли успешно")
        else:
            print("✗ Тесты для дней рождения не прошли")
            all_passed = False
    else:
        print("✗ Файл test_birthdays.py не найден")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Все тесты успешно пройдены!")
    else:
        print("❌ Некоторые тесты не прошли")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
