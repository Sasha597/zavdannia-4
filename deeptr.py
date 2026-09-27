"""Демонстрація deep-translator та langdetect."""

from translation_package import AUTHOR, NAME
from translation_package import deeptr as translation


def main() -> None:
    text = "Добрий день! Я вивчаю програмування."
    print(f"{NAME} — deep-translator")
    print(f"Автор: {AUTHOR}")
    print(f"\nВизначення мови: {translation.LangDetect(text, 'all')}")
    print(f"Код англійської мови: {translation.CodeLang('english')}")
    print(f"\nПереклад англійською: {translation.TransLate(text, 'uk', 'en')}")
    print(f"\nРезультат LanguageList: {translation.LanguageList('screen')}")


if __name__ == "__main__":
    main()