import os
import json
import subprocess
import time
import pandas as pd
import shutil

#修改pom文件，使其可以运行

def list_directories(path):
    # 获取path下的所有文件和目录
    entries = os.listdir(path)
    # 过滤出目录
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]
    return directories
 
# 示例使用
path = '/home/fdse/rmy/defects4j/projects_b_test'
directories = list_directories(path)


print("修改pom文件的内容：")
for i in range(len(directories)):
    file_path = os.path.join(path,directories[i],'pom.xml')
    file_test_path = os.path.join(path,directories[i],'test.xml')
    print(f"当前修改==============================={file_path}==========================================")
    lines = []
    with open(file_path,"r",encoding="utf-8") as f:
        line = f.readline()
        while line:
            # if line.strip() == "<parent>":
            #     for j in range(5):
            #         line = f.readline()
            #     continue
            if line.strip() == "<groupId>junit</groupId>" :
                lines.append(line)
                for j in range(4):
                    line = f.readline()
                lines.append("""        <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency> 
    <dependency>
        <groupId>org.evosuite</groupId>
        <artifactId>evosuite-standalone-runtime</artifactId>
        <version>1.1.0</version>
        <scope>test</scope>
    </dependency>
""")
                line = f.readline()
            elif line.strip() == "<properties>" :
                lines.append(line)
                lines.append("""    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
""")            
                line = f.readline()
            else :
                lines.append(line)
                line = f.readline()
    with open(file_path,'w',encoding='utf-8') as f :
        for i in range(len(lines)):
            f.write(lines[i])