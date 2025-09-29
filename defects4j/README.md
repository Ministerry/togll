**思路1** change_pom_way 通过修改pom.xml文件，使得可以运行mvn test进行测试
qs1:修改pom.xml文件，将1.3改为11，
qs2:使用正确的pom依赖
    1. 在pom中删去<parent>标签
    2. 
        <dependency>
        <groupId>org.evosuite</groupId>
        <artifactId>evosuite-standalone-runtime</artifactId>
        <version>1.1.0</version>
        <scope>test</scope>
        </dependency>
        <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
        </dependency>
    3. 在properties中添加
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    使用本地的evosuite.jar包
    mvn install:install-file -DgroupId=org.evosuite -DartifactId=evosuite-standalone-runtime -Dversion=1.0.6 -Dpackaging=jar -Dfile=/home/fdse/rmy/defects4j/evosuite-standalone-runtime-1.0.6.jar

# 整体操作：
1. 先依据get_projects.py和projects_bugs获取项目列表
2. cd项目列表，通过evosuite_geneate.py生成测试用例
3. 根据RQ5_data.json通过llama训练，得到generated_predictions.jsonl
4. 通过geneate_predictions.jsonl和RQ5_data.jsonl以及rq5_llama_assemble.py生成sft_qwen3_llama_result.json
5. 使用replace_test.py和sft_qwen3_llama_result.json将evosuite生成的测试用例替换为llama生成的测试用例
6. 对于不正确的test，使用remove_wrong_file.py删除
7. 找到没有pom文件的，加入正常的pom文件,使用search_pom.py文件
8. 对于有pom文件的，修改pom文件
9.  对每个文件夹，进行mvn clean compile 和 mvn test
10. 对结果进行对比


**思路2** change_build_way 通过修改build.xml和maven.xml文件，指定环境和依赖，直接运行。
qs1:如何将测试生成运行时库添加到编译测试代码的类路径中，确保编译器能够找到生成的测试用例可能依赖的类
# 整体操作：
1. 使用get_projects_b.py得到所有bug版本
2. 使用evosuite_generate.py脚本对每个用例生成evosuite测试用例
3. 使用add_path.py修改maven和build.xml文件
4. 使用add_sh.py对每个buggy文件生成run_test.sh文件
5. 使用replace_test.py将evosuite生成的测试用例替换为sft_qwen3_llama_result生成的code
6. 对code进行测试


# other:
设立环境变量
export PATH=$PATH:/home/fdse/rmy/defects4j/framework/bin
./init.sh
下载测试项目
defects4j checkout -p Lang -v 1b -w /tmp/lang_1_bugg
defects4j checkout -p Lang -v 1b -w /home/fdse/rmy/defects4j/Lang_Buggy
一些可能用到的命令：
    生成测试用例，这个什么目录都可以
    gen_tests.pl -g evosuite -p Gson -v 1b -n 1 -o /home/fdse/rmy/defects4j/Lang_Buggy -b 2
    然后解压缩
    bzip2 -d /home/fdse/rmy/defects4j/Lang_Buggy/Gson/evosuite/0/Gson-1b-evosuite.0.tar.bz2
    tar -xf /home/fdse/rmy/defects4j/Lang_Buggy/Gson/evosuite/0/Gson-1b-evosuite.0.tar.bz2.tar

    使用evosuite生成command的例子
    evo_cmd = [
        'java', '-jar', evosuite_jar,
        '-target', 'target/classes',
        '-class', buggy_class,
        '-Dtest_dir=src/test/java/evosuite',
        '-Dsearch_budget=1'
    ]
    java -jar /home/fdse/rmy/defects4j/framework/lib/test_generation/generation/evosuite-1.1.0.jar -target     target/classes -class org.apache.commons.cli.HelpFormatter -Dtest_dir=src/test/java/evosuite -Dsearch_budget=1