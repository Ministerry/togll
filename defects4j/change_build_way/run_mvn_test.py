import os
import json
import subprocess
import xml.etree.ElementTree as ET

def list_directories(path):
    # 获取path下的所有文件和目录
    entries = os.listdir(path)
    # 过滤出目录
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return directories
 
# 示例使用
cwd = os.getcwd()
directories = list_directories(cwd)

for i in range(len(directories)):
    file_path = os.path.join(cwd,directories[i])
    if directories[i].split('_')[0] == 'cli':
        os.chdir(file_path)
        ret = subprocess.run(['mvn', 'test'], capture_output=True, text=True)
        if "BUILD FAILURE" in ret.stdout :
            print(file_path)