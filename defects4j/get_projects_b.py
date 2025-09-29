import json
import subprocess
import pandas as pd
import os

#得到所有缺陷文件
with open("projects_bugs.json", "r") as f:
    data = pd.json_normalize(json.loads(f.read()))

path_name = "projects_b_test"
for i in range(len(data)):
    print(data.loc[i]['project'].lower())
    project = data.loc[i]['project']
    project_name = data.loc[i]['project'].lower() 
    bug_num = data.loc[i]['bug_num']
    version = f"{bug_num}b"
    path = f"{path_name}/{project_name}_{bug_num}_buggy"
    cmd = [
        "defects4j" , "checkout"
        , "-p" , project
        , "-v" , version
        , "-w" , path
    ]
    subprocess.run(cmd)
