import os
import json
import subprocess
import time
import pandas as pd
import shutil

#将evosuite生成的例子换成qwen3生成的

error_path = 'error_path.json'
error = set()
def replace_from_first_brace(file_path, new_code,file_name):
    """
    定位 Java 文件中第一个 { ，删除其后所有内容并插入 new_code，然后加一个 }。
    """
    if not os.path.exists(file_path):
        print(f"[!] 文件不存在: {file_path}")
        error.add(file_name)
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    brace_pos = content.find('{')
    if brace_pos == -1:
        print(f"[!] 找不到 '{{' ：{file_path}")
        return
    
    # 保留前面内容 + 新代码 + }
    new_content = content[:brace_pos + 1] + '\n' + new_code.strip() + '\n}'

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

json_path = "../sft_qwen3_llama_result.json"  # 你自己的 JSON 文件路径

with open(json_path, 'r', encoding='utf-8') as f:
    items = json.load(f)

for item in items:
    project = item['project'].lower()
    bug_num = item['bug_num']
    test_name = item['test_name']
    # code = item['code']
    code=item['code']
    class_path = test_name.split("::")[0]
    class_file = class_path.split(".")[-1] + ".java"
    parts = class_path.split(".")
    sub_dir = os.path.join(*parts[:-1])
    file_path = os.path.join(f"{project}_{bug_num}_buggy", "src", "test", "java","evosuite", sub_dir, class_file)
    file_name = f"{project}_{bug_num}_buggy"
    replace_from_first_brace(file_path, code,file_name)

with open(error_path, 'w', encoding='utf-8') as f:
    json.dump(list(error),f, ensure_ascii=False, indent=4)