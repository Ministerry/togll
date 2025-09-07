import os
import json
import pandas as pd
#打开json文件
with open("../dataset/dataset.json", 
          "r", encoding='utf-8') as file:
    data = json.loads(file.read())

df = pd.json_normalize(data)
#确定数据集数量和格式
train_data = []
test_data = []
answer_data = []
print("data的长度为：", len(data))
train_length = input("请输入数据集数量：")
for i in range(len(df)):
    line = df.loc[i]
    if i >= int(train_length):
        item = {
            "conversation": [
                {"role": "user", "content": "#focal_method\n{" + line['focal_method'] + "}\n#test_prefix\n{" + line['test_prefix'] + "}\n#assertORexception\n{" + line['assertORexception'] + "}\n#prefix\n{" + line['prefix'] + "}"}
            ]
        }
        answer_data.append(line['result'])
        test_data.append(item)
    else:
        item = {
            "conversation": [
                {"role": "user", "content": "#focal_method\n{" + line['focal_method'] + "}\n#test_prefix\n{" + line['test_prefix'] + "}\n#assertORexception\n{" + line['assertORexception'] + "}\n#prefix\n{" + line['prefix'] + "}"},
                {"role": "assistant", "content": line['result']}
            ]
        }
        train_data.append(item)

with open("../dataset/train.json", 'w', encoding='utf-8') as f:
    json.dump(train_data, f, ensure_ascii=False, indent=4)


with open("../dataset/test.json", 'w', encoding='utf-8') as f:
    json.dump(test_data, f, ensure_ascii=False, indent=4)
    
with open("../dataset/answer.json", 'w', encoding='utf-8') as f:
    json.dump(answer_data, f, ensure_ascii=False, indent=4)