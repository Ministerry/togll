import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset
#1. 加载模型和分词器
model_name = "Qwen/Qwen3-4B-Instruct-2507"
model_path = "/home/ubuntu/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Instruct-2507"
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_path,
        torch_dtype=torch.bfloat16,
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

def preprocess_with_masking(examples):
    # This assumes each 'conversation' is a list of dictionaries with 'role' and 'content' keys.
    all_input_ids = []
    all_labels = []

    for conversation in examples['conversation']:
        # The user's message is the first item
        user_message = conversation[0]
        # The assistant's response is the second item
        assistant_response = conversation[1]
        
        # Tokenize the user's prompt
        prompt_tokens = tokenizer.apply_chat_template(
            [user_message],
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt"
        )
        
        # Tokenize the assistant's response
        response_tokens = tokenizer.apply_chat_template(
            [assistant_response],
            tokenize=True,
            add_generation_prompt=False,
            return_tensors="pt"
        )

        # Concatenate the tokenized prompt and response
        input_ids = torch.cat([prompt_tokens, response_tokens], dim=-1).squeeze(0)
        
        # Create labels: a copy of input_ids
        labels = input_ids.clone()
        
        # Mask the loss for the user prompt.
        # We do this by setting the labels corresponding to the prompt tokens to -100.
        labels[:prompt_tokens.size(1)] = -100

        all_input_ids.append(input_ids)
        all_labels.append(labels)

    # Pad all sequences to the same length for batching
    padded_inputs = tokenizer.pad(
        {'input_ids': all_input_ids, 'labels': all_labels},
        padding=True,
        max_length=1024,
        return_tensors="pt"
    )
    
    return padded_inputs

# Apply the preprocessing function to the dataset
processed_dataset = dataset.map(
    preprocess_with_masking,
    batched=True,
    remove_columns=dataset.column_names,
    load_from_cache_file=False  # Set to False to re-run the mapping
)

#分词器
# def preprocess1(example):
#     tokens = tokenizer.apply_chat_template(
#         example["conversation"][0]["content"],  # 传入对话列表
#         tokenizer=True,
#         add_generation_prompt=True,
#         enable_thinking=False
#     )
#     return tokens
# def preprocess2(example):
#     tokens = tokenizer.apply_chat_template(
#         example["conversation"][1]["content"],  # 传入对话列表
#         tokenizer=True,
#         add_generation_prompt=True,
#         enable_thinking=False
#     )
#     return tokens


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
    save_steps=500,
    remove_unused_columns=False
)

#4.定义Trainer(训练器
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=processed_dataset
)

#5.开始训练
trainer.train()

trainer.save_model("../model/qwen3_4b_finetune")
