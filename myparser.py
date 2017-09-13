#-*- coding: utf-8 -*-
from html.parser import HTMLParser

class MyParser(HTMLParser): 
    idx = 0
    list = []
    
    def handle_data(self, data):
        # |(파이프라인)만 있는 경우는 무시한다.
        if data.strip() == '|' and len(data) == 1:
            pass
        # 공백이나 엔터문자가 포함된 |(파이프라인)은 파이프라인만 치환
        elif data.strip() == '|' and len(data) > 1:
            self.list.insert(self.idx, data.replace("|", ""))
            self.idx = self.idx + 1
        # 나머진 원데이터 그대로
        else:
            self.list.insert(self.idx, data)
            self.idx = self.idx + 1
        
    def clear(self):
        self.idx = 0
        self.list = []

    def getList(self):
        return self.list[:]