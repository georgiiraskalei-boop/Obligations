# TODO: Шаг 1. Импортировать нужные библиотеки (easyocr)
import easyocr
import json
from pathlib import Path
import numpy as np
import cv2
import re
from datetime import datetime
from statistics import mode, StatisticsError
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

# TODO: Шаг 3. Написать блок выгрузки сырого текста:
# открыть картинку, прогнать через OCR без фильтрации 
# и записать результат построчно в промежуточный .txt файл

def to_txt(true_way):
    img = cv2.imdecode(np.fromfile(str(true_way), dtype=np.uint8), cv2.IMREAD_COLOR)
    results = reader.readtext(img, detail=0)
    with open("raw_text.txt", "w", encoding="utf-8") as workfile:
        for line in results:
            workfile.write(line + "\n")
    return(results)                   
                    
# TODO: Шаг 4. Написать функцию нормализации значений:
# принимать строку, проверять наличие точки, 
# если копеек нет — добивать '.00', возвращать нормализованное значение

def normalization_of_results(results):
    cleaned_data = []
    for line in results:
        cleaned = line.strip().replace("UAH", "").strip()
        cleaned = cleaned.replace("O", "0").replace("o", "0").replace(",", ".")
        
        # Безопасный перевод в число или сохранение текста как есть
        try:
            value = float(cleaned)
            cleaned_data.append(value)
        except ValueError:
            # Если это не число (название, ISIN), оставляем текст
            cleaned_data.append(cleaned)
            
    return cleaned_data


# TODO: Шаг 6. Упаковать очищенные и структурированные данные в JSON-файл
def to_json(cleaned_data):
    # Получаем папку, в которой лежит этот скрипт, и приклеиваем имя файла
    file_path = Path(__file__).parent / "portfolio_result.json"
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    return(file_path)

#    Достаем из файла нужные значения

def work_with_json(way_to_json):
    date_list = []
    cupon_date_list = []
    coupon_candidates = []
    ovdp = None
    ovdp_count = None
    final_date = None
    total_sum = None
    coupon_pattern = r"\b\d{2}\.\d{2}\b"

    with open(way_to_json, "r", encoding="utf-8") as file_to_parsing:
        data = json.load(file_to_parsing)
        for item in data:
            if isinstance(item, str):
                if "UA" in item:
                    ovdp = item
                elif "шт" in item.lower():
                    # Очищаем строку от лишних символов и переводим количество во float
                    count_clean = re.sub(r"[^\d.]", "", item.replace(",", "."))
                    try:
                        ovdp_count = float(count_clean)
                    except ValueError:
                        ovdp_count = 0.0
                
                # Сбор дат пишем прямо здесь, внутри общей проверки на строку
                for word in item.split():
                    clean_word = word.strip(".,/;")
                    if len(clean_word) == 10 and clean_word.count(".") == 2:
                        try:
                            parsed_date = datetime.strptime(clean_word, "%d.%m.%Y")
                            date_list.append(parsed_date)
                        except ValueError:
                            continue
                
                # Сбор сумм купонов по паттерну (XX.XX)
                matches = re.findall(coupon_pattern, item)
                if matches:
                    for val in matches:
                        try:
                            coupon_candidates.append(float(val))
                        except ValueError:
                            continue
                            
            elif isinstance(item, float):
                s = str(item)
                parts = s.split(".")
                if len(parts[0]) >= 4 and len(parts[1]) == 2:
                    total_sum = float(item)

    # Итоговый поиск максимума даты погашения
    if date_list:
        final_date = max(date_list)
        
    for date in date_list:
        if date != final_date:
            cupon_date_list.append(date)
            
    formatted_coupon_dates = [d.strftime("%d.%m.%Y") for d in cupon_date_list]
    
    # Выделяем самую частую сумму купона через моду
    target_coupon = 0.0
    if coupon_candidates:
        try:
            target_coupon = float(mode(coupon_candidates))
        except StatisticsError:
            target_coupon = float(coupon_candidates[0])

    # Формируем и возвращаем итоговый сырой словарь данных
    parsed_result = {
        "ovdp": ovdp,
        "ovdp_count": ovdp_count if ovdp_count is not None else 0.0,
        "total_sum": total_sum if total_sum is not None else 0.0,
        "maturity_date": final_date.strftime("%d.%m.%Y") if final_date else None,
        "coupon_dates": formatted_coupon_dates,
        "coupon_amount": target_coupon
    }
    
    return parsed_result
       
def main():
    true_way = take_data()         
    results = to_txt(true_way)     
    cleaned_data = normalization_of_results(results) 
    way_to_json = to_json(cleaned_data)
    clean_json_data = work_with_json(way_to_json)
    print("Результат парсинга:", clean_json_data)

if __name__=="__main__": 
    main()