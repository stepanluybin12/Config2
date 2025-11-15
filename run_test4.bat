@echo off
chcp 65001 > nul

echo === ТЕСТИРОВАНИЕ ЭТАПА 4 - ОБРАТНЫЕ ЗАВИСИМОСТИ ===
echo.

echo 1. Простой граф - обратные зависимости для D:
python dependency_visualizer.py test_configs/Config4.ini test_configs/graph.txt
echo.
pause

echo 2. Граф с циклами - обратные зависимости:
python dependency_visualizer.py test_configs/Config4.ini test_configs/graph_cycle.txt
echo.
pause

echo === ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===