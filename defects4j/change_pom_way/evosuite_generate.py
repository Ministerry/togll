import os
import json
import subprocess
import time
import pandas as pd
import shutil

# —— 一次性设置的环境变量 —— #
os.environ['D4J_HOME'] = '/home/fdse/rmy/defects4j'
os.environ['PATH'] = os.environ['D4J_HOME'] + '/framework/bin:' + os.environ.get('PATH', '')
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-11-openjdk-amd64'
os.environ['PATH'] = os.environ['JAVA_HOME'] + '/bin:' + os.environ['PATH']

# 输入和输出 JSON 文件路径
json_path = '/home/fdse/rmy/defects4j/sft_qwen3_llama_result.json'      # 你的输入
error_json = 'error_list.json'    # 错误记录会写到这里

# EvoSuite Jar 路径
evosuite_jar = os.path.join(
    os.environ['D4J_HOME'],
    'framework/lib/test_generation/generation/evosuite-1.1.0.jar'
)

# 读取全部记录
with open(json_path, 'r', encoding='utf-8') as f:
    records = json.load(f)

seen = set()
errors = []

for rec in records:
    project  = rec['project']
    bug_num  = rec['bug_num']
    test_name = rec['test_name']
    buggy_class = test_name.split("::")[0][:-7]
    # buggy_class = rec['class']
    key = (project, bug_num, buggy_class)
    if key in seen:
        continue
    seen.add(key)

    # 目录名首字母小写
    dir_name = f"{project.lower()}_{bug_num}_buggy"
    # dir_name = raw_name[0].lower() + raw_name[1:]

    print(f"\n=== Processing {dir_name}, class {buggy_class} ===")

    cwd = os.getcwd()
    project_path = os.path.join(cwd, dir_name)
    if not os.path.isdir(project_path):
        print(f"[WARN] 目录不存在，跳过: {project_path}")
        errors.append({'project': project, 'bug_num': bug_num, 'class': buggy_class,'reason': '目录不存在'})
        continue
    os.chdir(project_path)

    # —— 1) defects4j compile —— #
    ret = subprocess.run(['defects4j', 'compile'], capture_output=True, text=True)
    if ret.returncode != 0:
        print(f"[ERROR] defects4j compile 失败:\n{ret.stderr}")
        errors.append({'project': project, 'bug_num': bug_num, 'class': buggy_class,'reason': 'defects4j compile'})
        os.chdir(cwd)
        continue

    # —— 2) EvoSuite —— #
    evo_cmd = [
        'java', '-jar', evosuite_jar,
        '-target', 'target/classes',
        '-class', buggy_class,
        '-Dtest_dir=src/test/java/evosuite',
        '-Dsearch_budget=1'
    ]
    try:
        proc = subprocess.Popen(
            evo_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        start = time.time()
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            print(line, end='')
            if time.time() - start > 1000:
                proc.kill()
                print("[WARN] EvoSuite 超时（90s），已终止")
                break
        retcode = proc.wait()
        if retcode not in (0, -9):
            print(f"[ERROR] EvoSuite 返回码：{retcode}")
            errors.append({'project': project, 'bug_num': bug_num, 'class': buggy_class,'reason':'timeout'})
    except Exception as e:
        print(f"[ERROR] EvoSuite 异常：{e}")
        errors.append({'project': project, 'bug_num': bug_num, 'class': buggy_class,'reason':'exception'})

    # 切回原目录
    os.chdir(cwd)


# —— 把错误记录写入 JSON —— #
with open(error_json, 'w', encoding='utf-8') as f:
    json.dump(errors, f, indent=2, ensure_ascii=False)

print(f"\n共记录 {len(errors)} 条出错：已写入 {error_json}")
