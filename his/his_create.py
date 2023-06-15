import json


class BizException(Exception):
    pass


def assert_key_not_repeat(his_model):
    list1 = []
    with open(his_model, encoding='utf-8') as f:
        my_dict = json.load(f)
        for key in my_dict.keys():
            if key != 'config':
                value = my_dict[key]
                if isinstance(value, list):
                    my_dict2 = value[0]
                    for key2 in my_dict2.keys():
                        if key2 not in list1:
                            list1.append(key2)
                        else:
                            raise BizException(f'重复的key {key2}')
                elif isinstance(value, dict):
                    for key2 in value.keys():
                        if key2 not in list1:
                            list1.append(key2)
                        else:
                            raise BizException(f'重复的key {key2}')
    return my_dict


def create_pipe_txt(pipe):
    txt = ''
    for i in range(pipe):
        txt = txt + '|'
    return txt


def create_origin_his_txt():
    txt = 'MSH' + create_pipe_txt(pipe_length) + '\n'
    txt = txt + 'PID' + create_pipe_txt(pipe_length) + '\n'
    txt = txt + 'PV1' + create_pipe_txt(pipe_length) + '\n'
    txt = txt + 'OBR' + create_pipe_txt(pipe_length) + '\n'
    return txt


# 将值value插入到txt的value_loc位置
def insert_value(txt, value_loc, value):
    if txt:
        split = txt.split('|')
        # 单个值的插入方法
        if '.' not in value_loc:
            loc = int(value_loc)
            txt2 = ''
            for i in range(len(split)):
                value_i = split[i]
                # 如果该位置已经有值了，那么是不能插入的
                if i == loc and not value_i and value:
                    txt2 = txt2 + value
                else:
                    txt2 = txt2 + value_i
                if i < len(split) - 1:
                    txt2 = txt2 + '|'
            return txt2
        else:
            loc_split = value_loc.split('.')
            loc = int(loc_split[0])
            txt2 = ''
            for i in range(len(split)):
                value_i = split[i]
                value2 = ''
                if i == loc and value:
                    loc2 = int(loc_split[1])
                    value_i_split = value_i.split('^')
                    field_length = len(value_i_split)
                    max_length = field_length
                    if loc2 > field_length-1:
                        max_length = loc2 + 1
                    for i2 in range(max_length):
                        if i2 == loc2:
                            value2 = value2 + value
                        else:
                            if i2 < field_length:
                                value2 = value2 + value_i_split[i2]
                        if i2 < max_length - 1:
                            value2 = value2 + '^'
                    txt2 = txt2 + value2
                else:
                    txt2 = txt2 + value_i
                if i < len(split) - 1:
                    txt2 = txt2 + '|'
            return txt2
    return txt


def get_txt_from_his_txt(his_txt, key):
    split = his_txt.split('\n')
    for i in range(len(split)):
        txt = split[i]
        if txt.startswith(key):
            return txt + '\n'


def replace_his_txt(key, his_txt, txt):
    split = his_txt.split('\n')
    his_txt2 = ''
    for i in range(len(split)):
        txt1 = split[i]
        if txt1.startswith(key):
            his_txt2 = his_txt2 + txt
        else:
            his_txt2 = his_txt2 + txt1 + '\n'
    return his_txt2


# 将json转换为his文本
def create_his_txt(model, his_json_file):
    with open(his_json_file, encoding='utf-8') as f:
        his_json = json.load(f)
        his_txt = create_origin_his_txt()
        for key in his_json.keys():
            if key == 'config':
                continue
            if key == 'OBX':
                obxs = his_json[key]
                for obx in obxs:
                    txt = key + create_pipe_txt(pipe_length) + '\n'
                    model_item = model[key][0]
                    for model_item_key in model_item.keys():
                        value = obx[model_item_key]
                        value_loc = model_item[model_item_key]
                        txt = insert_value(txt, value_loc, value)
                    his_txt = his_txt + txt
            else:
                his_json_item = his_json[key]
                txt = get_txt_from_his_txt(his_txt, key)
                model_item = model[key]
                for model_item_key in model_item.keys():
                    value = his_json_item[model_item_key]
                    value_loc = model_item[model_item_key]
                    txt = insert_value(txt, value_loc, value)
                his_txt = replace_his_txt(key, his_txt, txt)
        return his_txt


def his_create(his_txt_file, his_model_file, his_json_file):
    # 校验所有名称全局唯一
    model = assert_key_not_repeat(his_model_file)
    # 将json转换为his文本
    his_txt2 = create_his_txt(model, his_json_file)
    # 输出成txt
    with open(his_txt_file, "w", encoding='utf-8') as file:
        file.write(his_txt2)


# 生成hl7协议的报文
# 相当于his解析的逆向操作，给一个数据json，一个model.json，即可实现hl7报文的实现
if __name__ == '__main__':
    his_txt_file1 = "his_data2.txt"
    his_model_file1 = "his_model2.json"
    his_json_file1 = "his_data2.json"
    pipe_length = 50
    his_create(his_txt_file1, his_model_file1, his_json_file1)
