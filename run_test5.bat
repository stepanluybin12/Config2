@echo off
chcp 65001 > nul

echo === ТЕСТИРОВАНИЕ ЭТАПА 5 - ВИЗУАЛИЗАЦИЯ ===
echo.

echo 1. Визуализация для пакета A (простой граф):
python dependency_visualizer.py test_configs/config5_1.ini test_configs/graph.txt
echo.
pause

echo 2. Визуализация для пакета D (обратные зависимости):
python dependency_visualizer.py test_configs/config5_2.ini test_configs/graph.txt
echo.
pause

echo 3. Визуализация графа с циклами:
python dependency_visualizer.py test_configs/config5_1.ini test_configs/graph_cycle.txt
echo.
pause

echo === ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ===