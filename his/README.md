#### Universal HIS parsing  
##### HIS general parsing and packet generation: Only conventional HIS operations are used, and unconventional ones cannot be supported, or independent development is required
- With a model.json, you can convert arbitrary data.txt to data.json
- With a model.json, you can convert arbitrary data.json to a data.txt
##### Model.json is described in several fields
- messageType：The corresponding fields contained in each message header need to ensure that each field is globally unique
- filed: Define the comments for the field
- messageTypeOrderAndLength: When generating a data .txt through data.json, specify the order of the request headers and the length of the data to be generated
- list：Data.txt multiple request headers need to be filled in
#### his_model：Easy to transfer Excel and model
After the initial HIS protocol is finalized, such an excel table can be obtained  

| 字段        | 注释   | 消息头 | 位置  |
|-----------|------|-----|-----|
| id        | 病人id | PV1 | 7   |
| firstName | 姓    | PID | 5.1 |
| lastName  | 名    | PID | 5.0 |
| gender    | 性别   | DG1 | 8   |
| age       | 年龄   | PID | 6.0 |

This table can be converted to the corresponding model.json through his_model.py script  
You can also translate existing model.json for readability  
After getting model.json, you can arbitrarily convert his message to json, or convert json to packet  