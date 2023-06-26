#### Cobweb system  
A general purpose monitoring independent of platform monitoring to monitor the following aspects
- Server power-on, disk, memory conditions
- Whether the service is healthy and viable
- Number of system logs
- System exception logs are developed for specific services
- Monitor the latest creation/update/other times of tables related to the server database  
##### Dependent environment
python：3.8.10  
Logbook：1.5.3  
colorlog：6.7.0  
pandas：1.4.2  
paramiko：2.10.3  
PyMySQL：1.0.2  
No secondary development is required, only the corresponding configuration file needs to be configured, the specific configuration and instructions are as follows：
##### env.txt  
Purpose: It is mainly used to distinguish different environments of different projects, and may be dynamically generated in the optional list after configuration  
Configuration content (be sure to be separated by tabs) is from front to back  
- Serial number (non-repeatable)
- Environment name nickname
- Environment (separated by colons, preceded by the project name followed by the specific environment name)  
##### mysql_latest_time.txt 
Purpose: It is used for simple service monitoring with time, such as wondering whether a user is logged in to a certain environment today, reporting data on the device, and so on  
Configuration content (be sure to be separated by tabs) is from front to back  
- Database name
- Table name
- Time field
- Project name
- Environment name
##### mysql_pass.txt 
Purpose: Stores the database account password of MySQL  
Configuration content (be sure to be separated by tabs) is from front to back  
- Project name
- Environment name
- Database IP address
- port
- Account
- password
##### mysql_sql.txt 
Purpose: General mySQL query statement configuration file  
Configuration content (be sure to be separated by tabs) is from front to back  
- SQL unique identifier
- Environment name
- Specific SQL
##### server_log.txt 
Uses: Business-related monitoring can be carried out, such as monitoring whether the service is alive, whether too many logs are printed and more problems can be inferred, such as the crazy loop of the program.  
Devices send crazy messages, or hackers frantically adjust interfaces and so on. You can also monitor the abnormal log, and you can bury the abnormal business log in the code in advance.  
Exceptions that need attention can be caught as soon as possible, without manually viewing the exception logs of each server and service one by one  
Configuration content (be sure to be separated by tabs) is from front to back  
- Server IP address
- The directory where the logs are located
- Log name
- Service name
- Project name
- Environment name
##### server_pass.txt 
Purpose: It can monitor some hardware indicators of the server to avoid memory exceeding the standard, hard disk explosion and so on    
Configuration content (be sure to be separated by tabs) is from front to back  
- Server IP address
- Account
- password
#### Spider web system demonstration
- Monitor MySQL up-to-date time.gif
![img.png](../resource/images/spider/监控mysql最新时间.gif)
- Monitor server health.gif
![img.png](../resource/images/spider/监控服务器健康状况.gif)
- Monitor service viability.gif
![img.png](../resource/images/spider/监控服务存活情况.gif)
- Monitor system exception logs.gif
![img.png](../resource/images/spider/监控系统异常日志.gif)
- Monitor the number of system logs.gif
![img.png](../resource/images/spider/监控系统日志数量.gif)
