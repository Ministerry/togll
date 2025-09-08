import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset
#1. 加载模型和分词器
model_name = "Qwen/Qwen3-4B-Instruct-2507"
model_path = "/home/ubuntu/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Instruct-2507"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path,
        torch_dtype="auto",
        device_map="auto")
target_modules = ["q_proj", "v_proj", "k_proj", "o_proj","gate_proj","up_proj", "down_proj"]  
#配置lora参数
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=target_modules,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

#2.加载数据集,将其送入分词器
data_path ="../dataset/train.json"
with open(data_path, 'r', encoding='utf-8') as f:
    data = json.loads(f.read())
#分词器
dataset = []
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
#dataset = Dataset.from_list(data)
# print("dataset:",dataset)

#3.定义训练参数
training_args = TrainingArguments(
    #output_dir="../model/qwen3_4b_finetune",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    num_train_epochs=3,
    logging_steps=100,
    save_steps=2000,
    remove_unused_columns=False
)

#4.定义Trainer(训练器
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

#5.开始训练
trainer.train()

trainer.save_model("../model/qwen3_4b_finetune")
