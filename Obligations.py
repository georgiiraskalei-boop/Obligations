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
    img = cv2.imdecode(np.fromfile(str(true_way), dtype=np.uint8), cv2.IMREAD_COLOR)
    results = reader.readtext(img, detail=0)
    
    with open("raw_text.json", "w", encoding="utf-8") as workfile:
        json.dump(results, workfile, ensure_ascii=False, indent=4)
    return results 

class work_with_json:
     def __init__(self, results):
          self.results=results
          self.data={}
          self.all_dates=[]

     def ovdp(self):
        fovdp = 'OVDP'
        for line in self.results:
            if 'ОВДП' in line:
                words = line.split()
                for word in words:
                    if word.startswith('UA'):
                        self.data[fovdp] = word
                        break
                       
        return self.data
     
     def procent(self):
          procent='PROCENT'
          for line in self.results:
               if '%' in line:
                    words=line.split()
                    for word in words:
                        if '%' in word:
                             clean_word=word.replace('%','')
                             self.data[procent]=clean_word
                             break
          return self.data

     def count(self):
        fcount = 'COUNT'
        for line in self.results:
            if 'шт' in line.lower() and line.strip(' .,:').lower().endswith('шт'):
            # Очищаем строку от 'шт' и лишних пробелов
                cleaned = line.lower().replace('шт', '').strip()
                self.data[fcount] = cleaned
                break
        return self.data

     def buy_sum(self):
        bsum = 'SUM OF BUY'
        for line in self.results:
            cleaned_line = line.strip(' ,.')
            if len(cleaned_line) >= 7 and cleaned_line.endswith('UAH'):
                try:
                    # Сначала убираем 'UAH' и сохраняем в новую переменную, затем парсим
                    num_str = cleaned_line.replace('UAH', '').strip()
                    val = float(num_str)
                    self.data[bsum] = val
                    return self.data
                except ValueError:
                    continue
        return self.data

     def dates(self):
         date_format = r'\d{2}[.,]\d{2}[.,]\d{4}'
         for line in self.results:
             # Заменяем запятые на точки, чтобы OCR-мусор не ломал поиск
             cleaned_line = line.replace(',', '.')
             found = re.findall(date_format, cleaned_line)
             self.all_dates.extend(found)
             
         if not self.all_dates:
            return None
         return self.all_dates

     def final_dates(self):
        date_format = []
        fdata = "FINAL DATE"
        for date_str in self.all_dates: 
            parsed_date = datetime.strptime(date_str, '%d.%m.%Y') 
            date_format.append(parsed_date)    
        finall_date = max(date_format)
        self.data[fdata] = finall_date.strftime('%d.%m.%Y') 
        return self.data
     
     def cupon_dates(self):
         cdata = "COUPON DATES"
         # Парсим строки в datetime, чтобы убрать дубли и отсортировать по хронологии, а не по строкам
         parsed_dates = [datetime.strptime(d, '%d.%m.%Y') for d in self.all_dates]
         unique_dates = sorted(list(set(parsed_dates)))
         
         # Переводим обратно в читаемый строковый формат для словаря
         self.data[cdata] = [d.strftime('%d.%m.%Y') for d in unique_dates]
         return self.data

     def cupon_body(self):
        pattern = r'\d+[\.,]\d{2}'
        all_amounts = []
        for line in self.results:
            found = re.findall(pattern, line)
            all_amounts.extend(found)
        if not all_amounts:
            return None
        counter = Counter(all_amounts)
        most_common_amount, _ = counter.most_common(1)[0]
        self.data["COUPON"] = most_common_amount
        return self.data                 
        
class Finance_Analyzer():
    def __init__(self, data):
        self.data = data

    def all_cupons(self):
        cupon_dates_count = float( len(self.data['COUPON DATES']))
        cupon_body= float(self.data['COUPON'])
        cupon_count= float(self.data['COUNT'])
        cupon_tot_sum= float(cupon_dates_count*cupon_body*cupon_count)
        self.data['TOTAL COPON SUM']=cupon_tot_sum
        return(self.data)
    
    def body_return(self):
        ukr_nominal = 1000
        count_val = int(self.data['COUNT'])
        breturn = count_val * ukr_nominal
        self.data['TOTAL RETURN SUM'] = float(breturn)  # можно оставить float для единообразия в отчетах
        print(self.data)
        return self.data
      

def main():
    true_way=take_data()
    results=to_json(true_way)
    processor=work_with_json(results)
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
    
    input("\nНажми Enter, чтобы закрыть программу...")
if __name__=='__main__':
     main()    
