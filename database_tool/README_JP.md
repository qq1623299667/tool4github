### 自動データベース挿入ツール

- **環境要件:** Python 3.11.8
- **依存関係:**
  - pymysql: MySQL接続ツール
  - pyyaml: YAMLリーダー
  - faker: データシミュレーション

- **使用方法:** `insertTestData.yaml`を変更し、挿入するデータのデータベース、テーブル、列、および数量を指定します。`run.py`を実行し、プログラムは設計に従って自動的に挿入されます。

- **構文の説明: YMLコンテンツ**
  - db_type: データベースのタイプを指定します
  - mysql.datasource.host: ホスト
  - mysql.datasource.username: ユーザー名
  - mysql.datasource.password: パスワード
  - mysql.datasource.db: データベース
  - mysql.datasource.count: 挿入数
  - mysql.datasource.table: テーブル名
  - mysql.datasource.column: 以下はすべてのテーブルのフィールドで、テーブルに存在する必要があります
  - mysql.datasource.column.is_deleted: テーブルのフィールド名、テーブルに存在する必要があります

- **構文の説明: ランダム値**
  - enum: 列挙型、リストに続く。文字列型または整数型があります。引用符がない場合、整数型です。引用符が付いている場合、文字列型です。
  - first_name: 名
  - last_name: 姓
  - rand_int: ランダムな整数