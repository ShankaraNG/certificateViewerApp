# '{date} INFO [Certificate Viewer Tool] Fetched all the data for the certificates'.format(date=datetime.now().strftime('%d %B %Y %H:%M:%S,%f')[:-3])
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import configloader as cnfloader


def logger(information, type, exceptioncode, data):
    log = '{date} {information} [{type}] {exceptioncode} {data}'.format(date=datetime.now().strftime('%d %B %Y %H:%M:%S,%f')[:-3],information = information, type= type, exceptioncode = exceptioncode, data = data)
    config = cnfloader.load_properties()
    logfile = config.get('loggingFilePath')
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(log + '\n')

def startinglogger(data):
    config = cnfloader.load_properties()
    logfile = config.get('loggingFilePath')
    with open(logfile, 'a', encoding='utf-8') as f:
        f.write(data + '\n')

