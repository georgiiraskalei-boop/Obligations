from pathlib import Path
from datetime import datetime
import json

try:
    from Obligations import parse_single_bond
except ImportError:
    pass

file_path = Path("total_list.json")


def remove_expired_bonds(bonds_list):
    """Фильтрует список, удаляя облигации с истекшим сроком погашения."""
    current_date = datetime.now()
    active_bonds = []

    for bond in bonds_list:
        date_str = bond.get('FINAL DATE')
        if date_str:
            try:
                final_date = datetime.strptime(date_str, '%d.%m.%Y')
                if final_date >= current_date:
                    active_bonds.append(bond)
            except ValueError:
                active_bonds.append(bond)
        else:
            active_bonds.append(bond)

    return active_bonds


class Total:
    def __init__(self, use_cli_input=False):
        self.t_list = []
        self.load_json()

        if use_cli_input:
            self.new_data = parse_single_bond()
            if self.new_data:
                self.t_list.append(self.new_data)

    def load_json(self):
        """Загружаем список с жесткого диска"""
        if file_path.is_file():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.t_list = json.load(f)
            except Exception:
                self.t_list = []
        else:
            self.t_list = []
        return self.t_list

    def save_json(self):
        """Сохраняем весь список на жесткий диск"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.t_list, f, ensure_ascii=False, indent=4)
            print("Файл успешно сохранен на диск!")
        except Exception as e:
            print(f"[Ошибка сохранения]: {e}")

    def add_bond(self, bond_data: dict):
        if bond_data:
            self.t_list.append(bond_data)
            self.save_json()

    def update_bond(self, index: int, updated_data: dict):
        if 0 <= index < len(self.t_list):
            self.t_list[index] = updated_data
            self.save_json()

    def delete_bond(self, index: int):
        if 0 <= index < len(self.t_list):
            del self.t_list[index]
            self.save_json()

    def counter(self):
        total_buy = 0.0
        total_coupon = 0.0
        total_annual_coupon = 0.0
        total_return = 0.0
        total_count = 0

        for dictionary in self.t_list:
            try:
                total_buy += float(dictionary.get('SUM OF BUY', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                total_coupon += float(dictionary.get('TOTAL COPON SUM', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                total_annual_coupon += float(dictionary.get('ANNUAL COUPON INCOME', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                total_return += float(dictionary.get('TOTAL RETURN SUM', 0.0))
            except (ValueError, TypeError):
                pass

            raw_count = dictionary.get('COUNT', 0)
            try:
                total_count += int(raw_count)
            except (ValueError, TypeError):
                if str(raw_count).lower() in ['l', 'i', 'I']:
                    total_count += 1

        safe_withdrawal = total_buy * 0.03
        monthly_withdrawal = safe_withdrawal / 12

        portfolio_summary = {
            "TOTAL PAPERS COUNT": total_count,
            "TOTAL BUY SUM": round(total_buy, 2),
            "TOTAL COUPON INCOME": round(total_coupon, 2),
            "ANNUAL COUPON INCOME": round(total_annual_coupon, 2),
            "TOTAL RETURN SUM": round(total_return, 2),
            "SAFE WITHDRAWAL YEAR": round(safe_withdrawal, 2),
            "SAFE WITHDRAWAL MONTH": round(monthly_withdrawal, 2)
        }

        return portfolio_summary


def main():
    portfolio = Total(use_cli_input=True)
    portfolio.save_json()
    summary = portfolio.counter()
    print("\n--- ИТОГИ ПОРТФЕЛЯ ---")
    print(summary)


if __name__ == '__main__':
    main()