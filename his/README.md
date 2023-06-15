#### 通用his解析  
解析his报文  
his_analysis.py通过配置一个model.json来解析his的文本，会按照model.json输出对应的data.json,方便对不同医院的his进行解析  

生成his报文  
his_create.py通过配置一个model.json来解析his的json，会按照model.json输出对应的data.txt，相当于上面的逆向操作  
测试数据见hisJSON示例和his文本示例  