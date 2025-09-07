from datasets import Dataset
from transformers import AutoTokenizer
import json
model_path = "/home/ubuntu/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Instruct-2507"
tokenizer = AutoTokenizer.from_pretrained(model_path)
data_path ="../dataset/train.json"
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
dataset = []
#分词器
def preprocess1(example):
    tokens = tokenizer.apply_chat_template(
        example["conversation"][0]["content"],  # 传入对话列表
        tokenizer=True,
        add_generation_prompt=True,
        enable_thinking=False
    )
    return tokens
def preprocess2(example):
    tokens = tokenizer.apply_chat_template(
        example["conversation"][1]["content"],  # 传入对话列表
        tokenizer=True,
        add_generation_prompt=True,
        enable_thinking=False
    )
    return tokens
for i in range(len(data)):
    dataset.append({"input_ids" : preprocess1(data[i]),"labels": preprocess2(data[i])})
#dataset = Dataset.from_list(dataset)
print("dataset:",dataset)
decoded_text = tokenizer.decode(
    dataset[0]["labels"], 
    skip_special_tokens=True,
    clean_up_tokenization_spaces=True
)
print("decoded_text:",decoded_text)