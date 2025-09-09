from collections import defaultdict
import json
import random
import pandas as pd
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from data_process.question_with_continuous_choices.option_range import OptionRange
from data_process.question_with_continuous_choices.gen_QA import *


def judge_continuous(row):
    if row['二三级要素类型'] not in {'select','multiselect'}:
        return False
    choices = row['二三级要素可选值']
    if pd.isna(choices):
        return False
    
    if (">" in choices or "大于" in choices or "以上" in choices) and ("<" in choices or "小于" in choices or "以下" in choices):
        return True
    if (">" in choices or "大于" in choices or "以上" in choices) and "-" in choices:
        return True
    if ("<" in choices or "小于" in choices or "以下" in choices) and "-" in choices:
        return True
    
    third_ability_tag = row['三级要素'] 
    if pd.isna(third_ability_tag):
        return False
    return any(keyword in third_ability_tag for keyword in ["级别", "等级", "规模", "数量", "占比", "程度", "量级", "频率"])

def trailing_zeros(n):
    count = 0
    while n % 10 == 0:
        count += 1
        n //= 10
    return count

def analyze_values_in_excel(path,output_path_continuous,output_path_incontinuous):
    # 读取Excel文件
    df = pd.read_excel(path, header=0)
    print("原始数据:")
    print(df)
    
    # 创建两个空的DataFrame用于存储分割后的数据
    df_continuous = pd.DataFrame(columns=df.columns)
    df_incontinuous = pd.DataFrame(columns=df.columns)
    
    # 遍历每一行进行判断
    for index, row in df.iterrows():
        is_continuous = judge_continuous(row)
        if is_continuous:
            df_continuous = pd.concat([df_continuous, row.to_frame().T], ignore_index=True)
        else:
            df_incontinuous = pd.concat([df_incontinuous, row.to_frame().T], ignore_index=True)
    
    df_continuous.to_csv(output_path_continuous, index=False)
    df_incontinuous.to_csv(output_path_incontinuous, index=False)
    
    print(f"\n分割完成:")
    print(f"连续值数据已保存到: {output_path_continuous}")
    print(f"非连续值数据已保存到: {output_path_incontinuous}")

def remove_redundancy_for_continuous_values(output_path_continuous, txt_output_path):
    # 读取连续值Excel文件
    df_continuous = pd.read_csv(output_path_continuous)

    df_continuous['二三级要素可选值'] = df_continuous['二三级要素可选值'].str.replace('；', ';', regex=False)    
    df_continuous['三级要素'] = df_continuous['三级要素'].str.replace('（', '(', regex=False).str.replace('）', ')', regex=False)    

    df_unique = df_continuous.drop_duplicates(subset=['三级要素', '二三级要素可选值'])
    
    # 提取去重后的结果，并去除空值
    unique_pairs = df_unique[['一级要素', '二级要素', '三级要素', '二三级要素可选值']].dropna()
    
    
    # 保存到txt文件
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        for _, row in unique_pairs.iterrows():
            f.write(f"{row['一级要素']}##{row['二级要素']}##{row['三级要素']}____{row['二三级要素可选值']}\n")
    
    print(f"\n去重完成:")
    print(f"唯一值已保存到: {txt_output_path}")
    print(f"共找到 {len(unique_pairs)} 个唯一值")

def construct_QAtemplate(txt_output_path,jsn_output_path,jsn_output_path_QA_tmp_map):
    lst2d_element_choices = []
    with open(txt_output_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            parts = line.split('____')
            if len(parts) == 2:
                lst2d_element_choices.append(parts)
    
    # 以可选值为key，不同的要素值装进一个键为“lst_element”的list
    dict_choices_element = defaultdict(lambda: {'QA': [], 'lst_element': []})
    dic_choices_empty  = {}
    for element, choices in lst2d_element_choices:
        dic_choices_empty[choices] = {"format": choices, "is_math": True, "has_percent": False, "factor": 1}
        dict_choices_element[choices]['lst_element'].append(element)
        print(element, choices)
    
    json_str = json.dumps(dict_choices_element, indent=2, ensure_ascii=False)
    with open(jsn_output_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    # dic_choices_empty 排序
    dic_choices_empty = dict(sorted(dic_choices_empty.items()))
    json_str = json.dumps(dic_choices_empty, indent=2, ensure_ascii=False)
    with open(jsn_output_path_QA_tmp_map, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    print(f"\n构造完成:")
    print(f"问题和答案已保存到: {jsn_output_path}")


def construct_QA_from_choices(jsn_output_path_QA_tmp, jsn_output_path_QA_tmp_map_modify, jsn_output_path_QA):
    with open(jsn_output_path_QA_tmp, 'r', encoding='utf-8') as f:
        dic_choices_element = json.load(f)
        
    map_tmp = json.load(open(jsn_output_path_QA_tmp_map_modify, 'r', encoding='utf-8'))
    for choices, dic_value in dic_choices_element.items():
        lst_element = dic_value['lst_element']
        lsr_QA = dic_value['QA']
        dic_map = map_tmp[choices]
        dic_value['dic_map'] = dic_map
        if dic_map['is_math']:
            if 'delete' in dic_map:
                continue
            str_format = dic_map['format'].replace("%", "")
            # if str_format=="0;1-3;3-5;>5":
            #     print()
            lst_option = [OptionRange(i) for i in str_format.split(";")]
            lst_QA_part = generate_QA_from_choices(lst_option,count=100) # 一般是单选
            lsr_QA.extend(lst_QA_part)
            lst_QA_part = generate_QA_from_choices_addinf(lst_option,count=100) # 一般是多选
            lsr_QA.extend(lst_QA_part)
            lst_QA_part = generate_QA_from_choices_addrandomrange(lst_option,count=100) # 一般是多选
            lsr_QA.extend(lst_QA_part)
            pass
        else:
            pass

    json_str = json.dumps(dic_choices_element, indent=2, ensure_ascii=False)
    with open(jsn_output_path_QA, 'w', encoding='utf-8') as f:
        f.write(json_str)
    print(f"\n构造完成:")
    print(f"问题和答案已保存到: {jsn_output_path_QA}")

if __name__ == '__main__':
    # 通过切分的形式 发现连续值
    path = "data_process/question_with_continuous_choices/品类要素信息.xlsx"
    output_path_continous = path.replace('.xlsx', '_连续.csv')
    output_path_incontinous = path.replace('.xlsx', '_非连续.csv')
    # 分析数据，得到连续值和非连续值
    analyze_values_in_excel(path,output_path_continous,output_path_incontinous) 

    # # 对连续值去重并保存到txt
    txt_output_path = path.replace('.xlsx', '_连续唯一值.txt')
    remove_redundancy_for_continuous_values(output_path_continous, txt_output_path)

    jsn_output_path_QA_tmp = path.replace('.xlsx', '_QA模板.json')
    jsn_output_path_QA_tmp_map = path.replace('.xlsx', '_QA模板映射待编辑.json')
    construct_QAtemplate(txt_output_path,jsn_output_path_QA_tmp,jsn_output_path_QA_tmp_map)
    
    jsn_output_path_QA = path.replace('.xlsx', '_问题和答案.json')
    jsn_output_path_QA_tmp_map_modify = path.replace('.xlsx', '_QA模板映射已编辑.json')
    construct_QA_from_choices(jsn_output_path_QA_tmp, # 未来向空list里添加数据
                  jsn_output_path_QA_tmp_map_modify, #借助映射表
                  jsn_output_path_QA # 保存的文件
                  )

