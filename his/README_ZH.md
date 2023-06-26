#### 通用his解析  
##### his通用解析及报文生成：只使用常规his操作，非常规的不能支持，还是需要独立开发
- 通过一个model.json，可以将任意的data.txt转换为data.json
- 通过一个model.json，可以将任意的data.json转换为data.txt
##### model.json几个字段介绍
- messageType：对应的每个消息头里面包含的哪些字段，需要保证每个字段全局唯一
- filed：定义字段的注释
- messageTypeOrderAndLength：通过data.json生成data.txt的时候，指定好请求头的顺序以及需要生成的数据长度
- list：data.txt里面出现多个请求头的需要填入
#### his_model：方便excel和model互转
最初his协议定下来之后，可以得到这样一个excel表格  

| 字段        | 注释   | 消息头 | 位置  |
|-----------|------|-----|-----|
| id        | 病人id | PV1 | 7   |
| firstName | 姓    | PID | 5.1 |
| lastName  | 名    | PID | 5.0 |
| gender    | 性别   | DG1 | 8   |
| age       | 年龄   | PID | 6.0 |

这个表格，可以通过his_model.py脚本进行转换成对应的model.json  
也可以翻译现有的model.json，增强可读性  
得到model.json之后，可以任意转换his报文成json，或者把json转换成报文