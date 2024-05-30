### Automatic Database Insertion Tool

- **Environment Requirements:** Python 3.11.8
- **Dependencies:**
  - pymysql: MySQL Connection Tool
  - pyyaml: YAML Reader
  - faker: Data Simulation

- **Usage:** Modify `insertTestData.yaml`, specify the database, table, columns, and the number of data to be inserted. Run `run.py`, and the program will automatically insert according to the design.

- **Syntax Explanation: YML Content**
  - db_type: Specify the database type
  - mysql.datasource.host: Host
  - mysql.datasource.username: Username
  - mysql.datasource.password: Password
  - mysql.datasource.db: Database
  - mysql.datasource.count: Number of inserts
  - mysql.datasource.table: Table name
  - mysql.datasource.column: Below are all the table's fields, which must exist in the table
  - mysql.datasource.column.is_deleted: Table field name, which must exist in the table

- **Syntax Explanation: Random Values**
  - enum: Enumeration, followed by a list. Can be string or integer types. If without quotes, it's an integer type; if with quotes, it's a string type.
  - first_name: First name
  - last_name: Last name
  - rand_int: Random integer
