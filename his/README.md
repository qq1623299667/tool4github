#### 通用his解析  
##### 2023年6月21日 his通用解析及报文生成：只使用常规his操作，非常规的不能支持，还是需要独立开发
- 通过一个model.json，可以将任意的data.txt转换为data.json
- 通过一个model.json，可以将任意的data.json转换为data.txt
##### model.json几个字段介绍
- messageType：对应的每个消息头里面包含的哪些字段，需要保证每个字段全局唯一
- filed：定义字段的注释，类型（暂未实现类型的转换，默认生成json全部都是str类型，请按需进行二次开发）
- messageTypeOrderAndLength：通过data.json生成data.txt的时候，指定好请求头的顺序以及需要生成的数据长度
- list：data.txt里面出现多个请求头的需要填入