import os
import sys
from ap2 import src_config
import gzip
import glob
import shutil
from file_parser_new import folder_select

LOGFILE_PATH = '/home/sahupr@ad.uc.edu/pubmed_docs/logs.txt'
FILE_PATH = '/home/sahupr@ad.uc.edu/pubmed_docs/'

args = sys.argv

if len(args) == 1:
    print('Choose either `baseline` or `daily`')
    exit(0)

elif args[1] == 'baseline':
    src_config('/pubmed/baseline/', args)
    # unzip .gz files
    search_path = os.getcwd()
    file_type = ".gz"
    for fname in os.listdir(path=search_path):
        if fname.endswith(file_type):
            with gzip.open(fname,'rb') as f_in:
                with open(fname[0:-7]+'.xml','wb') as f_out:
                    shutil.copyfileobj(f_in,f_out)
                    os.remove(fname)
    folder_select(args[1])

elif args[1] == 'daily':        
    src_config('/pubmed/updatefiles/', args)
    # unzip .gz files
    search_path = os.getcwd()
    file_type = ".gz"
    for fname in os.listdir(path=FILE_PATH+'pubmed/updatefiles/'):
        print(fname)
        if fname.endswith(file_type):
            with gzip.open(fname,'rb') as f_in:
                with open(fname[0:-7]+'.xml','wb') as f_out:
                    shutil.copyfileobj(f_in,f_out)
                    os.remove(fname)
        else:
            continue
    folder_select(args[1])