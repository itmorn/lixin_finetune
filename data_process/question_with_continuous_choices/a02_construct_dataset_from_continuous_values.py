import json
import random
map_char = {0:"A", 1:"B", 2:"C", 3:"D", 4:"E", 5:"F", 6:"G", 7:"H", 8:"I", 9:"J", 10:"K", 11:"L", 12:"M", 13:"N", 14:"O", 15:"P", 16:"Q", 17:"R", 18:"S", 19:"T", 20:"U", 21:"V", 22:"W", 23:"X", 24:"Y", 25:"Z"}
map_num = {"A":0, "B":1, "C":2, "D":3, "E":4, "F":5, "G":6, "H":7, "I":8, "J":9, "K":10, "L":11, "M":12, "N":13, "O":14, "P":15, "Q":16, "R":17, "S":18, "T":19, "U":20, "V":21, "W":22, "X":23, "Y":24, "Z":25}
def build_prompt(jsn_input_path_QA, jsn_output, count = 10000):
    with open(jsn_input_path_QA, 'r', encoding='utf-8') as f:
        dic_choices_element = json.load(f)
    lst2d_msg = []
    lst_choices_element = list(dic_choices_element.items())
    while len(lst2d_msg) < count:
        # 从dic_可选值_element中随机选取一个可选值和dic_value
        choice, dic_value = random.choice(lst_choices_element)
        if "%" in choice:
            pass
        lst_element = dic_value['lst_element']
        lsr_QA = dic_value['QA']
        if not lsr_QA:
            continue
        dic_map = dic_value['dic_map']
        str_format = dic_map['format']
        factor = dic_map['factor']
        has_percent = dic_map['has_percent']
        if 'delete' in dic_map:
            continue
        element = random.choice(lst_element)
        QA = random.choice(lsr_QA)
        lst_option = choice.split(";")
        lst_msg = []
        if QA['type']=='之内':
            content = f"帮我找到业务相关的供应商。要求{element.split('##')[-1]}的数量为{QA['Q']*factor}{'%' if has_percent else ''}。"
        elif QA['type']=='大于':
            content = f"帮我找到业务相关的供应商。要求{element.split('##')[-1]}的数量大于{QA['Q']*factor}{'%' if has_percent else ''}。"
        elif QA['type']=='小于':
            content = f"帮我找到业务相关的供应商。要求{element.split('##')[-1]}的数量小于{QA['Q']*factor}{'%' if has_percent else ''}。"
        elif QA['type']=='区间内':
            a = f"{QA['Q'][0]*factor}{'%' if has_percent else ''}"
            b = f"{QA['Q'][1]*factor}{'%' if has_percent else ''}"
            content = f"帮我找到业务相关的供应商。要求{element.split('##')[-1]}的数量在{a}和{b}的范围内。"
        else:
            raise ValueError
        str_options = "\n".join([f"{map_char[idx]}. {i}" for idx,i in enumerate(lst_option)])
        content += f"\n不要直接回复用户query\n请结合下面的筛选条件和对应的选项：\n{element}\n{str_options}\n只要和用户指定的范围有交集的选项都要输出，不要遗漏选项，输出格式为选项字母，多选用英文逗号隔开"
        lst_msg.append({"content": content, "role": "user"})
        # msg.append({"content": f"不要直接回复用户query\n请结合下面的筛选条件和对应的选项：\n{element}\n{str_options}\n只要和用户指定的范围有交集的选项都要输出，不要遗漏选项，输出格式为选项字母，多选用英文逗号隔开", "role": "system"})
        str_answer = ",".join([map_char[i] for i in QA['A']])
        lst_msg.append({"content": str_answer, "role": "assistant"})
        lst2d_msg.append({"messages":lst_msg})
    
    with open(jsn_output, 'w', encoding='utf-8') as f:
        json.dump(lst2d_msg, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    path = "data_process/question_with_continuous_choices/品类要素信息.xlsx"
    
    jsn_input_path_QA = path.replace('.xlsx', '_问题和答案.json')
    jsn_output = path.replace('.xlsx', '_连续值微调数据集.json')
    build_prompt(jsn_input_path_QA, jsn_output, count = 10000)

    
    pass