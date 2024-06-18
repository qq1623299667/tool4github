import random
import re
import string

import pymysql
import yaml
from faker import Faker
from datetime import datetime, timedelta


def get_value_from_yaml1(path):
    yaml_file = 'insertTestData.yaml'
    return get_value_from_yaml(yaml_file, path)


def get_value_from_yaml(yaml_file, path):
    # 读取 YAML 文件内容
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)

    # 解析路径
    keys = path.split('.')
    value = config

    # 遍历路径中的每个键
    for key in keys:
        if key.startswith('$'):
            continue
        value = value[key]

    return value


def testMysql():
    # 连接数据库
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="gn_business_db"
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 执行SQL查询
    cursor.execute("SELECT * FROM staff")

    # 获取查询结果
    result = cursor.fetchall()
    for row in result:
        print(row)

    # 关闭游标和连接
    cursor.close()
    conn.close()


def testYML():
    # 打开并读取YAML文件
    with open('insertTestData.yaml', 'r') as file:
        data = yaml.safe_load(file)

    # 打印读取的数据
    print(data)


def testFake():
    # 创建一个Faker对象
    fake = Faker()

    # 生成虚拟姓名
    print("Fake Name:", fake.name())

    # 生成虚拟地址
    print("Fake Address:", fake.address())

    # 生成虚拟电子邮件
    print("Fake Email:", fake.email())

    # 生成虚拟文本
    print("Fake Text:", fake.text())

    # 生成虚拟数字
    print("Fake Number:", fake.random_number())


def loadYML(yml_path):
    # 打开并读取YAML文件
    with open(yml_path, 'r') as file:
        data = yaml.safe_load(file)

    return data


def connect_db():
    host_path = '$.mysql.datasource.host'
    username_path = '$.mysql.datasource.username'
    password_path = '$.mysql.datasource.password'
    db_path = '$.mysql.datasource.db'

    host = get_value_from_yaml1(host_path)
    user = get_value_from_yaml1(username_path)
    password = get_value_from_yaml1(password_path)
    database = get_value_from_yaml1(db_path)

    # 连接数据库
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    # 创建游标对象
    cursor = conn.cursor()

    return conn, cursor


def generate_value(value):
    if value.startswith("enum"):
        random_option = do_enum(value)
        return random_option
    elif value.startswith("int"):
        return replace_rand_int(value)
    elif value.startswith("varchar"):
        letters_and_digits = string.ascii_letters + string.digits
        str1 = ''.join(random.choice(letters_and_digits) for _ in range(random.randint(1, 10)))
        return f'"{str1}"'
    elif value.startswith("first_name"):
        fake = Faker('zh_CN')
        first_name = f'"{fake.first_name()}"'
        return first_name
    elif value.startswith("last_name"):
        fake = Faker('zh_CN')
        last_name = f'"{fake.last_name()}"'
        return last_name
    elif value.startswith("kana"):
        fake = Faker('ja_JP')
        # 将自定义提供者添加到 Faker 实例
        fake.add_provider(KatakanaProvider)

        kana = f'"{fake.katakana(2)}"'
        return kana
    elif value.startswith("email"):
        fake = Faker()
        email = f'"{fake.email()}"'
        return email
    elif value=="datetime":
        time1 = random_datetime_string()
        time2 = f'"{time1}"'
        return time2
    elif value=="date":
        time1 = random_date_string()
        time2 = f'"{time1}"'
        return time2
    else:
        return None


def replace_rand_int(input_string):
    # 定义匹配模式
    pattern_full = r'int\[(\d+),(\d+)\]'
    pattern_simple = r'int'

    # 处理带有范围的模式 rand_int[min,max]
    def full_replacer(match):
        min_val = int(match.group(1))
        max_val = int(match.group(2))
        return str(random.randint(min_val, max_val))

    # 处理简单模式 rand_int
    def simple_replacer(match):
        return str(random.randint(0, 10000))

    # 先处理带范围的模式
    result_string = re.sub(pattern_full, full_replacer, input_string)
    # 再处理简单模式
    result_string = re.sub(pattern_simple, simple_replacer, result_string)

    return result_string


def random_datetime_string():
    year = random.randint(1970, 2030)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    random_datetime = datetime(year, month, day, hour, minute, second)
    return random_datetime.strftime("%Y-%m-%d %H:%M:%S")
def random_date_string():
    # 定义日期范围
    start_date = datetime(1970, 1, 1)
    end_date = datetime(2030, 12, 31)

    # 生成随机日期
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

    # 将日期转换为字符串
    random_date_str = random_date.strftime("%Y-%m-%d")
    return random_date_str

def do_enum(value):
    # 提取其中的选项部分
    options = value.split("[")[1].split("]")[0].split(",")
    # 随机选择一个选项
    random_option = random.choice(options)
    return random_option


def generate_sql(table_name,column_keys, column):
    result = f"INSERT INTO {table_name} ("  # 初始化结果字符串

    # 遍历字典的键值对，并累加到结果字符串中
    for key in column_keys:
        result += f"{key}, "

    # 移除最后一个逗号和空格
    result = result.rstrip(", ")
    result += ") VALUES ("
    for key in column_keys:
        value = column[key]
        fake_value = generate_value(value)
        result += f" {fake_value}, "
    result = result.rstrip(", ")
    result += ")"
    print(result)
    return result


def insert_data1(table_name):
    table_name_yml = table_name+'.yml'
    column = loadYML(table_name_yml)

    column_keys = sorted(column.keys())

    count_path = '$.mysql.datasource.count'
    count_value = get_value_from_yaml1(count_path)

    try:
        for i in range(count_value):
            # 模拟插入 SQL
            sql = generate_sql(table_name,column_keys, column)
            # 执行多次插入操作
            cursor.execute(sql)
        # 提交事务
        conn.commit()
        print("插入成功")
    except Exception as e:
        # 发生异常时回滚事务
        conn.rollback()
        print("插入失败:", e)


def insert_data():
    # 获取所有的表
    table_path = '$.mysql.datasource.table'
    table_value = get_value_from_yaml1(table_path)
    for table_name in table_value:
        insert_data1(table_name)




class KatakanaProvider:
    katakana_chars = [
        'ア', 'イ', 'ウ', 'エ', 'オ',
        'カ', 'キ', 'ク', 'ケ', 'コ',
        'サ', 'シ', 'ス', 'セ', 'ソ',
        'タ', 'チ', 'ツ', 'テ', 'ト',
        'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
        'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
        'マ', 'ミ', 'ム', 'メ', 'モ',
        'ヤ', 'ユ', 'ヨ',
        'ラ', 'リ', 'ル', 'レ', 'ロ',
        'ワ', 'ヲ', 'ン',
        'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
        'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
        'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
        'バ', 'ビ', 'ブ', 'ベ', 'ボ',
        'パ', 'ピ', 'プ', 'ペ', 'ポ',
        'キャ', 'キュ', 'キョ',
        'シャ', 'シュ', 'ショ',
        'チャ', 'チュ', 'チョ',
        'ニャ', 'ニュ', 'ニョ',
        'ヒャ', 'ヒュ', 'ヒョ',
        'ミャ', 'ミュ', 'ミョ',
        'リャ', 'リュ', 'リョ',
        'ギャ', 'ギュ', 'ギョ',
        'ジャ', 'ジュ', 'ジョ',
        'ビャ', 'ビュ', 'ビョ',
        'ピャ', 'ピュ', 'ピョ'
    ]

    def __init__(self, generator):
        self.generator = generator

    def katakana(self, length=5):
        return ''.join(random.choices(self.katakana_chars, k=length))


if __name__ == '__main__':
    core_yml_path = 'insertTestData.yaml'
    yml = loadYML(core_yml_path)
    conn, cursor = connect_db()
    insert_data()
    cursor.close()
    conn.close()
