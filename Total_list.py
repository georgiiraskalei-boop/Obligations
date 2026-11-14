from pathlib import Path
from datetime import datetime
import sqlite3

try:
    from Obligations import parse_single_bond
except ImportError:
    pass

db_path = Path("Database.db")


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
        self._init_db()     # 1. Создаем таблицу (если её нет)
        self.load_from_db() # 2. Загружаем данные из базы

        if use_cli_input:
            self.new_data = parse_single_bond()
            if self.new_data:
                self.add_bond(self.new_data)

    def _init_db(self):
        """Создает таблицу для облигаций, если она еще не существует"""
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bonds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ovdp TEXT,
                    procent TEXT,
                    count TEXT,
                    sum_of_buy REAL,
                    final_date TEXT,
                    coupon TEXT,
                    total_coupon_sum REAL,
                    annual_coupon_income REAL,
                    total_return_sum REAL,
                    maturity_period TEXT
                )
            """)
            conn.commit()

    def load_from_db(self):
        """Загружает все облигации из базы данных в виде словарей"""
        self.t_list = []
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bonds")
            rows = cursor.fetchall()
            
            for row in rows:
                bond_dict = {
                    "id": row["id"],
                    "OVDP": row["ovdp"],
                    "PROCENT": row["procent"],
                    "COUNT": row["count"],
                    "SUM OF BUY": row["sum_of_buy"],
                    "FINAL DATE": row["final_date"],
                    "COUPON": row["coupon"],
                    "TOTAL COPON SUM": row["total_coupon_sum"],
                    "ANNUAL COUPON INCOME": row["annual_coupon_income"],
                    "TOTAL RETURN SUM": row["total_return_sum"],
                    "MATURITY PERIOD": row["maturity_period"]
                }
                self.t_list.append(bond_dict)
        return self.t_list

    def add_bond(self, bond_data: dict):
        """Добавляет новую облигацию в базу данных"""
        if bond_data:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO bonds (
                        ovdp, procent, count, sum_of_buy, final_date, 
                        coupon, total_coupon_sum, annual_coupon_income, 
                        total_return_sum, maturity_period
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    bond_data.get('OVDP'),
                    bond_data.get('PROCENT'),
                    bond_data.get('COUNT'),
                    bond_data.get('SUM OF BUY', 0.0),
                    bond_data.get('FINAL DATE'),
                    bond_data.get('COUPON'),
                    bond_data.get('TOTAL COPON SUM', 0.0),
                    bond_data.get('ANNUAL COUPON INCOME', 0.0),
                    bond_data.get('TOTAL RETURN SUM', 0.0),
                    bond_data.get('MATURITY PERIOD')
                ))
                conn.commit()
            self.load_from_db()

    def update_bond(self, index: int, updated_data: dict):
        """Обновляет облигацию в базе по её индексу в списке"""
        if 0 <= index < len(self.t_list):
            bond_id = self.t_list[index].get("id")
            if bond_id is not None:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE bonds SET 
                            ovdp = ?, procent = ?, count = ?, sum_of_buy = ?, 
                            final_date = ?, coupon = ?, total_coupon_sum = ?, 
                            annual_coupon_income = ?, total_return_sum = ?, maturity_period = ?
                        WHERE id = ?
                    """, (
                        updated_data.get('OVDP'),
                        updated_data.get('PROCENT'),
                        updated_data.get('COUNT'),
                        updated_data.get('SUM OF BUY', 0.0),
                        updated_data.get('FINAL DATE'),
                        updated_data.get('COUPON'),
                        updated_data.get('TOTAL COPON SUM', 0.0),
                        updated_data.get('ANNUAL COUPON INCOME', 0.0),
                        updated_data.get('TOTAL RETURN SUM', 0.0),
                        updated_data.get('MATURITY PERIOD'),
                        bond_id
                    ))
                    conn.commit()
                self.load_from_db()

    def delete_bond(self, index: int):
        """Удаляет облигацию из базы по её индексу"""
        if 0 <= index < len(self.t_list):
            bond_id = self.t_list[index].get("id")
            if bond_id is not None:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM bonds WHERE id = ?", (bond_id,))
                    conn.commit()
                self.load_from_db()

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
    summary = portfolio.counter()
    print("\n--- ИТОГИ ПОРТФЕЛЯ ---")
    print(summary)


if __name__ == '__main__':
    main()