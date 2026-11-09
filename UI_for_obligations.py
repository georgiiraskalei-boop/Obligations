import json
from pathlib import Path
import customtkinter as ctk
from customtkinter import filedialog

# Настройка темы
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

FILE_PATH = Path("total_list.json")

# Импортируем твои модули
try:
    from Obligations import to_json, work_with_json, Finance_Analyzer
except ImportError:
    pass


def process_image_file(image_path: Path) -> dict:
    """Парсинг картинки по выбранному пути без консольного ввода"""
    results = to_json(image_path)
    if not results:
        return {}

    processor = work_with_json(results)
    processor.ovdp()
    processor.procent()
    processor.count()
    processor.buy_sum()
    processor.dates()
    processor.final_dates()
    processor.cupon_dates()
    processor.cupon_body()

    analyzer = Finance_Analyzer(processor.data)
    analyzer.all_cupons()
    analyzer.body_return()
    analyzer.calculate_time_to_maturity()
    analyzer.matuarity_per_year()

    return analyzer.data


class EditBondWindow(ctk.CTkToplevel):
    """Модальное окно для ручного редактирования всех полей облигации"""
    def __init__(self, parent, bond_data: dict, on_save_callback):
        super().__init__(parent)
        self.title("Редактирование облигации")
        self.geometry("500x650")
        self.resizable(False, False)

        self.bond_data = bond_data
        self.on_save_callback = on_save_callback

        # Поверх главного окна
        self.transient(parent)
        self.grab_set()

        self._build_widgets()

    def _build_widgets(self):
        lbl = ctk.CTkLabel(
            self, text="✏️ Редактирование параметров", font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl.pack(pady=15)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.entries = {}

        fields = [
            ("OVDP", "Код ОВДП (ISIN):"),
            ("PROCENT", "Процентная ставка (%):"),
            ("COUNT", "Количество (шт):"),
            ("SUM OF BUY", "Сумма покупки (₴):"),
            ("FINAL DATE", "Дата погашения (ДД.ММ.ГГГГ):"),
            ("COUPON", "Размер 1 купона (₴):"),
        ]

        for key, title in fields:
            box = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            box.pack(fill="x", pady=6)

            ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=12)).pack(anchor="w")
            
            val = str(self.bond_data.get(key, ""))
            entry = ctk.CTkEntry(box, placeholder_text=title)
            entry.insert(0, val)
            entry.pack(fill="x", pady=(2, 0))

            self.entries[key] = entry

        # Кнопка Сохранить
        btn_save = ctk.CTkButton(
            self,
            text="💾 Сохранить изменения",
            fg_color="#27AE60",
            hover_color="#219150",
            command=self.save
        )
        btn_save.pack(pady=15)

    def save(self):
        # Обновляем базовые значения из текстовых полей
        self.bond_data["OVDP"] = self.entries["OVDP"].get().strip()
        self.bond_data["PROCENT"] = self.entries["PROCENT"].get().strip()
        
        raw_count = self.entries["COUNT"].get().strip()
        if raw_count.lower() in ['l', 'i', 'I']:
            raw_count = '1'
        self.bond_data["COUNT"] = raw_count

        try:
            self.bond_data["SUM OF BUY"] = float(self.entries["SUM OF BUY"].get().strip())
        except ValueError:
            self.bond_data["SUM OF BUY"] = 0.0

        self.bond_data["FINAL DATE"] = self.entries["FINAL DATE"].get().strip()
        self.bond_data["COUPON"] = self.entries["COUPON"].get().strip()

        # Пересчитываем аналитику с обновленными полями
        try:
            analyzer = Finance_Analyzer(self.bond_data)
            analyzer.all_cupons()
            analyzer.body_return()
            analyzer.calculate_time_to_maturity()
            analyzer.matuarity_per_year()
            self.bond_data = analyzer.data
        except Exception as e:
            print(f"[Ошибка перерасчета при изменении]: {e}")

        # Вызываем колбэк родителя для сохранения на диск и обновления UI
        self.on_save_callback(self.bond_data)
        self.destroy()


class BondPortfolioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Obligations Portfolio Manager")
        self.geometry("1000x820")
        self.minsize(900, 700)

        # Данные
        self.t_list = []
        self.load_data()

        # Построение интерфейса
        self._build_header()
        self._build_metrics_dashboard()
        self._build_cards_scroll_area()

        # Отображение данных
        self.refresh_ui()

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if FILE_PATH.is_file():
            try:
                with open(FILE_PATH, "r", encoding="utf-8") as f:
                    self.t_list = json.load(f)
            except Exception:
                self.t_list = []
        else:
            self.t_list = []

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.t_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[Ошибка сохранения]: {e}")

    def _build_header(self):
        """Верхняя шапка приложения с кнопками действий"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        title_label = ctk.CTkLabel(
            self.header_frame,
            text="💼 Портфель Облигаций",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left")

        # Кнопки справа
        btn_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_box.pack(side="right")

        self.btn_add = ctk.CTkButton(
            btn_box,
            text="➕ Добавить облигации",
            width=170,
            fg_color="#27AE60",
            hover_color="#219150",
            command=self.add_bond_from_file
        )
        self.btn_add.pack(side="left", padx=(0, 10))

        self.btn_reload = ctk.CTkButton(
            btn_box,
            text="🔄 Обновить",
            width=100,
            command=self.refresh_ui
        )
        self.btn_reload.pack(side="left")

    def _build_metrics_dashboard(self):
        """Панель итоговых показателей (6 метрик в 2 ряда)"""
        self.metrics_frame = ctk.CTkFrame(self, fg_color="#1E1E2E", corner_radius=12)
        self.metrics_frame.pack(fill="x", padx=20, pady=10)

        for i in range(3):
            self.metrics_frame.columnconfigure(i, weight=1)

        # Ряд 1: Базовые финансовые показатели
        self.lbl_count_val = self._create_metric_card(
            self.metrics_frame, "Всего бумаг", "0 шт", row=0, col=0
        )
        self.lbl_buy_val = self._create_metric_card(
            self.metrics_frame, "Инвестировано", "0.00 ₴", row=0, col=1
        )
        self.lbl_return_val = self._create_metric_card(
            self.metrics_frame, "Возврат номинала", "0.00 ₴", row=0, col=2
        )

        # Ряд 2: Доходность и купоны (включая годовые купоны и правило 3%)
        self.lbl_coupon_val = self._create_metric_card(
            self.metrics_frame, "Купонный доход (всего)", "0.00 ₴", row=1, col=0, text_color="#2ECC71"
        )
        self.lbl_annual_coupon_val = self._create_metric_card(
            self.metrics_frame, "Купонный доход в год", "0.00 ₴", row=1, col=1, text_color="#2ECC71"
        )
        self.lbl_safe_withdrawal_val = self._create_metric_card(
            self.metrics_frame, "Безопасное снятие (3%)", "0.00 ₴", row=1, col=2, text_color="#3498DB"
        )

    def _create_metric_card(self, parent, title, default_val, row, col, text_color=None):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=row, column=col, padx=15, pady=12, sticky="ew")

        t_lbl = ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=11), text_color="#A0A0AB"
        )
        t_lbl.pack(anchor="w")

        v_lbl = ctk.CTkLabel(
            card,
            text=default_val,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=text_color if text_color else "#FFFFFF"
        )
        v_lbl.pack(anchor="w", pady=(2, 0))
        return v_lbl

    def _build_cards_scroll_area(self):
        """Прокручиваемая область для карточек"""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Список облигаций (свежие сверху)",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

    def add_bond_from_file(self):
        """Множественный выбор файлов скриншотов пачкой и их автопарсинг"""
        file_paths = filedialog.askopenfilenames(
            title="Выберите скриншоты облигаций (можно выделить несколько)",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Все файлы", "*.*")]
        )
        if not file_paths:
            return

        for file_path in file_paths:
            image_path = Path(file_path)
            new_data = process_image_file(image_path)
            
            if new_data:
                self.t_list.append(new_data)

        self.save_data()
        self.refresh_ui()

    def edit_bond(self, original_index: int):
        """Открытие модального окна для редактирования выбранной записи"""
        if 0 <= original_index < len(self.t_list):
            bond_data = self.t_list[original_index]

            def on_save(updated_data):
                self.t_list[original_index] = updated_data
                self.save_data()
                self.refresh_ui()

            EditBondWindow(self, bond_data, on_save)

    def delete_bond(self, original_index: int):
        """Удаление облигации по её оригинальному индексу"""
        if 0 <= original_index < len(self.t_list):
            del self.t_list[original_index]
            self.save_data()
            self.refresh_ui()

    def refresh_ui(self):
        """Обновление интерфейса"""
        self.load_data()
        self._update_metrics()
        self._render_bond_cards()

    def _update_metrics(self):
        """Расчет и обновление тоталов с безопасным приведением типов"""
        tot_buy = 0.0
        tot_coupon = 0.0
        tot_annual_coupon = 0.0
        tot_return = 0.0
        tot_count = 0

        for bond in self.t_list:
            try:
                tot_buy += float(bond.get('SUM OF BUY', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                tot_coupon += float(bond.get('TOTAL COPON SUM', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                tot_annual_coupon += float(bond.get('ANNUAL COUPON INCOME', 0.0))
            except (ValueError, TypeError):
                pass

            try:
                tot_return += float(bond.get('TOTAL RETURN SUM', 0.0))
            except (ValueError, TypeError):
                pass

            raw_count = bond.get('COUNT', 0)
            try:
                tot_count += int(raw_count)
            except (ValueError, TypeError):
                if str(raw_count).lower() in ['l', 'i', 'I']:
                    tot_count += 1

        safe_withdrawal = tot_buy * 0.03

        self.lbl_count_val.configure(text=f"{tot_count} шт")
        self.lbl_buy_val.configure(text=f"{tot_buy:,.2f} ₴")
        self.lbl_return_val.configure(text=f"{tot_return:,.2f} ₴")
        self.lbl_coupon_val.configure(text=f"{tot_coupon:,.2f} ₴")
        self.lbl_annual_coupon_val.configure(text=f"{tot_annual_coupon:,.2f} ₴")
        self.lbl_safe_withdrawal_val.configure(text=f"{safe_withdrawal:,.2f} ₴")

    def _render_bond_cards(self):
        """Отрисовка карточек с кнопками редактирования и удаления"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.t_list:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="Список пуст. Нажмите «➕ Добавить облигации», чтобы распознать скриншоты!",
                font=ctk.CTkFont(size=14),
                text_color="#71717A"
            )
            empty_lbl.pack(pady=40)
            return

        for orig_idx in range(len(self.t_list) - 1, -1, -1):
            bond = self.t_list[orig_idx]
            self._execute_card_creation(bond, orig_idx)

    def _execute_card_creation(self, bond, orig_idx):
        card = ctk.CTkFrame(self.scroll_frame, fg_color="#27272A", corner_radius=10)
        card.pack(fill="x", pady=6, padx=5)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(10, 5))

        title = bond.get('OVDP', 'ОБЛИГАЦИЯ')
        lbl_title = ctk.CTkLabel(
            top_row,
            text=f"📌 {title}",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        lbl_title.pack(side="left")

        right_box = ctk.CTkFrame(top_row, fg_color="transparent")
        right_box.pack(side="right")

        procent = bond.get('PROCENT', '0')
        badge_proc = ctk.CTkLabel(
            right_box,
            text=f"  {procent}%  ",
            fg_color="#3F3F46",
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        badge_proc.pack(side="left", padx=(0, 10))

        # Кнопка Редактировать
        btn_edit = ctk.CTkButton(
            right_box,
            text="✏️ Изменить",
            width=80,
            height=24,
            fg_color="#D35400",
            hover_color="#E67E22",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda idx=orig_idx: self.edit_bond(idx)
        )
        btn_edit.pack(side="left", padx=(0, 5))

        # Кнопка Удалить
        btn_del = ctk.CTkButton(
            right_box,
            text="🗑 Удалить",
            width=80,
            height=24,
            fg_color="#E74C3C",
            hover_color="#C0392B",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda idx=orig_idx: self.delete_bond(idx)
        )
        btn_del.pack(side="left")

        sep = ctk.CTkFrame(card, height=1, fg_color="#3F3F46")
        sep.pack(fill="x", padx=15, pady=3)

        grid_frame = ctk.CTkFrame(card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(5, 10))

        # Показ суммы покупки с защитой от ошибок
        try:
            sum_buy_val = f"{float(bond.get('SUM OF BUY', 0.0)):,.2f} ₴"
        except (ValueError, TypeError):
            sum_buy_val = f"{bond.get('SUM OF BUY', 0.0)} ₴"

        fields = [
            ("Количество:", f"{bond.get('COUNT', 0)} шт"),
            ("Покупка:", sum_buy_val),
            ("Купон (всего):", f"{float(bond.get('TOTAL COPON SUM', 0.0)):,.2f} ₴"),
            ("Купон в год:", f"{float(bond.get('ANNUAL COUPON INCOME', 0.0)):,.2f} ₴"),
            ("Возврат:", f"{float(bond.get('TOTAL RETURN SUM', 0.0)):,.2f} ₴"),
            ("Погашение:", bond.get('FINAL DATE', '-'))
        ]

        for idx, (label, val) in enumerate(fields):
            r = idx // 3
            c = idx % 3

            box = ctk.CTkFrame(grid_frame, fg_color="transparent")
            box.grid(row=r, column=c, sticky="ew", pady=4, padx=5)
            grid_frame.columnconfigure(c, weight=1)

            ctk.CTkLabel(
                box, text=label, font=ctk.CTkFont(size=11), text_color="#A0A0AB"
            ).pack(anchor="w")

            ctk.CTkLabel(
                box, text=val, font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w")


if __name__ == "__main__":
    app = BondPortfolioApp()
    app.mainloop()