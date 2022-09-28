import os

def createDir(path):
    os.makedirs(path,mode=0o777,exist_ok=True)
