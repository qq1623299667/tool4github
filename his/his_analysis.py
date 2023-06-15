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


# 解析his到字典
def load_his_from_txt(file):
    with open(file, "r", encoding='utf-8') as f:
        dict1 = {}
        for line in f:
            obx_str = "OBX"
            if line.startswith(obx_str):
                if obx_str not in dict1:
                    obx = []
                    obx.append(line)
                    dict1[obx_str] = obx
                else:
                    obx = dict1[obx_str]
                    obx.append(line)
            else:
                split = line.split('|')
                head = split[0]
                dict1[head] = line
        return dict1


# 获取真正的值
def get_field(field, loc):
    if '.' in loc:
        split = loc.split('.')
        field_split = field.split('^')
        return field_split[int(split[1])]
    else:
        return field


def his_analysis2(his_map_dict, his_txt):
    his = load_his_from_txt(his_txt)
    for key in his_map_dict.keys():
        if key != 'config':
            # 1级key
            value = his_map_dict[key]
            if isinstance(value, list):
                # 2级key
                value1 = value[0]
                list1 = []
                # 解析出来的是多行
                rows = his[key]
                for row in rows:
                    dict2 = {}
                    for key2 in value1.keys():
                        value2 = value1[key2]
                        loc = value2.split(".")[0]
                        fields = row.split('|')
                        loc_i = int(loc)
                        if loc_i < len(fields):
                            field = fields[loc_i]
                            # 获取真正的值
                            field2 = get_field(field, value2)
                            dict2[key2] = field2
                        else:
                            dict2[key2] = None
                    list1.append(dict2)
                his_map_dict[key] = list1
            elif isinstance(value, dict):
                dict2 = {}
                for key2 in value.keys():
                    value2 = value[key2]
                    loc = value2.split(".")[0]
                    fields = his[key].split('|')
                    loc_i = int(loc)
                    if loc_i < len(fields):
                        field = fields[loc_i]
                        # 获取真正的值
                        field2 = get_field(field, value2)
                        dict2[key2] = field2
                    else:
                        dict2[key2] = None
                his_map_dict[key] = dict2
    return his_map_dict


def his_analysis(his_txt, his_model, his_json):
    # 校验所有名称全局唯一
    his_map_dict = assert_key_not_repeat(his_model)
    # 解析具体值
    his_map_dict = his_analysis2(his_map_dict, his_txt)
    # 输出成json
    with open(his_json, "w", encoding='utf-8') as file:
        json.dump(his_map_dict, file, indent=4, ensure_ascii=False)


# his通用解析
# 主要是sourcemap映射关系要对齐
# key是请求头，具体的值通过位置获取，然后带小数点的是具体的子层级，多个点是多个层级
# 根据具体的source_map，通过转换器可以快速将his解析，生成json，方便获取值
# 通过记录公司，名称，版本这三个唯一识别获取source_map，然后快速解析到需要的字段
# 默认全部为string字符串类型，如果需要进行特殊处理，需要指定config类型，以及字段的名称config.type
# 可以指定注释内容 config.comment
# 保证每个字段全局唯一
# 没有的话就是空，会去掉原始所有value
if __name__ == '__main__':
    his_txt1 = "his_data1.txt"
    his_model1 = "his_model1.json"
    his_json1 = "his_data1.json"
    his_analysis(his_txt1, his_model1, his_json1)
