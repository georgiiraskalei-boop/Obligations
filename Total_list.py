from Obligations import parse_single_bond
from pathlib import Path
import json
class Total:
    def __init__(self):
        self.data=parse_single_bond()

    def total_cup(self):
        print (self.data)


def main():
    portfolio=Total()
    portfolio.total_cup()

    
if __name__=='__main__':
    main()    