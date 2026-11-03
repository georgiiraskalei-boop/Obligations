# TODO: Шаг 1. Импортировать нужные библиотеки (easyocr)
import easyocr
import json
from pathlib import Path
import numpy as np
import cv2
import re
from datetime import datetime
from statistics import mode, StatisticsError
from collections import Counter
# Objects
reader=easyocr.Reader(['uk','ru','en'])

# TODO: Шаг 2. Инициализировать ридер для работы с картинкой
def take_data():
        while True:   
            way=input('Print way:') 
            way=way.strip('\,",""')
            way=Path(way)
            if way.is_file():
                return(way)
            else:
                 print('Wrong way')

def to_json(true_way):
    try:
        img = cv2.imdecode(np.fromfile(str(true_way), dtype=np.uint8), cv2.IMREAD_COLOR)
        results = reader.readtext(img, detail=0)
        return results 
    except Exception as e:
        print(f"[Ошибка в функции to_json]: не удалось прочитать картинку или сохранить JSON -> {e}")
        return []

class work_with_json:
     def __init__(self, results):
          self.results=results
          self.data={}
          self.all_dates=[]

     def ovdp(self):
        try:
            fovdp = 'OVDP'
            for line in self.results:
                if 'ОВДП' in line:
                    words = line.split()
                    for word in words:
                        if word.startswith('UA'):
                            self.data[fovdp] = word
                            break
        except Exception as e:
            print(f"[Ошибка в функции ovdp]: {e}")
        return self.data
     
     def procent(self):
          try:
              procent='PROCENT'
              for line in self.results:
                   if '%' in line:
                        words=line.split()
                        for word in words:
                            if '%' in word:
                                 clean_word=word.replace('%','')
                                 self.data[procent]=clean_word
                                 break
          except Exception as e:
              print(f"[Ошибка в функции procent]: {e}")
          return self.data

     def count(self):
        try:
            fcount = 'COUNT'
            for line in self.results:
                if 'шт' in line.lower() and line.strip(' .,:').lower().endswith('шт'):
                    cleaned = line.lower().replace('шт', '').strip()
                    self.data[fcount] = cleaned
                    break
        except Exception as e:
            print(f"[Ошибка в функции count]: {e}")
        return self.data

     def buy_sum(self):
        try:
            bsum = 'SUM OF BUY'
            for line in self.results:
                cleaned_line = line.strip(' ,.')
                if len(cleaned_line) >= 7 and cleaned_line.endswith('UAH'):
                    try:
                        num_str = cleaned_line.replace('UAH', '').strip()
                        val = float(num_str)
                        self.data[bsum] = val
                        return self.data
                    except ValueError:
                        continue
        except Exception as e:
            print(f"[Ошибка в функции buy_sum]: {e}")
        return self.data

     def dates(self):
         try:
             date_format = r'\d{2}[.,]\d{2}[.,]\d{4}'
             for line in self.results:
                 cleaned_line = line.replace(',', '.')
                 found = re.findall(date_format, cleaned_line)
                 self.all_dates.extend(found)
                 
             if not self.all_dates:
                return None
         except Exception as e:
             print(f"[Ошибка в функции dates]: {e}")
         return self.all_dates

     def final_dates(self):
        try:
            if not self.all_dates:
                return self.data
            date_format = []
            fdata = "FINAL DATE"
            for date_str in self.all_dates: 
                parsed_date = datetime.strptime(date_str, '%d.%m.%Y') 
                date_format.append(parsed_date)    
            finall_date = max(date_format)
            self.data[fdata] = finall_date.strftime('%d.%m.%Y') 
        except Exception as e:
            print(f"[Ошибка в функции final_dates]: {e}")
        return self.data
     
     def cupon_dates(self):
         try:
             if not self.all_dates:
                 return self.data
             cdata = "COUPON DATES"
             parsed_dates = [datetime.strptime(d, '%d.%m.%Y') for d in self.all_dates]
             unique_dates = sorted(list(set(parsed_dates)))
             
             self.data[cdata] = [d.strftime('%d.%m.%Y') for d in unique_dates]
         except Exception as e:
             print(f"[Ошибка в функции cupon_dates]: {e}")
         return self.data

     def cupon_body(self):
        try:
            pattern = r'\d+[\.,]\d{2}'
            all_amounts = []
            for line in self.results:
                found = re.findall(pattern, line)
                all_amounts.extend(found)
            if all_amounts:
                counter = Counter(all_amounts)
                most_common_amount, _ = counter.most_common(1)[0]
                self.data["COUPON"] = most_common_amount
        except Exception as e:
            print(f"[Ошибка в функции cupon_body]: {e}")
        return self.data                 
        
class Finance_Analyzer():
    def __init__(self, data):
        self.data = data

    def all_cupons(self):
        try:
            cupon_dates_count = float(len(self.data.get('COUPON DATES', [])))
            cupon_body = float(self.data.get('COUPON', 0))
            cupon_count = float(self.data.get('COUNT', 1))
            cupon_tot_sum = float(cupon_dates_count * cupon_body * cupon_count)
            self.data['TOTAL COPON SUM'] = cupon_tot_sum
        except Exception as e:
            print(f"[Ошибка в Finance_Analyzer.all_cupons]: {e}")
        return self.data
    
    def body_return(self):
        try:
            ukr_nominal = 1000
            count_val = int(self.data.get('COUNT', 1))
            breturn = count_val * ukr_nominal
            self.data['TOTAL RETURN SUM'] = float(breturn)
        except Exception as e:
            print(f"[Ошибка в Finance_Analyzer.body_return]: {e}")
        return self.data
    
    def calculate_time_to_maturity(self):
        try:
            date_str = self.data.get('FINAL DATE')
            if date_str:
                final_date = datetime.strptime(date_str, '%d.%m.%Y')
                current_date = datetime.now()
                total_days = (final_date - current_date).days
                if total_days < 0:
                    total_days = 0
                years = total_days // 365
                remaining_days = total_days % 365
                months = remaining_days // 30 
                self.data['MATURITY PERIOD'] = f"{years} лет, {months} мес."
        except Exception as e:
            print(f"[Ошибка в Finance_Analyzer.calculate_time_to_maturity]: {e}")
        return self.data

    def matuarity_per_year(self):
        try:
            date_str = self.data.get('FINAL DATE')
            if date_str:
                final_date = datetime.strptime(date_str, '%d.%m.%Y')
                current_date = datetime.now()
                total_days = (final_date - current_date).days
                if total_days <= 0:
                    years = 1 
                else:
                    years = total_days / 365.25 
                total_coupon = float(self.data.get('TOTAL COPON SUM', 0))
                annual_income = total_coupon / years
                self.data['ANNUAL COUPON INCOME'] = round(annual_income, 2)
        except Exception as e:
            print(f"[Ошибка в Finance_Analyzer.matuarity_per_year]: {e}")
        return self.data

def parse_single_bond():
    true_way = take_data()
    results = to_json(true_way)
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
    print (analyzer.data)
    return analyzer.data

def main():
    parse_single_bond()
    input("\nНажми Enter, чтобы закрыть программу...")
if __name__=='__main__':
     main()
    