import os
import json
import subprocess
import time
import pandas as pd
import shutil

#删除错误文件

with open('error_path.json', 'r',encoding='utf-8') as f:
    data = json.loads(f.read())

directory = '/home/fdse/rmy/defects4j/projects_b_1'

print(data)

for i in range(len(data)):
    file_path = os.path.join(directory,data[i])
    if os.path.exists(file_path):
        print("文件存在,清除")
        shutil.rmtree(file_path)
    else:
        print("文件不存在")

