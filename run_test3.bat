@echo off
chcp 65001 > nul

echo === ТЕСТ 1: Простой граф (макс. глубина 3) ===
python dependency_visualizer.py test_configs\config.ini test_configs\graph.txt
echo.
pause

echo === ТЕСТ 2: Граф с циклами ===
python dependency_visualizer.py test_configs\config.ini test_configs\graph_cycle.txt
echo.
pause