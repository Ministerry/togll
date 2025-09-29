import os
import json
import subprocess
import time
import pandas as pd
import shutil

#将不存在的文件从sft_qwen3_llama_result去除

def list_directories(path):
    # 获取path下的所有文件和目录
    entries = os.listdir(path)
    # 过滤出目录
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return directories
 
# 示例使用
cwd = os.getcwd()
directories = list_directories(cwd)
qwen_train_data = '/home/fdse/rmy/defects4j/sft_qwen3_llama_result.json'

print(directories)

with open(qwen_train_data,'r',encoding='utf-8') as f :
    sft_data = pd. json_normalize(json.loads(f.read()))
print(len(sft_data))
data = []
visit = []
for i in range(len(directories)): # cli_25
    # for j in range(len(sft_data)): # cli_32 cli_25
    #     if sft_data.loc[j]['project'].lower() == directories[i].split('_')[0]:
    for k in range(len(sft_data)):
        if sft_data.loc[k]['bug_num'] == directories[i].split('_')[1] and sft_data.loc[k]['project'].lower() == directories[i].split('_')[0] :
            class_path = sft_data.loc[k]['test_name'].split("::")[0]
            class_file = class_path.split(".")[-1]
            data.append(sft_data.loc[k]._append(pd.Series(
        {"Dtest" : class_file
         })).to_dict())

with open('sft_qwen3_remove_error.json','w',encoding='utf-8') as f:
     json.dump(data, f, ensure_ascii=False,indent=4)