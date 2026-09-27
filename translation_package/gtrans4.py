"""Асинхронна реалізація функцій на основі googletrans 4.0.2."""

from __future__ import annotations

import asyncio
import csv
import sys
from pathlib import Path
from typing import Any

MIN_PYTHON = (3, 13)
REQUIRED_GOOGLETRANS_VERSION = "4.0.2"


def _version_error() -> str | None:
    if sys.version_info < MIN_PYTHON:
        return (
            "Помилка: модуль googletrans 4.0.2 в цій роботі призначений "
            "для Python 3.13 або новішої версії."
        )

    try:
        from importlib.metadata import PackageNotFoundError, version

        installed = version("googletrans")
    except PackageNotFoundError:
        return (
            "Помилка: googletrans не встановлено. Виконайте "
            "`python -m pip install -r requirements.txt`."
        )
    except Exception as error:  # pragma: no cover - metadata-specific failure
        return f"Помилка перевірки googletrans: {error}"

    if installed != REQUIRED_GOOGLETRANS_VERSION:
        return (
            "Помилка: потрібен googletrans==4.0.2, "
            f"а встановлено {installed}. Використайте окреме середовище "
            "та встановіть requirements.txt."
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


async def _translate_one(text: str, source: str, target: str) -> str:
    from googletrans import Translator

    async with Translator() as translator:
        result = await translator.translate(text, src=source, dest=target)
    return str(result.text)


async def TransLate(text: str, scr: str, dest: str) -> str:
    """Перекласти текст з мови scr на dest або повернути повідомлення про помилку."""
    problem = _version_error()
    if problem:
        return problem
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для перекладу не може бути порожнім."

    try:
        languages = _language_map()
        source = scr.strip().casefold()
        if source != "auto":
            source = _language_code(scr, languages)
        target = _language_code(dest, languages)
        return await _translate_one(text, source, target)
    except Exception as error:
        return _error(error)


async def LangDetect(text: str, set: str = "all") -> str:
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

        async with Translator() as translator:
            detected = await translator.detect(text)
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


async def CodeLang(lang: str) -> str:
    """Повернути код мови за назвою або назву за кодом."""
    problem = _version_error()
    if problem:
        return problem
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


async def LanguageList(out: str = "screen", text: str | None = None) -> str:
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
        languages = _language_map()
        codes = sorted(languages, key=lambda code: languages[code].casefold())
        headers = ["Мова", "Код"]
        rows = [[languages[code], code] for code in codes]

        if text:
            headers.append("Переклад")
            from googletrans import Translator

            semaphore = asyncio.Semaphore(4)

            async with Translator() as translator:
                async def translate_for(code: str) -> tuple[str, str]:
                    async with semaphore:
                        try:
                            result: Any = await translator.translate(
                                text, src="auto", dest=code
                            )
                            return code, str(result.text)
                        except Exception as error:
                            return code, _error(error)

                translations = dict(
                    await asyncio.gather(*(translate_for(code) for code in codes))
                )
            rows = [
                [languages[code], code, translations[code]] for code in codes
            ]

        if destination == "screen":
            print(_format_table(headers, rows))
        else:
            output_path = Path("languages_gtrans4.csv")
            with output_path.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows)

        failed = sum(
            1 for row in rows if len(row) > 2 and row[2].startswith("Помилка:")
        )
        if failed:
            return f"Помилка: не вдалося перекласти текст для {failed} мов."
        return "Ok"
    except Exception as error:
        return _error(error)