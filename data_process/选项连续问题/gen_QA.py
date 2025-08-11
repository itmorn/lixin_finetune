import random

def 用选项内的值构造QA(lst_option,count=100): # 一般是单选
    lst_QA = []
    for _ in range(count):
        option_choice = random.choice(lst_option)
        point_choice = option_choice.gen_point()
        # 判断这个点属于哪些选项
        lst_A = []
        for idx, option in enumerate(lst_option):
            if option.is_contain(point_choice):
                lst_A.append(idx)
        lst_QA.append({"type": "之内", "Q": point_choice, "A": lst_A})

    return lst_QA

def 用选项内的值加左右无穷构造QA(lst_option,count=100): # 一般是多选
    lst_QA = []
    for _ in range(count//2):
        option_choice = random.choice(lst_option)
        point_choice = option_choice.gen_point()
        # 判断这个点属于哪些选项
        lst_A = []
        for idx, option in enumerate(lst_option):
            if option.is_contain(point_choice):
                lst_A.append(idx)
            elif option.left > point_choice:
                lst_A.append(idx)
        lst_QA.append({"type": "大于", "Q": point_choice, "A": lst_A})

    for _ in range(count//2):
        option_choice = random.choice(lst_option)
        point_choice = option_choice.gen_point()
        # 判断这个点属于哪些选项
        lst_A = []
        for idx, option in enumerate(lst_option):
            if option.is_contain(point_choice):
                lst_A.append(idx)
            elif option.right < point_choice:
                lst_A.append(idx)
        lst_QA.append({"type": "小于", "Q": point_choice, "A": lst_A})

    return lst_QA
  

def 用选项内的值加随机区间构造QA(lst_option,count=100): # 一般是多选
    lst_QA = []
    while len(lst_QA) < count:
        point_choice1 = random.choice(lst_option).gen_point()
        point_choice2 = random.choice(lst_option).gen_point()
        if point_choice1==point_choice2:
            continue

        min_point, max_point = min(point_choice1, point_choice2), max(point_choice1, point_choice2)
        # 判断这个点属于哪些选项
        lst_A = []
        for idx, option in enumerate(lst_option):
            if option.right<min_point:
                continue
            if option.left>max_point:
                continue
            lst_A.append(idx)
        if min_point==9 > max_point:
            pass
        lst_QA.append({"type": "区间内", "Q": [min_point, max_point], "A": lst_A})

    return lst_QA