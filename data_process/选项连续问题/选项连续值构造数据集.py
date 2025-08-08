import json
import random

def 构造提示词(jsn_input_path_QA, jsn_output):
    with open(jsn_input_path_QA, 'r', encoding='utf-8') as f:
        dic_可选值_要素 = json.load(f)

    for 可选值, dic_value in dic_可选值_要素.items():
        lst_要素 = dic_value['lst_要素']
        lsr_QA = dic_value['QA']
        dic_map = dic_value['dic_map']
        str_format = dic_map['format']
        if 'delete' in dic_map:
            continue
        要素 = random.choice(lst_要素)
        QA = random.choice(lsr_QA)
        
        pass
    
    with open(jsn_output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    path = "data_process/选项连续问题/品类要素信息.xlsx"
    
    jsn_input_path_QA = path.replace('.xlsx', '_问题和答案.json')
    jsn_output = path.replace('.xlsx', '_连续数据集.json')
    构造提示词(jsn_input_path_QA, jsn_output)

    
    pass