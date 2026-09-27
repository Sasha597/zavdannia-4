"""Створює редагований DOCX-звіт без сторонніх залежностей."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "Звіт_ЛР4_Чумако.docx"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def paragraph(text: str, style: str = "Normal", *, page_break: bool = False) -> str:
    text = escape(text)
    props = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
    content = '<w:r><w:br w:type="page"/></w:r>' if page_break else ""
    content += f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r>'
    return f"<w:p>{props}{content}</w:p>"


def section(title: str, lines: list[str]) -> list[str]:
    return [paragraph(title, "Heading1")] + [paragraph(line) for line in lines]


def document_xml() -> str:
    body: list[str] = []
    body.extend(
        [
            paragraph("НАЗВА НАВЧАЛЬНОГО ЗАКЛАДУ: _________________________", "Subtitle"),
            paragraph("ЛАБОРАТОРНА РОБОТА №4", "Title"),
            paragraph("Тема: Модулі і пакети", "Subtitle"),
            paragraph("Дисципліна: _________________________"),
            paragraph("Виконав: Чумако Олександр Олексійович"),
            paragraph("Група: ІПЗ-23-к"),
            paragraph("Викладач: _________________________"),
            paragraph("2026", "Subtitle"),
            paragraph("", page_break=True),
        ]
    )

    body.extend(
        section(
            "1. Текст завдання",
            [
                "1. Створити віртуальне оточення з назвою-прізвищем студента і Python-проєкт.",
                "2. Створити пакет із трьох модулів. У __init__.py задати NAME = «Text translation» і AUTHOR = «Прізвище та ім’я студента, група».",
                "3. Реалізувати асинхронні TransLate(text, scr, dest), LangDetect(text, set='all'), CodeLang(lang) і LanguageList(out='screen', text=None) на googletrans 4.0.2 для Python 3.13+.",
                "4. Реалізувати ті самі функції на googletrans 3.1.0a0, передбачивши повідомлення про несумісність Python 3.13+ і запуск через Python 3.11.",
                "5. Реалізувати ті самі функції на deep-translator; для визначення мови можна використати langdetect.",
                "6. Створити gtrans4.py, gtrans3.py та deeptr.py із демонстрацією функцій кожного модуля.",
                "7. Створити filetr.py, вхідний файл із не менш як чотирма українськими реченнями та конфігураційний файл. Конфігурація містить назву файла, цільову мову, модуль, спосіб виводу і кількість речень.",
                "8. filetr.py виводить назву файла, розмір, число символів, число речень і мову; перекладає задану кількість речень. Для screen показує назву мови, модуль і переклад; для file створює файл із кодом мови в назві та повідомляє «Ok».",
                "9. Додати requirements.txt, .gitignore, завантажити проєкт на GitHub.",
                "10. Підготувати електронний звіт із титульним аркушем, текстом завдання, кодом основної програми, скриншотами VS Code та термінала (включно з помилкою для gtrans3 на Python 3.13+) і посиланням на GitHub.",
                "Параметри LangDetect: lang — тільки мова; confidence — тільки коефіцієнт довіри; all — обидва значення. CodeLang перетворює назву на код і навпаки. LanguageList друкує вирівняну таблицю або записує її до файла; колонка перекладу відсутня, якщо параметр text не вказано.",
            ],
        )
    )
    body.extend(
        section(
            "2. Мета та короткий опис виконання",
            [
                "Мета: навчитись створювати Python-пакети, використовувати сторонні бібліотеки та віртуальні середовища, реалізовувати асинхронні функції і конфігураційні файли.",
                "Створений пакет translation_package має модулі gtrans4, gtrans3 та deeptr. Головна програма filetr.py читає config.json і sample_uk.txt, перевіряє конфігурацію, рахує характеристики тексту, перекладає задану кількість речень і виводить або зберігає результат.",
                "Для googletrans 3.1.0a0 передбачено окреме середовище Python 3.11. Воно несумісне за версією пакета з основним середовищем googletrans 4.0.2.",
            ],
        )
    )
    body.extend(
        section(
            "3. Структура проєкту",
            [
                "translation_package/__init__.py — NAME та AUTHOR",
                "translation_package/gtrans4.py — асинхронні функції на googletrans 4.0.2",
                "translation_package/gtrans3.py — синхронні функції на googletrans 3.1.0a0",
                "translation_package/deeptr.py — функції на deep-translator і langdetect",
                "gtrans4.py, gtrans3.py, deeptr.py — демонстраційні програми",
                "filetr.py, config.json, sample_uk.txt — переклад із файла",
                "requirements.txt, requirements-gtrans3.txt, .gitignore — залежності та службові винятки",
            ],
        )
    )

    body.append(paragraph("4. Текст коду головної програми (filetr.py)", "Heading1"))
    for line in (ROOT / "filetr.py").read_text(encoding="utf-8").splitlines():
        body.append(paragraph(line, "Code"))

    body.extend(
        section(
            "5. Скриншоти, які слід додати перед здачею",
            [
                "[МІСЦЕ ДЛЯ СКРІНШОТА 1] Вікно VS Code: Explorer зі структурою завершеного проєкту, рядок стану з активним Python-середовищем «Чумако» і фрагмент filetr.py.",
                "[МІСЦЕ ДЛЯ СКРІНШОТІВ 2–4] Термінал із запуском gtrans4.py, deeptr.py, gtrans3.py на Python 3.11 та filetr.py. Видно активне середовище і цільову мову en, яку вказано в config.json.",
                "[МІСЦЕ ДЛЯ СКРІНШОТА 5] Термінал із повідомленням gtrans3.py про неправильну версію Python 3.13 або вище.",
                "Не підміняйте скриншоти зразками: зробіть їх після фактичного запуску програм у своєму середовищі.",
            ],
        )
    )
    body.extend(
        section(
            "6. Посилання на GitHub",
            ["https://github.com/Sasha597/zavdannia-4"],
        )
    )
    body.extend(
        section(
            "7. Висновок",
            [
                "У роботі реалізовано пакет із трьома модулями для перекладу й визначення мови. Розділено середовища для несумісних версій googletrans, додано керування з конфігураційного файла, перевірку помилок і збереження результату у файл.",
            ],
        )
    )

    sect = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" '
        'w:left="1417" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}" xmlns:r="{R_NS}"><w:body>'
        + "".join(body)
        + sect
        + "</w:body></w:document>"
    )


def build() -> Path:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        "</Types>"
    )
    root_relationships = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="word/document.xml"/></Relationships>'
    )
    styles = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:styles xmlns:w="{W_NS}">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
        '<w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        '<w:sz w:val="24"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:sz w:val="28"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
        '<w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/>'
        '<w:pPr><w:spacing w:after="0"/></w:pPr><w:rPr>'
        '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>'
        '<w:sz w:val="16"/></w:rPr></w:style>'
        "</w:styles>"
    )

    with ZipFile(REPORT, "w", compression=ZIP_DEFLATED) as document:
        document.writestr("[Content_Types].xml", content_types)
        document.writestr("_rels/.rels", root_relationships)
        document.writestr("word/document.xml", document_xml())
        document.writestr("word/styles.xml", styles)
        document.writestr(
            "word/_rels/document.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
        )
    return REPORT


if __name__ == "__main__":
    print(f"Звіт збережено: {build()}")