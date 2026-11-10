from Obligations import parse_single_bond
from pathlib import Path
from datetime import datetime
import json

# Глобальный список для накопления
t_list = []
file_path = Path("total_list.json")

# 1. Сразу проверяем диск при запуске: если файл есть — грузим из него данные в t_list
if file_path.is_file():
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            t_list = json.load(f)
    except Exception:
        t_list = []

def remove_expired_bonds(bonds_list):
    """Фильтрует список, удаляя облигации с истекшим сроком погашения."""
    current_date = datetime.now()
    active_bonds = []
    
    for bond in bonds_list:
        date_str = bond.get('FINAL DATE')
        if date_str:
            try:
                final_date = datetime.strptime(date_str, '%d.%m.%Y')
                # Если финальная дата больше или равна текущей — бумага активна
                if final_date >= current_date:
                    active_bonds.append(bond)
            except ValueError:
                # Если вдруг формат даты поврежден, оставляем бумагу на всякий случай
                active_bonds.append(bond)
        else:
            active_bonds.append(bond)
            
    return active_bonds
class Total:
    def __init__(self):
        # Получаем свежую бумагу через твой парсер
        self.new_data = parse_single_bond()
        
        if self.new_data:
            # Добавляем в общий список
            t_list.append(self.new_data)

    def save_json(self):
        """Сохраняем весь список на жесткий диск"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(t_list, f, ensure_ascii=False, indent=4)
            print("Файл успешно сохранен на диск!")
        except Exception as e:
            print(f"[Ошибка сохранения]: {e}")

    def counter(self):
        total_buy = 0.0
        total_coupon = 0.0
        total_return = 0.0
        total_count = 0

        # Пробегаемся по каждой облигации в общем списке t_list
        for dictionary in t_list:
            total_buy += float(dictionary.get('SUM OF BUY', 0.0))
            total_coupon += float(dictionary.get('TOTAL COPON SUM', 0.0))
            total_return += float(dictionary.get('TOTAL RETURN SUM', 0.0))
            total_count += int(dictionary.get('COUNT', 0))

        # Собираем общие итоги в один отдельный словарь
        portfolio_summary = {
            "TOTAL PAPERS COUNT": total_count,
            "TOTAL BUY SUM": round(total_buy, 2),
            "TOTAL COUPON INCOME": round(total_coupon, 2),
            "TOTAL RETURN SUM": round(total_return, 2)
        }

        print("\n--- ИТОГИ ПОРТФЕЛЯ ---")
        print(portfolio_summary)
        
        return portfolio_summary
    
def main():
    portfolio = Total()
    portfolio.save_json()
    portfolio.counter()
if __name__ == '__main__':
    main()