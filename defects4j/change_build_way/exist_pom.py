import os
import json
import subprocess
import time
import pandas as pd
import shutil

#查询是否存在pom.xml文件

def list_directories(path):
    # 获取path下的所有文件和目录
    entries = os.listdir(path)
    # 过滤出目录
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return directories
 
# 示例使用
path = '/home/fdse/rmy/defects4j/projects_b_1'
directories = list_directories(path)


print("修改pom文件的内容：")
without_pom = []
for i in range(len(directories)):
    file_path = os.path.join(path,directories[i],'pom.xml')
    if os.path.exists(file_path):
        continue
    else:
        without_pom.append(os.path.join(path,directories[i]))

print(without_pom)

qwen_train_data = '/home/fdse/rmy/defects4j/projects_b_test/sft_qwen3_remove_error.json'

with open(qwen_train_data,'r',encoding='utf-8') as f:
    data = pd.json_normalize(json.loads(f.read()))

Dtest = ''
for i in range(len(directories)):
    file_path = os.path.join(path,directories[i])
    if directories[i].split('_')[0] == 'cli':
        os.chdir(file_path)
        for j in range(len(data)):
            if directories[i].split('_')[0] == data.loc[j]['project'].lower() and  directories[i].split('_')[1] == data.loc[j]['bug_num']:
                Dtest = data.loc[j]['Dtest']
                break
        ret = subprocess.run(['mvn', 'test',f"-Dtest={Dtest}"], capture_output=True, text=True)
        if 'Results :' not in ret.stdout : 
            print(file_path)
        
