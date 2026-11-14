import sys
from pathlib import Path

# Добавляем текущую директорию в путь, чтобы питон железно видел локальные модули
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

from UI_for_obligations import BondPortfolioApp

def main():
    """
    Единая точка входа в приложение «Финансовый дневник / Портфель Облигаций».
    Инициализирует графический интерфейс и запускает главный цикл приложения.
    """
    try:
        app = BondPortfolioApp()
        app.mainloop()
    except Exception as e:
        print(f"[Критическая ошибка запуска приложения]: {e}")

if __name__ == "__main__":
    main()