from collections import defaultdict
import json
import random
import pandas as pd
import sys
import os
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)
from data_process.选项连续问题.option_range import OptionRange
from data_process.选项连续问题.gen_QA import *


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


def 分析excel连续值(path,output_path_连续,output_path_非连续):
    # 读取Excel文件
    df = pd.read_excel(path, header=0)
    print("原始数据:")
    print(df)
    
    # 创建两个空的DataFrame用于存储分割后的数据
    df_连续 = pd.DataFrame(columns=df.columns)
    df_非连续 = pd.DataFrame(columns=df.columns)
    
    # 遍历每一行进行判断
    for index, row in df.iterrows():
        is_continuous = judge_continuous(row)
        if is_continuous:
            df_连续 = pd.concat([df_连续, row.to_frame().T], ignore_index=True)
        else:
            df_非连续 = pd.concat([df_非连续, row.to_frame().T], ignore_index=True)
    
    df_连续.to_excel(output_path_连续, index=False)
    df_非连续.to_excel(output_path_非连续, index=False)
    
    print(f"\n分割完成:")
    print(f"连续值数据已保存到: {output_path_连续}")
    print(f"非连续值数据已保存到: {output_path_非连续}")

def 对连续值去重(output_path_连续, txt_output_path):
    # 读取连续值Excel文件
    df_连续 = pd.read_excel(output_path_连续)

    df_连续['二三级要素可选值'] = df_连续['二三级要素可选值'].str.replace('；', ';', regex=False)    
    df_连续['三级要素'] = df_连续['三级要素'].str.replace('（', '(', regex=False).str.replace('）', ')', regex=False)    

    df_去重 = df_连续.drop_duplicates(subset=['三级要素', '二三级要素可选值'])
    
    # 提取去重后的结果，并去除空值
    unique_pairs = df_去重[['三级要素', '二三级要素可选值']].dropna()
    
    
    # 保存到txt文件
    with open(txt_output_path, 'w', encoding='utf-8') as f:
        for _, row in unique_pairs.iterrows():
            f.write(f"{row['三级要素']}____{row['二三级要素可选值']}\n")
    
    print(f"\n去重完成:")
    print(f"唯一值已保存到: {txt_output_path}")
    print(f"共找到 {len(unique_pairs)} 个唯一值")

def 根据选项构造QA模板(txt_output_path,jsn_output_path,jsn_output_path_QA_tmp_map):
    lst2d_要素_可选值 = []
    with open(txt_output_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            parts = line.split('____')
            if len(parts) == 2:
                lst2d_要素_可选值.append(parts)
    
    # 以可选值为key，不同的要素值装进一个键为“lst_要素”的list
    dict_可选值_要素 = defaultdict(lambda: {'QA': [], 'lst_要素': []})
    dic_可选值_空  = {}
    for 要素, 可选值 in lst2d_要素_可选值:
        dic_可选值_空[可选值] = {"format": 可选值, "is_math": True, "has_percent": False, "factor": 1}
        dict_可选值_要素[可选值]['lst_要素'].append(要素)
        print(要素, 可选值)
    
    json_str = json.dumps(dict_可选值_要素, indent=2, ensure_ascii=False)
    with open(jsn_output_path, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    # dic_可选值_空 排序
    dic_可选值_空 = dict(sorted(dic_可选值_空.items()))
    json_str = json.dumps(dic_可选值_空, indent=2, ensure_ascii=False)
    with open(jsn_output_path_QA_tmp_map, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    print(f"\n构造完成:")
    print(f"问题和答案已保存到: {jsn_output_path}")


def 根据选项构造多个问题和答案(jsn_output_path_QA_tmp, jsn_output_path_QA, jsn_output_path_QA_tmp_map_modify):
    with open(jsn_output_path_QA_tmp, 'r', encoding='utf-8') as f:
        dic_可选值_要素 = json.load(f)
    map_tmp = json.load(open(jsn_output_path_QA_tmp_map_modify, 'r', encoding='utf-8'))
    for 可选值, dic_value in dic_可选值_要素.items():
        lst_要素 = dic_value['lst_要素']
        lsr_QA = dic_value['QA']
        dic_map = map_tmp[可选值]
        if dic_map['is_math']:
            has_percent = "%" in 可选值
            factor = dic_map['factor']
            str_format = dic_map['format'].replace("%", "")
            # if str_format=="0;1-3;3-5;>5":
            #     print()
            lst_option = [OptionRange(i) for i in str_format.split(";")]
            lst_QA_part = 用选项内的值构造QA(lst_option,count=100) # 一般是单选
            lsr_QA.extend(lst_QA_part)
            lst_QA_part = 用选项内的值加左右无穷构造QA(lst_option,count=100) # 一般是多选
            lsr_QA.extend(lst_QA_part)
            lst_QA_part = 用选项内的值加随机区间构造QA(lst_option,count=100) # 一般是多选
            lsr_QA.extend(lst_QA_part)
            dic_value['has_percent'] = has_percent
            dic_value['factor'] = factor
            pass
        else:
            pass

    json_str = json.dumps(dic_可选值_要素, indent=2, ensure_ascii=False)
    with open(jsn_output_path_QA, 'w', encoding='utf-8') as f:
        f.write(json_str)
    print(f"\n构造完成:")
    print(f"问题和答案已保存到: {jsn_output_path_QA}")

if __name__ == '__main__':
    # 通过切分的形式 发现连续值
    path = "data_process/选项连续问题/品类要素信息.xlsx"
    output_path_连续 = path.replace('.xlsx', '_连续.xlsx')
    output_path_非连续 = path.replace('.xlsx', '_非连续.xlsx')
    # 分析excel连续值(path,output_path_连续,output_path_非连续)


    # 对连续值去重并保存到txt
    txt_output_path = path.replace('.xlsx', '_连续唯一值.txt')
    # 对连续值去重(output_path_连续, txt_output_path)

    jsn_output_path_QA_tmp = path.replace('.xlsx', '_QA模板.json')
    jsn_output_path_QA_tmp_map = path.replace('.xlsx', '_QA模板映射待编辑.json')  # 生成之后复制一份 改名为已编辑
    # 根据选项构造QA模板(txt_output_path,jsn_output_path_QA_tmp,jsn_output_path_QA_tmp_map)

    
    jsn_output_path_QA = path.replace('.xlsx', '_问题和答案.json')
    jsn_output_path_QA_tmp_map_modify = path.replace('.xlsx', '_QA模板映射已编辑.json')
    # 根据选项构造多个问题和答案(jsn_output_path_QA_tmp, # 空list
    #               jsn_output_path_QA, # 保存的文件
    #               jsn_output_path_QA_tmp_map_modify #借助映射表
    #               )

    
    pass