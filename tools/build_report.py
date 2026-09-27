"""Створює редагований DOCX-звіт без сторонніх залежностей."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report" / "Звіт_ЛР4_Чумако.docx"
ILLUSTRATIONS = ROOT / "report" / "illustrations"

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


def image(name: str, rel_id: str, image_id: int, height: int) -> str:
    """Вставити PNG завширшки 6 дюймів з альтернативним описом."""
    width = 5486400
    description = escape(f"Навчальна ілюстрація {name}; не скриншот фактичного запуску.")
    return (
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
        '<wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<wp:extent cx="{width}" cy="{height}"/>'
        f'<wp:docPr id="{image_id}" name="{escape(name)}" descr="{description}"/>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr>'
        f'<pic:cNvPr id="{image_id}" name="{escape(name)}"/>'
        '<pic:cNvPicPr/></pic:nvPicPr>'
        '<pic:blipFill>'
        f'<a:blip r:embed="{rel_id}"/>'
        '<a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill><pic:spPr><a:xfrm>'
        f'<a:off x="0" y="0"/><a:ext cx="{width}" cy="{height}"/>'
        '</a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '</pic:spPr></pic:pic></a:graphicData></a:graphic>'
        '</wp:inline></w:drawing></w:r></w:p>'
    )


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
                "ЛАБОРАТОРНА РОБОТА №4. Тема: Модулі і пакети.",
                "1. Створити віртуальне оточення (ім’я оточення — прізвище студента). В цьому оточенні створити проєкт Python. Без виконання цього пункту завдання не буде зараховано.",
                "2. Створити пакет, який складається з трьох модулів. Назви пакета і модулів — на розсуд студента.",
                "3. У файлі __init__.py задати змінні NAME = «Text translation» та AUTHOR = «Прізвище та ім’я студента, група».",
                "4. У першому модулі створити наведені далі функції, використовуючи googletrans 4.0.2. Функції мають бути асинхронними і працювати з Python 3.13 та вище.",
                "TransLate(text: str, scr: str, dest: str) -> str: повертає переклад на задану мову або повідомлення про помилку. text — текст; scr — назва чи ISO-639-код мови оригіналу або «auto»; dest — назва чи ISO-639-код мови перекладу.",
                "LangDetect(text: str, set: str = «all») -> str: визначає мову та коефіцієнт довіри або повертає помилку. set = «lang» — лише мова; «confidence» — лише коефіцієнт; «all» (за замовчуванням) — обидва значення.",
                "CodeLang(lang: str) -> str: повертає код за назвою мови, назву за кодом або повідомлення про помилку.",
                "LanguageList(out: str = «screen», text: str = None) -> str: виводить у файл або на екран таблицю підтримуваних мов, їхніх кодів і перекладів тексту. Якщо text відсутній, колонка перекладу також відсутня. out = «screen» — екран; out = «file» — файл. Таблиця на екрані має мати заголовки та вирівняні ліворуч стовпці. Повернути «Ok» за успіху або повідомлення про помилку.",
                "5. У другому модулі створити ті самі функції за допомогою googletrans==3.1.0a0. Якщо Python >= 3.13, програма має показати повідомлення про несумісність.",
                "6. У третьому модулі створити ті самі функції за допомогою deep_translator. Для визначення мови можна використати langdetect.",
                "7. У кореневому каталозі проєкту створити файли gtrans4.py, gtrans3.py, deeptr.py та filetr.py.",
                "8. gtrans4.py демонструє роботу функцій першого модуля.",
                "9. gtrans3.py демонструє роботу другого модуля; для демонстрації використати Python launcher із Python 3.11.",
                "10. deeptr.py демонструє роботу третього модуля.",
                "11. filetr.py перекладає текст із файла. Попередньо створити в корені проєкту текстовий файл із щонайменше чотирма українськими реченнями та конфігураційний файл довільного типу.",
                "Конфігурація містить: назву файла з текстом, назву або код цільової мови, назву модуля пакета, місце виводу (файл або екран) і кількість речень, які потрібно прочитати та перекласти.",
                "Етап I: вивести назву файла, розмір, кількість символів, кількість речень у файлі та мову тексту; якщо файл відсутній або сталася помилка, показати відповідне повідомлення.",
                "Етап II: читати текст до кінця файла або до заданої кількості речень, після чого перекласти отриманий текст на мову з конфігурації функціями створеного пакета.",
                "Етап IV: для виводу на екран показати назву мови перекладу, назву використаного модуля і переклад або помилку.",
                "Етап V: для виводу у файл створити файл, додавши код мови перекладу до назви початкового файла, зберегти переклад; показати «Ok» або повідомлення про помилку.",
                "12. Створити requirements.txt з установленими модулями та пакетами.",
                "13. Створити .gitignore для технічних файлів і папок.",
                "14. Завантажити проєкт на GitHub.",
                "Форма подання — електронний звіт. Він має містити титульний аркуш; текст завдання; скриншот VS Code зі структурою проєкту (Explorer), рядком стану та кодом головної програми; текст коду головної програми; скриншоти термінала із запусками у віртуальному середовищі та мовою перекладу, що відповідає конфігурації; скриншот повідомлення gtrans3.py про неправильну версію Python 3.13+; посилання на GitHub.",
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

    body.append(paragraph("", page_break=True))
    body.extend(
        section(
            "5. Демонстраційні макети — не докази виконання",
            [
                "Наведені нижче зображення створено для ілюстрації оформлення. Це не скриншоти VS Code чи термінала студента і вони не підтверджують створення локального віртуального середовища «Чумако».",
            ],
        )
    )
    body.append(image("Макет редактора", "rId2", 1, 3291840))
    body.append(paragraph("Рис. 1. Макет вигляду редактора зі структурою проєкту (не скриншот VS Code)."))
    body.append(image("Приклад виводу filetr.py", "rId4", 3, 2468880))
    body.append(paragraph("Рис. 2. Реальний текстовий вивід filetr.py у Replit, оформлений за зразком; не скриншот VS Code чи середовища «Чумако»."))
    body.append(image("Приклад помилки gtrans3.py", "rId3", 2, 2468880))
    body.append(paragraph("Рис. 3. Реальний текстовий вивід gtrans3.py на Python 3.13 у Replit, оформлений за зразком; не скриншот середовища студента."))
    body.extend(
        section(
            "5.1. Справжні скриншоти, які слід додати перед здачею",
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
        '<Default Extension="png" ContentType="image/png"/>'
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
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId2" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            'Target="media/editor_demo.png"/>'
            '<Relationship Id="rId3" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            'Target="media/terminal_demo.png"/>'
            '<Relationship Id="rId4" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
            'Target="media/filetr_demo.png"/>'
            '</Relationships>',
        )
        for filename in ("editor_demo.png", "terminal_demo.png", "filetr_demo.png"):
            document.write(ILLUSTRATIONS / filename, f"word/media/{filename}")
    return REPORT


if __name__ == "__main__":
    print(f"Звіт збережено: {build()}")