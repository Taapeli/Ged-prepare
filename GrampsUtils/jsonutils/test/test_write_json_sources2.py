'''
Created on 16.11.2016

@author: Timo Nallikari

2. test phase: from Results.csv from phase 1 build Result2.json (Gramps format, updates) and Result2.csv (identical with Results.csv
'''

from jsonutils import write_json_sources


if __name__ == '__main__':
    write_json_sources.main(["write_json_sources", "C:/Temp/", "Result.csv", "Result2.json", "Result2.csv", 1000, 10]) 