import random

import pymysql
import yaml
from faker import Faker


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


def loadYML():
    # 打开并读取YAML文件
    with open('insertTestData.yaml', 'r') as file:
        data = yaml.safe_load(file)

    return data


def connect_db():
    # 连接数据库
    conn = pymysql.connect(
        host=yml['mysql']['datasource']['host'],
        user=yml['mysql']['datasource']['username'],
        password=yml['mysql']['datasource']['password'],
        database=yml['mysql']['datasource']['db']
    )

    # 创建游标对象
    cursor = conn.cursor()

    return conn, cursor


def generate_value(value):
    if value.startswith("enum"):
        random_option = do_enum(value)
        return random_option
    elif value.startswith("rand_int"):
        return random.randint(0, 100000)
    elif value.startswith("first_name"):
        fake = Faker('zh_CN')
        first_name = f'"{fake.first_name()}"'
        return first_name
    elif value.startswith("last_name"):
        fake = Faker('zh_CN')
        last_name = f'"{fake.last_name()}"'
        return last_name
    else:
        return None


def do_enum(value):
    # 提取其中的选项部分
    options = value.split("[")[1].split("]")[0].split(",")
    # 随机选择一个选项
    random_option = random.choice(options)
    return random_option


def generate_sql(column_keys, column):
    result = f"INSERT INTO {yml['mysql']['datasource']['table']} ("  # 初始化结果字符串

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
    return result


def insert_data():
    column = yml['mysql']['datasource']['column']
    column_keys = sorted(column.keys())
    try:
        for i in range(yml['mysql']['datasource']['count']):
            # 模拟插入 SQL
            sql = generate_sql(column_keys, column)
            # 执行多次插入操作
            cursor.execute(sql)
        # 提交事务
        conn.commit()
        print("插入成功")
    except Exception as e:
        # 发生异常时回滚事务
        conn.rollback()
        print("插入失败:", e)


if __name__ == '__main__':
    yml = loadYML()
    conn, cursor = connect_db()
    insert_data()
    cursor.close()
    conn.close()
