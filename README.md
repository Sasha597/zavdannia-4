# Лабораторна робота №4 — модулі і пакети

**Виконав:** Чумако Олександр Олексійович, ІПЗ-23-к  
**Тема:** переклад тексту різними Python-бібліотеками.
**GitHub:** https://github.com/Sasha597/zavdannia-4

## Структура проєкту

```text
lab4_text_translation/
├── translation_package/
│   ├── __init__.py       # NAME, AUTHOR
│   ├── gtrans4.py        # googletrans 4.0.2, async, Python 3.13+
│   ├── gtrans3.py        # googletrans 3.1.0a0, Python 3.11
│   └── deeptr.py         # deep-translator + langdetect
├── gtrans4.py            # демонстрація першого модуля
├── gtrans3.py            # демонстрація другого модуля
├── deeptr.py             # демонстрація третього модуля
├── filetr.py             # переклад файла за config.json
├── sample_uk.txt         # текст із шести українських речень
├── config.json
├── config_file.json      # приклад збереження перекладу у файл
├── requirements.txt
├── requirements-gtrans3.txt
├── tools/build_report.py # генератор редагованого звіту .docx
├── report/
└── tests/
```

## Підготовка середовища

За умовою основне **віртуальне середовище називається прізвищем студента** —
`Чумако`. Створіть його локально в каталозі `lab4_text_translation`
в **VS Code**. Ця папка додана до `.gitignore`, тому в GitHub потрапить
тільки код і список залежностей.

Windows PowerShell:

```powershell
py -3.13 -m venv Чумако
.\Чумако\Scripts\Activate.ps1
python --version
python -m pip install -r requirements.txt
python gtrans4.py
python deeptr.py
python filetr.py
```

Linux / macOS (коли Python 3.13 доступний як `python3.13`):

```bash
python3.13 -m venv Чумако
source Чумако/bin/activate
python -m pip install -r requirements.txt
python gtrans4.py
python deeptr.py
python filetr.py
```

Для перевірки **gtrans3.py** потрібен **окремий** Python 3.11:
версії `googletrans==4.0.2` і `googletrans==3.1.0a0` не можуть бути
встановлені одночасно в одному середовищі.

```powershell
deactivate
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
python -m pip install -r requirements-gtrans3.txt
py -3.11 gtrans3.py
```

Якщо запуск `py -3.11 gtrans3.py` не знаходить пакет у середовищі,
використайте `python gtrans3.py` **після активації `.venv311`**. Виклик
`py -3.13 gtrans3.py` окремо демонструє повідомлення про несумісну
версію для скриншота, потрібного у звіті. У Replit може не бути Windows
Python launcher `py`, тому ці команди призначені для VS Code у Windows.

> `requirements.txt` містить прямі залежності основного середовища;
> `requirements-gtrans3.txt` — альтернативного середовища Python 3.11.
> Деякі переклади залежать від доступності Google Translate, інтернету
> і лімітів сервісу. Функції повідомляють про помилки явно.

## Використання

Приклади запуску з каталогу проєкту:

```bash
python gtrans4.py
python deeptr.py
python filetr.py
```

Виклик таблиці з перекладами всіх мов:

```python
import asyncio
from translation_package import gtrans4
asyncio.run(gtrans4.LanguageList("screen", "Добрий день"))
```

Функція `LanguageList` друкує вирівняну таблицю або створює
`languages_<модуль>.csv` у поточній папці, коли `out="file"`.
Без `text` колонка перекладу не створюється. Переклад для всіх мов
вимагає багато запитів і може впертися в обмеження зовнішнього сервісу.

`config.json` містить:

| Поле | Значення |
| --- | --- |
| `input_file` | ім’я вхідного UTF-8 файла в корені проєкту |
| `target_language` | код або назва мови; приклад: `en` |
| `module` | `gtrans4`, `gtrans3` або `deeptr` |
| `output` | `screen` або `file` |
| `sentence_count` | додатне ціле число; `null` означає весь файл |

Основний приклад використовує модуль `gtrans4`; для перевірки інших
модулів змініть поле `module` на `deeptr` або `gtrans3` (останній
потрібно запускати з Python 3.11).

Для перевірки запису у файл використайте готову конфігурацію
`python filetr.py --config config_file.json`. Якщо цільова мова `en`,
результат буде записано у `sample_uk_en.txt`. На екран виводиться
повідомлення `Ok` та ім’я файла.
Інший конфігураційний файл можна передати через
`python filetr.py --config інший_конфіг.json`.

## Перевірки

```bash
python -m unittest discover -s tests -v
python -m compileall -q .
```

## Звіт та GitHub

Запустіть `python tools/build_report.py` з кореня проєкту, щоб
оновити редагований файл `report/Звіт_ЛР4_Чумако.docx`.
У розділі 5 уже вставлено три **демонстраційні ілюстрації** з папки
`report/illustrations/`. Це оформлені ілюстрації, а не скриншоти роботи
у VS Code чи доказ створення середовища `Чумако`. Два приклади термінала
містять справжній текстовий вивід, отриманий під час запуску в Replit.
Якщо потрібно змінити ілюстрації, запустіть
`python tools/build_demo_images.py` (потрібен ImageMagick),
потім знову `python tools/build_report.py`.
ПІБ, групу та посилання GitHub уже внесено. Перед здачею **додайте реальні**,
а не згенеровані, скриншоти VS Code та термінала й назву навчального закладу.
Обов’язково покажіть на
скриншотах активне середовище `Чумако`, відповідність мови перекладу
полю `target_language` та повідомлення `gtrans3.py` на Python 3.13+.

Репозиторій лабораторної:

https://github.com/Sasha597/zavdannia-4

Коли завершите скриншоти, додайте їх до звіту і завантажте оновлений
DOCX до цього самого репозиторію.