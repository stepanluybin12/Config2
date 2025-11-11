@echo off
REM Включаем поддержку UTF-8
chcp 65001 > nul

echo === Запуск тестов конфигурации ===
echo.

echo 1. Тест с отсутствующей секцией:
python dependency_visualizer.py test_configs\config_missing_section.ini
echo.

echo 2. Тест с пустыми значениями:
python dependency_visualizer.py test_configs\config_empty_values.ini
echo.

echo 3. Тест с невалидным test_mode:
python dependency_visualizer.py test_configs\config_invalid_test_mode.ini
echo.

echo 4. Тест с несуществующим файлом:
python dependency_visualizer.py non_existent_config.ini
echo.

echo 5. Тест с основным конфигом:
python dependency_visualizer.py test_configs\config.ini
echo.

pause