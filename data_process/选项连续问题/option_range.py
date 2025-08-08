import random

class OptionRange:
    def __init__(self, str_option):
        self.str_option = str_option.strip()
        self.left = None
        self.right = None
        self.init_border()

    def init_border(self):
        if self.str_option=="<0":
            self.left = -100
            self.right = -1
        elif "<" in self.str_option:
            value = int(self.str_option.split("<")[1])
            self.left = 0
            self.right = value-1
        elif ">" in self.str_option:
            value = int(self.str_option.split(">")[1])
            self.left = value+1
            self.right = self.left*2
        elif "-" in self.str_option:
            self.left, self.right = [int(i) for i in self.str_option.split("-")]
        else:
            self.left = self.right = int(self.str_option)

    def is_contain(self, value):
        return self.left <= value <= self.right

    def gen_point(self):
        return random.randint(self.left, self.right)