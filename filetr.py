"""Переклад заданої кількості речень з текстового файла за config.json."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
MODULES = {"gtrans4", "gtrans3", "deeptr"}
SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?…])\s+")


def split_sentences(text: str) -> list[str]:
    """Розбити текст на речення, зберігаючи розділові знаки."""
    return [part.strip() for part in SENTENCE_BOUNDARY.split(text.strip()) if part.strip()]


def read_config(config_path: Path) -> dict[str, Any]:
    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Не знайдено конфігураційний файл: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Помилка у форматі JSON, рядок {error.lineno}: {error.msg}"
        ) from error

    required = {"input_file", "target_language", "module", "output", "sentence_count"}
    missing = sorted(required.difference(config))
    if missing:
        raise ValueError(f"У config.json відсутні параметри: {', '.join(missing)}.")

    module_name = str(config["module"]).strip()
    if module_name not in MODULES:
        raise ValueError(
            "Параметр module має бути gtrans4, gtrans3 або deeptr."
        )

    output = str(config["output"]).strip().casefold()
    if output not in {"screen", "file"}:
        raise ValueError("Параметр output має бути screen або file.")

    count = config["sentence_count"]
    if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 1):
        raise ValueError("sentence_count має бути додатним цілим числом або null.")

    return {
        **config,
        "input_file": str(config["input_file"]).strip(),
        "target_language": str(config["target_language"]).strip(),
        "module": module_name,
        "output": output,
        "sentence_count": count,
    }


def _backend(module_name: str) -> Any:
    return importlib.import_module(f"translation_package.{module_name}")


def _get_source_language(text: str) -> str:
    try:
        from langdetect import detect

        code = detect(text)
        return f"{code} (визначено langdetect)"
    except Exception as error:
        raise ValueError(
            f"не вдалося визначити мову тексту: {type(error).__name__}: {error}"
        ) from error


def _resolve_output_path(source_path: Path, language_code: str) -> Path:
    safe_code = re.sub(r"[^a-zA-Z0-9-]", "", language_code.strip())
    if not safe_code:
        raise ValueError("Не вдалося визначити код мови для назви вихідного файла.")
    return source_path.with_name(f"{source_path.stem}_{safe_code}{source_path.suffix}")


async def _translate(
    module_name: str, text: str, target_language: str
) -> tuple[str, str]:
    backend = _backend(module_name)
    lookup_result = (
        await backend.CodeLang(target_language)
        if module_name == "gtrans4"
        else backend.CodeLang(target_language)
    )
    if lookup_result.startswith("Помилка:"):
        return lookup_result, lookup_result
    if re.fullmatch(r"[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,3})?", target_language):
        target_code = target_language.casefold()
    else:
        target_code = lookup_result

    result = (
        await backend.TransLate(text, "auto", target_language)
        if module_name == "gtrans4"
        else backend.TransLate(text, "auto", target_language)
    )
    return target_code, str(result)


def _format_report(
    source_path: Path,
    size_bytes: int,
    text: str,
    sentences: list[str],
    source_language: str,
) -> None:
    print(f"Файл: {source_path.name}")
    print(f"Розмір: {size_bytes} байт")
    print(f"Кількість символів: {len(text)}")
    print(f"Кількість речень: {len(sentences)}")
    print(f"Мова тексту: {source_language}")


async def run(config_path: Path) -> int:
    try:
        config = read_config(config_path)
        source_path = (BASE_DIR / config["input_file"]).resolve()
        if not source_path.is_relative_to(BASE_DIR):
            raise ValueError("Вхідний файл має знаходитися в каталозі проєкту.")
        if not source_path.is_file():
            raise FileNotFoundError(f"Вхідний файл не знайдено: {source_path.name}")

        text = source_path.read_text(encoding="utf-8")
        sentences = split_sentences(text)
        if not sentences:
            raise ValueError("Вхідний файл не містить жодного речення.")

        _format_report(
            source_path,
            source_path.stat().st_size,
            text,
            sentences,
            _get_source_language(text),
        )

        selected = sentences
        if config["sentence_count"] is not None:
            selected = sentences[: config["sentence_count"]]
        text_to_translate = " ".join(selected)
        target_code, translated = await _translate(
            config["module"], text_to_translate, config["target_language"]
        )

        if translated.startswith("Помилка:"):
            print(f"\n{translated}")
            return 1

        if config["output"] == "file":
            output_path = _resolve_output_path(source_path, target_code)
            output_path.write_text(translated, encoding="utf-8")
            print("\nOk")
            print(f"Переклад збережено у файл: {output_path.name}")
            return 0

        backend = _backend(config["module"])
        target_name = (
            await backend.CodeLang(target_code)
            if config["module"] == "gtrans4"
            else backend.CodeLang(target_code)
        )
        print(f"\nМова перекладу: {target_name} ({target_code})")
        print(f"Модуль перекладу: {config['module']}")
        print(f"Переклад:\n{translated}")
        return 0
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Помилка: {error}")
        return 1
    except Exception as error:
        print(f"Помилка під час виконання: {type(error).__name__}: {error}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Переклад тексту з файла на основі config.json."
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Шлях до JSON-конфігурації (типово: config.json).",
    )
    arguments = parser.parse_args()
    config_path = Path(arguments.config)
    if not config_path.is_absolute():
        config_path = (BASE_DIR / config_path).resolve()

    try:
        return asyncio.run(run(config_path))
    except KeyboardInterrupt:
        print("\nОперацію перервано користувачем.")
        return 130


if __name__ == "__main__":
    sys.exit(main())