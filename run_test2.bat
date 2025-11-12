@echo off
chcp 65001 > nul

echo === Запуск тестов этапа 2 ===
echo.

echo 1. Тест с React 18.2.0:
python dependency_visualizer.py test_configs/config2.ini
echo.

echo 2. Тест с другим пакетом:
python dependency_visualizer.py test_configs/config_express.ini
echo.

echo === Все тесты завершены ===
pause