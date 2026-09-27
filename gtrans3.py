"""Демонстрація синхронних функцій googletrans 3.1.0a0 (Python 3.11)."""

import sys

from translation_package import AUTHOR, NAME
from translation_package import gtrans3 as translation


def main() -> None:
    print(f"{NAME} — googletrans 3.1.0a0")
    print(f"Автор: {AUTHOR}")

    # Перевірка окремо від імпорту пакета: на Python 3.13+ відразу
    # показується зрозуміле повідомлення, як вимагає завдання.
    if sys.version_info >= (3, 13):
        print(translation.TransLate("Добрий день", "uk", "en"))
        return

    text = "Добрий день! Я вивчаю програмування."
    print(f"\nВизначення мови: {translation.LangDetect(text, 'all')}")
    print(f"Код англійської мови: {translation.CodeLang('english')}")
    print(f"\nПереклад англійською: {translation.TransLate(text, 'uk', 'en')}")
    print(f"\nРезультат LanguageList: {translation.LanguageList('screen')}")


if __name__ == "__main__":
    main()