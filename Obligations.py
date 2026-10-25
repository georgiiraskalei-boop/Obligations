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
def to_txt(true_way):
    img = cv2.imdecode(np.fromfile(str(true_way), dtype=np.uint8), cv2.IMREAD_COLOR)
    results = reader.readtext(img, detail=0)
    with open("raw_text.txt", "w", encoding="utf-8") as workfile:
        for line in results:
            workfile.write(line + "\n")
    print(results)
    return(results)                   
                    



# TODO: Шаг 3. Написать блок выгрузки сырого текста:
# открыть картинку, прогнать через OCR без фильтрации 
# и записать результат построчно в промежуточный .txt файл


# TODO: Шаг 4. Написать функцию нормализации значений:
# принимать строку, проверять наличие точки, 
# если копеек нет — добивать '.00', возвращать нормализованное значение


# TODO: Шаг 5. Написать логику построчного парсинга:
# открыть созданный .txt файл, запустить цикл по строкам, 
# применять функцию нормализации и отбирать нужные данные


# TODO: Шаг 6. Упаковать очищенные и структурированные данные в JSON-файл
def main():
    true_way=take_data()
    to_txt(true_way)
if __name__=="__main__": 
    main()    