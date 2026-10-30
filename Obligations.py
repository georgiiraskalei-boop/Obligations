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

def to_json(true_way):
    img = cv2.imdecode(np.fromfile(str(true_way), dtype=np.uint8), cv2.IMREAD_COLOR)
    results = reader.readtext(img, detail=0)
    
    with open("raw_text.json", "w", encoding="utf-8") as workfile:
        json.dump(results, workfile, ensure_ascii=False, indent=4)
        
    print(results)
    return results 

class work_with_json:
     def __init__(self, results):
          self.results=results
          self.data={}

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
                             print(self.data)
                             break
          return self.data                  
                    
def main():
    true_way=take_data()
    results=to_json(true_way)
    processor=work_with_json(results)
    processor.ovdp()
    processor.procent()
if __name__=='__main__':
     main()    
