import torch
import re
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
#加载基座模型
model_name = "Qwen/Qwen3-4B-Instruct-2507"
model_path = "/home/ubuntu/.cache/modelscope/hub/models/Qwen/Qwen3-4B-Instruct-2507"
finetuned_model_path = "/home/ubuntu/myren/py_work/trainer_output/checkpoint-6000"
tokenizer = AutoTokenizer.from_pretrained(model_path)
base_model = AutoModelForCausalLM.from_pretrained(model_path)
model = PeftModel.from_pretrained(base_model, finetuned_model_path)
model.eval()
#加载测试数据
print("模型加载完成!")

test_path ="../dataset/test.json"
with open(test_path, 'r', encoding='utf-8') as f:
    test_data = json.loads(f.read())
wrong = 0
evaluate = []
#将文本编码为模型输入
for i in range(len(test_data)):
    inputs = tokenizer(test_data[i]["conversation"][0]["content"], return_tensors="pt", padding=True)
    input_len = inputs["input_ids"].shape[1]
    #推送至Gpu
    if torch.cuda.is_available():
        model = model.to("cuda")
        inputs = {k: v.to("cuda") for k, v in inputs.items()}
    #生成文本
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id
        )
    #解码生成的文本
    generated_texts = tokenizer.batch_decode(outputs[0], skip_special_tokens=True)
    #打印结果
    predict = "".join(generated_texts[input_len:]).strip()
    text = re.search(r'\{(.+?)\}', predict)
    if(text.group(1) != test_data[i]["conversation"][1]["content"]) :
        wrong = wrong + 1
    evaluate.append({"predict":text.group(1),"answer:":test_data[i]["conversation"][1]["content"]})
    print(f"predict[{i}]:{text.group(1)}")
    print(f"answer[{i}]:",test_data[i]["conversation"][1]["content"])



print("模型错误率为：",wrong / len(test_data))
print("正确率为:",1 - wrong / len(test_data))


with open("../dataset/evaluate.json","w",encoding="utf-8") as f :
    json.dump(evaluate, f, ensure_ascii=False, indent=4)