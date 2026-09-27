"""Демонстрація асинхронних функцій googletrans 4.0.2."""

import asyncio

from translation_package import AUTHOR, NAME
from translation_package import gtrans4 as translation


async def main() -> None:
    text = "Добрий день! Я вивчаю програмування."
    print(f"{NAME} — googletrans 4.0.2")
    print(f"Автор: {AUTHOR}")

    language = await translation.LangDetect(text, "all")
    print(f"\nВизначення мови: {language}")

    language_code = await translation.CodeLang("english")
    print(f"Код англійської мови: {language_code}")

    translated = await translation.TransLate(text, "uk", "en")
    print(f"\nПереклад англійською: {translated}")

    print("\nТаблиця мов:")
    result = await translation.LanguageList("screen")
    print(f"Результат LanguageList: {result}")


if __name__ == "__main__":
    asyncio.run(main())