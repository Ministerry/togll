import os

# 要遍历的顶层目录
base_dir = 'projects_b_test_1'  # 替换为你的路径
sh_filename = 'run_test.sh'

# 目标 shell 脚本内容
sh_content = '''#!/bin/bash
# —— 1. 基本环境变量 —— 
export D4J_HOME=/home/fdse/rmy/defects4j
export JAVA_HOME=/home/fdse/anaconda3/envs/rmy_llama/lib/jvm

# —— 2. Defects4J 工具加入 PATH —— 
export PATH=$D4J_HOME/framework/bin:$JAVA_HOME/bin:$PATH

# —— 3. 各类 Jar 路径 —— 
EVOSUITE_JAR=$D4J_HOME/framework/lib/evosuite-standalone-runtime-1.1.0.jar
JUNIT4_JAR=$D4J_HOME/framework/projects/Cli/lib/junit/junit/4.11/junit-4.11.jar
HAMCREST_JAR=$D4J_HOME/framework/lib/hamcrest-core-1.3.jar
JACKSON_CORE_JAR=$D4J_HOME/framework/lib/jackson-core-2.9.10.jar
JACKSON_ANN_JAR=$D4J_HOME/framework/lib/jackson-annotations-2.9.10.jar
JDOM_JAR=$D4J_HOME/framework/lib/jdom-1.1.3.jar

# —— 4. 导出 Defects4J 自带的类路径 —— 
CP_DEFECTS4J=$(defects4j export -p cp.test)

# —— 5. 重新组装 classpath —— 
#     把 JUnit/Hamcrest/EvoSuite 放在最前面，确保加载到新版本 TestRule 实现
CP="$JUNIT4_JAR:$HAMCREST_JAR:$EVOSUITE_JAR:$JACKSON_CORE_JAR:$JACKSON_ANN_JAR:$JDOM_JAR:$CP_DEFECTS4J"

echo "Using classpath:"
echo "  $CP"

# —— 6. 编译 & 运行 —— 
defects4j compile
# "$@" 中传入要跑的 Test 类全名，如：org.apache.commons.cli.PosixParser_ESTest
java -ea -cp "$CP" org.junit.runner.JUnitCore "$@"
'''

for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        sh_path = os.path.join(folder_path, sh_filename)
        if  os.path.exists(sh_path):
            with open(sh_path, 'w') as f:
                f.write(sh_content)
            os.chmod(sh_path, 0o755)  # 设置可执行权限
            print(f"✅ Created {sh_filename} in: {folder_path}")
        else:
            print(f"✔️ Exists: {sh_path}")
