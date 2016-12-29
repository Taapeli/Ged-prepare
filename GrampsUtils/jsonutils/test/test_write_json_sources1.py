'''
Created on 16.11.2016

@author: Timo Nallikari

1. test phase: from Sources.csv build Results.json (Gramps format, inserts) and Results.csv (Sources.csv with ids and handles)
'''

from jsonutils import write_json_sources

if __name__ == '__main__':
    write_json_sources.main(['write_json_sources', 'C:/Temp/', 'Sources.csv', 'Result.json', 'Result.csv', '1000', '10', 'r'])