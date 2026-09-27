"""Синхронна реалізація функцій на основі googletrans 3.1.0a0."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

REQUIRED_GOOGLETRANS_VERSION = "3.1.0a0"


def _version_error() -> str | None:
    if sys.version_info >= (3, 13):
        return (
            "Помилка: версія Python не підтримується. googletrans 3.1.0a0 у цій роботі "
            "потрібно запускати з Python 3.11. Python 3.13 і новіші "
            "версії не підтримуються."
        )
    try:
        from importlib.metadata import PackageNotFoundError, version

        installed = version("googletrans")
    except PackageNotFoundError:
        return (
            "Помилка: googletrans не встановлено. Активуйте Python 3.11 "
            "і виконайте `python -m pip install -r requirements-gtrans3.txt`."
        )
    except Exception as error:  # pragma: no cover - metadata-specific failure
        return f"Помилка перевірки googletrans: {error}"

    if installed != REQUIRED_GOOGLETRANS_VERSION:
        return (
            "Помилка: потрібен googletrans==3.1.0a0, "
            f"а встановлено {installed}. Скористайтеся окремим середовищем "
            "Python 3.11 та файлом requirements-gtrans3.txt."
        )
    return None


def _language_map() -> dict[str, str]:
    from googletrans import LANGUAGES

    return {str(code).casefold(): str(name) for code, name in LANGUAGES.items()}


def _error(error: Exception) -> str:
    return f"Помилка: {type(error).__name__}: {error}"


def _language_code(lang: str, languages: dict[str, str]) -> str:
    normalized = " ".join(lang.replace("_", " ").split()).casefold()
    if normalized in languages:
        return normalized
    for code, name in languages.items():
        if " ".join(name.split()).casefold() == normalized:
            return code
    raise ValueError(f"Мову «{lang}» не знайдено в таблиці googletrans.")


def TransLate(text: str, scr: str, dest: str) -> str:
    """Перекласти текст з мови scr на dest або повернути повідомлення про помилку."""
    problem = _version_error()
    if problem:
        return problem
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для перекладу не може бути порожнім."
    try:
        from googletrans import Translator

        languages = _language_map()
        source = scr.strip().casefold()
        if source != "auto":
            source = _language_code(scr, languages)
        target = _language_code(dest, languages)
        return str(Translator().translate(text, src=source, dest=target).text)
    except Exception as error:
        return _error(error)


def LangDetect(text: str, set: str = "all") -> str:
    """Визначити мову тексту та/або повернути коефіцієнт довіри."""
    problem = _version_error()
    if problem:
        return problem
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для визначення мови не може бути порожнім."

    result_type = set.strip().casefold()
    if result_type not in {"lang", "confidence", "all"}:
        return "Помилка: параметр set має бути 'lang', 'confidence' або 'all'."
    try:
        from googletrans import Translator

        detected = Translator().detect(text)
        code = str(detected.lang).casefold()
        language = _language_map().get(code, code)
        confidence = float(detected.confidence)
        if result_type == "lang":
            return language
        if result_type == "confidence":
            return f"{confidence:.3f}"
        return f"Мова: {language} ({code}); довіра: {confidence:.3f}"
    except Exception as error:
        return _error(error)


def CodeLang(lang: str) -> str:
    """Повернути код мови за назвою або назву за кодом."""
    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: назва або код мови не можуть бути порожніми."
    try:
        languages = _language_map()
        normalized = " ".join(lang.replace("_", " ").split()).casefold()
        if normalized in languages:
            return languages[normalized]
        for code, name in languages.items():
            if " ".join(name.split()).casefold() == normalized:
                return code
        return f"Помилка: мову «{lang}» не знайдено."
    except Exception as error:
        return _error(error)


def _format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(headers[index]), *(len(row[index]) for row in rows))
        for index in range(len(headers))
    ]
    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    lines = [border, "| " + " | ".join(
        headers[index].ljust(widths[index]) for index in range(len(headers))
    ) + " |", border]
    lines.extend(
        "| " + " | ".join(
            row[index].ljust(widths[index]) for index in range(len(headers))
        ) + " |"
        for row in rows
    )
    lines.append(border)
    return "\n".join(lines)


def LanguageList(out: str = "screen", text: str | None = None) -> str:
    """Показати чи зберегти таблицю мов, кодів та, за потреби, перекладів."""
    problem = _version_error()
    if problem:
        return problem
    destination = out.strip().casefold()
    if destination not in {"screen", "file"}:
        return "Помилка: параметр out має бути 'screen' або 'file'."
    if text is not None and not isinstance(text, str):
        return "Помилка: text має бути рядком або None."

    try:
        from googletrans import Translator

        languages = _language_map()
        codes = sorted(languages, key=lambda code: languages[code].casefold())
        headers = ["Мова", "Код"]
        rows = [[languages[code], code] for code in codes]
        if text:
            headers.append("Переклад")
            translator = Translator()
            rows = [
                [
                    languages[code],
                    code,
                    str(translator.translate(text, src="auto", dest=code).text),
                ]
                for code in codes
            ]

        if destination == "screen":
            print(_format_table(headers, rows))
        else:
            with Path("languages_gtrans3.csv").open(
                "w", encoding="utf-8-sig", newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)
        return "Ok"
    except Exception as error:
        return _error(error)