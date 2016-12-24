'''
Created on 16.11.2016

@author: Timo Nallikari
'''

from Gramps.jsonutils import write_json_sources

if __name__ == '__main__':
    write_json_sources.main(["write_json_sources", "C:/Temp/", "Sources.csv", "Result.json", "Result.csv", 1000, 10])