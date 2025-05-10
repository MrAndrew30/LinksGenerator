#!/bin/bash

# Прерывать выполнение при ошибках
set -e

# Очистка предыдущих сборок
pip uninstall -y links-generator 2>/dev/null || true
rm -rf dist/ build/ *.egg-info/

# Сборка пакета
python -m build --no-isolation

# Установка пакета
pip install dist/*.whl --force-reinstall

# Сборка документации
rm -rf docs/build/
sphinx-build -b html docs/source/ docs/build/html

echo "Сборка успешно завершена!"

find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".mypy_cache" -exec rm -rf {} +