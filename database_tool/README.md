### 自动模拟插入数据库工具

- **需要环境:** Python 3.11.8
- **需要依赖包:**
  - pymysql: MySQL连接工具
  - pyyaml: YML读取
  - faker: 模拟数据

- **使用方法:** 修改`insertTestData.yaml`，指定好自己需要插入数据的库、表、列和插入数据量。运行`run.py`，程序会自动按照设计自动去插入。

- **语法说明:yml内容**
  - db_type：指定数据库类型
  - mysql.datasource.host：主机
  - mysql.datasource.username：用户名
  - mysql.datasource.password：用户名
  - mysql.datasource.db：数据库
  - mysql.datasource.count：插入数量
  - mysql.datasource.table：表名
  - mysql.datasource.column：下面的全部都是表的字段，字段必须在表中存在
  - mysql.datasource.column.is_deleted：表字段名，字段必须在表中存在
- **语法说明:随机值**
  - enum: 枚举，后面是一个列表，有字符串类型和数字类型。不带引号就是数字类型，带引号就是字符串类型。比如：enum['A1','A2','A3','B1','B2']
  - first_name: 名
  - last_name: 姓
  - rand_int: 随机数字
  - kana: 片假名
  - email: 邮箱
  - rand_str: 随机字符串


