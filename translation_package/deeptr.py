"""Реалізація функцій на основі deep-translator і langdetect."""

from __future__ import annotations

import csv
from pathlib import Path


def _language_map() -> dict[str, str]:
    from deep_translator import GoogleTranslator

    # deep-translator повертає словник {назва: код}; тут нормалізуємо його
    # до спільного з іншими модулями формату {код: назва}.
    return {
        str(code).casefold(): str(name)
        for name, code in GoogleTranslator(
            source="auto", target="english"
        ).get_supported_languages(as_dict=True).items()
    }


def _error(error: Exception) -> str:
    return f"Помилка: {type(error).__name__}: {error}"


def _language_code(lang: str, languages: dict[str, str]) -> str:
    normalized = " ".join(lang.replace("_", " ").split()).casefold()
    if normalized in languages:
        return normalized
    for code, name in languages.items():
        if " ".join(name.split()).casefold() == normalized:
            return code
    raise ValueError(f"Мову «{lang}» не знайдено в таблиці deep-translator.")


def TransLate(text: str, scr: str, dest: str) -> str:
    """Перекласти текст з мови scr на dest або повернути повідомлення про помилку."""
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для перекладу не може бути порожнім."
    try:
        from deep_translator import GoogleTranslator

        languages = _language_map()
        source = "auto" if scr.strip().casefold() == "auto" else _language_code(scr, languages)
        target = _language_code(dest, languages)
        return str(
            GoogleTranslator(source=source, target=target).translate(text)
        )
    except Exception as error:
        return _error(error)


def LangDetect(text: str, set: str = "all") -> str:
    """Визначити мову тексту та/або повернути коефіцієнт довіри."""
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для визначення мови не може бути порожнім."
    result_type = set.strip().casefold()
    if result_type not in {"lang", "confidence", "all"}:
        return "Помилка: параметр set має бути 'lang', 'confidence' або 'all'."

    try:
        from langdetect import detect_langs

        predictions = detect_langs(text)
        if not predictions:
            return "Помилка: не вдалося визначити мову."
        prediction = predictions[0]
        code = str(prediction.lang).casefold()
        confidence = float(prediction.prob)
        language = _language_map().get(code, code)
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
    destination = out.strip().casefold()
    if destination not in {"screen", "file"}:
        return "Помилка: параметр out має бути 'screen' або 'file'."
    if text is not None and not isinstance(text, str):
        return "Помилка: text має бути рядком або None."

    try:
        from deep_translator import GoogleTranslator

        languages = _language_map()
        codes = sorted(languages, key=lambda code: languages[code].casefold())
        headers = ["Мова", "Код"]
        rows = [[languages[code], code] for code in codes]
        if text:
            headers.append("Переклад")
            rows = []
            for code in codes:
                try:
                    translated = GoogleTranslator(
                        source="auto", target=code
                    ).translate(text)
                except Exception as error:
                    translated = _error(error)
                rows.append([languages[code], code, str(translated)])

        if destination == "screen":
            print(_format_table(headers, rows))
        else:
            with Path("languages_deeptr.csv").open(
                "w", encoding="utf-8-sig", newline=""
            ) as file:
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