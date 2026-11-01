#!/usr/bin/env python3
"""Локальная проверка HTML-сборки АРХИУМА перед публикацией."""
from argparse import ArgumentParser
from hashlib import sha256
from html import unescape
from pathlib import Path
import re
import sys

parser = ArgumentParser(description="Проверка релиза ARCHIUM")
parser.add_argument("html", type=Path, help="HTML-файл")
parser.add_argument("--version", help="Ожидаемый номер версии, например 6.51")
parser.add_argument("--max-mib", type=float, default=10.0)
args = parser.parse_args()

if not args.html.is_file():
    parser.error("HTML-файл не найден")

raw = args.html.read_bytes()
try:
    content = raw.decode("utf-8")
except UnicodeDecodeError:
    sys.exit("Ошибка: HTML не в UTF-8")

errors, warnings = [], []
title_match = re.search(r"<title\b[^>]*>(.*?)</title\s*>", content, re.I | re.S)
title = unescape(re.sub(r"<[^>]*>", "", title_match.group(1))).strip() if title_match else ""
if not title:
    errors.append("Отсутствует заголовок <title>")
if args.version and not re.search(r"(?<!\d)v?" + re.escape(args.version) + r"(?!\d)", title, re.I):
    errors.append("Номер версии не совпадает с заголовком")
if not re.search(r"<meta\s+name=[\"']viewport[\"']", content, re.I):
    warnings.append("Не найден meta viewport")
if re.search(r"(?<!\w)(?:контур|kontur)(?!\w)", content, re.I):
    errors.append("Найдено упоминание удалённого модуля «КОНТУР»")
if len(raw) > args.max_mib * 1024 ** 2:
    warnings.append("Большой HTML; изображения желательно выносить постепенно")
if not re.search(r"<html\b", content, re.I) or not re.search(r"</html\s*>", content, re.I):
    errors.append("Неполная HTML-структура")
print(f"Файл: {args.html.name}")
print(f"Размер: {len(raw)/1024**2:.2f} МиБ")
print(f"Заголовок: {title}")
print(f"SHA-256: {sha256(raw).hexdigest()}")
for item in warnings:
    print("Предупреждение:", item)
for item in errors:
    print("Ошибка:", item)
print("Важно: проверка не заменяет запуск сайта и тест в Safari")
sys.exit(1 if errors else 0)
