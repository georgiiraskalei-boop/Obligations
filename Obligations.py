# TODO: Шаг 1. Импортировать нужные библиотеки (easyocr)
import easyocr
import json
from pathlib import Path
import numpy as np
import cv2

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
    print(results)
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
    print(f"Данные успешно упакованы в {file_path}")
    return(file_path)

def work_with_json(way_to_json):
    with open (way_to_json, "r", encoding="utf-8") as file_to_parsing:
        for line in file_to_parsing:
            if"UA" in line:
                print(line)

def main():
    true_way = take_data()         
    results = to_txt(true_way)     
    cleaned_data=normalization_of_results(results) 
    way_to_json=to_json(cleaned_data)
    cleanJson=work_with_json(way_to_json)
if __name__=="__main__": 
    main()    