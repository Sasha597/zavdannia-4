"""Створює чітко позначені навчальні ілюстрації, а не скриншоти VS Code."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "report" / "illustrations"
FONT = "DejaVu Sans Mono"


def rect(x: int, y: int, width: int, height: int, color: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'fill="{color}"/>'
    )


def text(
    x: int,
    y: int,
    value: str,
    color: str = "#d4d4d4",
    size: int = 19,
    weight: str = "normal",
) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
        f'font-family="{FONT}" font-weight="{weight}" '
        f'xml:space="preserve">{escape(value)}</text>'
    )


def svg(width: int, height: int, elements: list[str]) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        + "".join(elements)
        + "</svg>"
    )


def editor_image() -> str:
    elements = [
        rect(0, 0, 1200, 720, "#1e1e1e"),
        rect(0, 0, 1200, 58, "#ffd166"),
        text(
            24, 37, "ДЕМОНСТРАЦІЙНИЙ МАКЕТ — НЕ СКРИНШОТ VS CODE",
            "#22202c", 22, "bold",
        ),
        rect(0, 58, 1200, 38, "#323233"),
        text(22, 83, "Редактор (ілюстрація структури проєкту)", "#eeeeee", 17),
        rect(0, 96, 314, 574, "#252526"),
        text(22, 127, "EXPLORER · ПРИКЛАД", "#c5c5c5", 16, "bold"),
        rect(314, 96, 886, 38, "#2d2d2d"),
        text(340, 122, "filetr.py", "#e5e5e5", 18),
    ]
    files = [
        "▾ lab4_text_translation",
        "  ▾ translation_package",
        "    __init__.py",
        "    gtrans4.py",
        "    gtrans3.py",
        "    deeptr.py",
        "  ▾ report",
        "    Звіт_ЛР4_Чумако.docx",
        "  config.json",
        "  filetr.py",
        "  gtrans4.py",
        "  gtrans3.py",
        "  deeptr.py",
        "  sample_uk.txt",
        "  requirements.txt",
    ]
    for index, filename in enumerate(files):
        elements.append(text(20, 159 + index * 29, filename, "#dddddd", 15))

    for index, line in enumerate((ROOT / "filetr.py").read_text(encoding="utf-8").splitlines()[:25], 1):
        y = 162 + (index - 1) * 19
        if y > 643:
            break
        elements.append(text(336, y, f"{index:>2}", "#777777", 14))
        elements.append(text(390, y, line[:91], "#d4d4d4", 14))

    elements += [
        rect(0, 670, 1200, 50, "#1d5b7e"),
        text(20, 701, "МАКЕТ · не підтверджує реальний запуск", "#ffffff", 16, "bold"),
        text(894, 701, "Python 3.13 · demo", "#ffffff", 15),
    ]
    return svg(1200, 720, elements)


def terminal_panel(command: str, output: str) -> str:
    """Зображення у стилі прикладу користувача з видимим маркуванням."""
    lines: list[str] = []
    for line in output.strip().splitlines():
        lines.extend(wrap(line, width=93, break_long_words=False) or [""])
    if len(lines) > 12:
        raise ValueError(f"Вивід {command} задовгий для ілюстрації.")

    elements = [
        rect(0, 0, 1200, 540, "#2d3340"),
        rect(15, 64, 1170, 415, "#0a0f16"),
        rect(0, 0, 1200, 56, "#ffd166"),
        text(
            19, 36, "ІЛЮСТРАЦІЯ З РЕАЛЬНОГО ВИВОДУ REPLIT · НЕ СКРИНШОТ VS CODE",
            "#22202c", 20, "bold",
        ),
        text(26, 102, f"$ python {command}", "#d6dee7", 20),
    ]
    for index, line in enumerate(lines):
        elements.append(text(26, 142 + index * 27, line, "#d6dee7", 19))
    elements += [
        rect(0, 490, 1200, 50, "#29313e"),
        text(
            19, 523, "Зразок оформлення — не доказ роботи середовища «Чумако»",
            "#fff2c2", 17, "bold",
        ),
    ]
    return svg(1200, 540, elements)


def terminal_image() -> str:
    if sys.version_info < (3, 13):
        raise RuntimeError("Ілюстрація помилки gtrans3 потребує Python 3.13+.")
    result = subprocess.run(
        [sys.executable, "gtrans3.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    return terminal_panel("gtrans3.py", result.stdout)


def filetr_image() -> str:
    result = subprocess.run(
        [sys.executable, "filetr.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=40,
    )
    if "Мова перекладу: english (en)" not in result.stdout or "Переклад:\n" not in result.stdout:
        raise RuntimeError(f"filetr.py не повернув очікуваний переклад: {result.stdout}")
    return terminal_panel("filetr.py", result.stdout)


def build() -> None:
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("Для генерації ілюстрацій потрібен ImageMagick (magick).")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, image in (
        ("editor_demo", editor_image()),
        ("terminal_demo", terminal_image()),
        ("filetr_demo", filetr_image()),
    ):
        svg_file = OUTPUT / f"{name}.svg"
        png_file = OUTPUT / f"{name}.png"
        svg_file.write_text(image, encoding="utf-8")
        try:
            subprocess.run(
                [magick, "-background", "none", str(svg_file), str(png_file)],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            svg_file.unlink(missing_ok=True)
        print(f"Створено навчальну ілюстрацію: {png_file}")


if __name__ == "__main__":
    build()