import json


class BizException(Exception):
    pass


def assert_key_not_repeat(model_file):
    list1 = []
    with open(model_file, encoding='utf-8') as f:
        my_dict = json.load(f)
        message_type = my_dict['messageType']
        for key in message_type.keys():
            value = message_type[key]
            for key2 in value.keys():
                if key2 not in list1:
                    list1.append(key2)
                else:
                    raise BizException(f'重复的key {key2}')
    return my_dict


# 解析his到字典
def load_his_from_txt(model, file):
    with open(file, "r", encoding='utf-8') as f:
        dict1 = {}
        list1 = get_list(model)
        for line in f:
            message_type = line.split('|')[0]
            # 有多行的情况
            if message_type in list1:
                if message_type not in dict1:
                    obx = [line]
                    dict1[message_type] = obx
                else:
                    obx = dict1[message_type]
                    obx.append(line)
            # 单行的情况
            else:
                dict1[message_type] = line
        return dict1


def get_list(model):
    list1 = []
    if 'list' in model:
        list1 = model['list']
    return list1


# 获取真正的值
def get_field(field, loc):
    if '.' in loc:
        split = loc.split('.')
        field_split = field.split('^')
        loc2 = int(split[1])
        if loc2 > len(field_split) - 1:
            return None
        return field_split[loc2]
    else:
        return field


# 通过model，解析报文数据到json
def his_analysis2(model, txt_file):
    his_txt_dict = load_his_from_txt(model, txt_file)
    message_type_order_and_length = model['messageTypeOrderAndLength']
    message_type = model['messageType']
    list1 = get_list(model)
    data_json = {}
    for message_type_item_key in message_type_order_and_length.keys():
        message_type_item = {}
        if message_type_item_key in message_type:
            message_type_item = message_type[message_type_item_key]
        # 解析出来的是多行
        if message_type_item_key in list1:
            list2 = []
            # 考虑messageType在model里面存在但是在报文中不存在的情况
            if message_type_item_key in his_txt_dict:
                rows = his_txt_dict[message_type_item_key]
                for row in rows:
                    dict2 = analysis_single_row(message_type_item, row)
                    if dict2:
                        list2.append(dict2)
            data_json[message_type_item_key] = list2
        else:
            dict2 = {}
            # 考虑messageType在model里面存在但是在报文中不存在的情况
            if message_type_item_key in his_txt_dict:
                row = his_txt_dict[message_type_item_key]
                dict2 = analysis_single_row(message_type_item, row)
            data_json[message_type_item_key] = dict2
    return data_json


# 解析单行数据
def analysis_single_row(message_type_item, row):
    fields = row.split('|')
    row_dict = {}
    for key in message_type_item.keys():
        value = message_type_item[key]
        loc = value.split(".")[0]
        loc_i = int(loc)
        if loc_i < len(fields):
            field = fields[loc_i]
            # 获取真正的值
            field2 = get_field(field, value)
            row_dict[key] = field2
        else:
            # 设置的值超过了报文的长度，导致取不出来，取值为空
            row_dict[key] = None
    return row_dict


# 根据字段进行补管道符的操作，1个字段不补，n个字段补n-1个管道符
def create_empty_message_txt(length):
    txt = ''
    if length > 1:
        for i in range(length - 1):
            txt = txt + '|'
    return txt


# 解析his数据
def his_datagram_analysis(txt_file, model_file, json_file):
    # 校验所有名称全局唯一
    model = assert_key_not_repeat(model_file)
    # 解析具体值
    his_json = his_analysis2(model, txt_file)
    # 输出成json
    with open(json_file, "w", encoding='utf-8') as file:
        json.dump(his_json, file, indent=4, ensure_ascii=False)
        print('解析his报文成功', json_file)


# msh 补偿
def msh_compensation(txt):
    if txt.startswith("MSH"):
        txt = insert_value(txt, '1', r'^~\&')
    return txt


# 将json转换为his文本
def create_his_txt(model, his_json_file):
    with open(his_json_file, encoding='utf-8') as f:
        his_json = json.load(f)
        his_txt = ''
        # 顺序读取model的config.messageType，解析出txt
        message_type_order_and_length = model['messageTypeOrderAndLength']
        message_type = model['messageType']
        list1 = model['list']
        for message_type_key in message_type_order_and_length.keys():
            message_txt_length = message_type_order_and_length[message_type_key]
            his_json_data = ''
            if message_type_key in his_json:
                his_json_data = his_json[message_type_key]
            if not his_json_data:
                # 先生成一个空的数据
                txt = message_type_key + create_empty_message_txt(message_txt_length) + '\n'
                # msh 补偿
                txt = msh_compensation(txt)
                his_txt = his_txt + txt
            elif message_type_key in list1:
                for item in his_json_data:
                    # 先生成一个空的数据
                    txt = message_type_key + create_empty_message_txt(message_txt_length) + '\n'
                    # 插入数据
                    model_item = message_type[message_type_key]
                    for model_item_key in model_item.keys():
                        value = item[model_item_key]
                        value_loc = model_item[model_item_key]
                        txt = insert_value(txt, value_loc, value)
                    his_txt = his_txt + txt
            else:
                # 先生成一个空的数据
                txt = message_type_key + create_empty_message_txt(message_txt_length) + '\n'
                # msh 补偿
                txt = msh_compensation(txt)
                # 插入数据
                model_item = message_type[message_type_key]
                for model_item_key in model_item.keys():
                    value = his_json_data[model_item_key]
                    value_loc = model_item[model_item_key]
                    txt = insert_value(txt, value_loc, value)
                his_txt = his_txt + txt
        return his_txt


# 将值value插入到txt的value_loc位置
def insert_value(txt, value_loc, value):
    # 先去掉\n，然后再补回来
    txt = txt[:len(txt) - 1]
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
            txt2 = txt2 + '\n'
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
                    if loc2 > field_length - 1:
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
            txt2 = txt2 + '\n'
            return txt2
    return txt


# 生成his报文
def his_datagram_create(his_txt_file, his_model_file, his_json_file):
    # 校验所有名称全局唯一
    model = assert_key_not_repeat(his_model_file)
    # 将json转换为his文本
    his_txt2 = create_his_txt(model, his_json_file)
    # 输出成txt
    with open(his_txt_file, "w", encoding='utf-8') as file:
        file.write(his_txt2)
        print('生成his报文成功', his_txt_file)


# 2023年6月21日 his通用解析及报文生成：只使用常规his操作，非常规的不能支持，还是需要独立开发
# 通过一个model.json，可以将任意的data.txt转换为data.json
# 通过一个model.json，可以将任意的data.json转换为data.txt
# model.json几个字段介绍
# messageType：对应的每个消息头里面包含的哪些字段，需要保证每个字段全局唯一
# filed：定义字段的注释，类型（暂未实现类型的转换，默认生成json全部都是str类型，请按需进行二次开发）
# messageTypeOrderAndLength：通过data.json生成data.txt的时候，指定好请求头的顺序以及需要生成的数据长度
# list：data.txt里面出现多个请求头的需要填入
if __name__ == '__main__':
    his_txt_file1 = "his1_data.txt"
    his_model_file1 = "his1_model.json"
    his_json_file1 = "his1_data.json"
    # 从data.txt中解析出data.json
    his_datagram_analysis(his_txt_file1, his_model_file1, his_json_file1)
    # 从data.json中生成data.txt
    his_txt_file2 = "his2_data.txt"
    his_datagram_create(his_txt_file2, his_model_file1, his_json_file1)
