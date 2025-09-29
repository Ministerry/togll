import os
import json
import pandas as pd

#将llama生成的预测和测试集进行拼接

with open('RQ5_data.json', 'r',encoding="utf-8") as file:
    rq5_data = pd.json_normalize(json.loads(file.read()))

with open('/home/fdse/rmy/defects4j/projects_b_test/generated_predictions.jsonl', 'r',encoding="utf-8") as file:
    llama_gen_data = pd.read_json(file, lines=True)

data = []
result_path = '/home/fdse/rmy/defects4j/sft_qwen3_llama_result.json'
for i in range(len(llama_gen_data)):
    code = ""
    if llama_gen_data.loc[i]["predict"] == "exception":
        code = f"@Test(timeout = 4000)\npublic void test{rq5_data.loc[i]['id']}()  throws Throwable  " + "{\n" + "\ntry{\n" + rq5_data.loc[i]["prefix"] + "\nfail();\n} catch (Exception e) {\n\n}\n}"
    else :
        code = f"@Test(timeout = 4000)\npublic void test{rq5_data.loc[i]['id']}()  throws Throwable  " + "{\n" + rq5_data.loc[i]["prefix"] + "\n" + llama_gen_data.loc[i]["predict"] + "\n}"

    data.append(rq5_data.loc[i]._append(pd.Series(
        {"predict" : llama_gen_data.loc[i]["predict"],
         "code" : code
         })).to_dict())
with open(result_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False,indent=4)
