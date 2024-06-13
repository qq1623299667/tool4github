# Custom Testing Tool

## Project Description

Achieve support for multi-environment, multi-service, multi-interface, and various branches testing through simple and quick configuration to ensure normal code logic execution.

- **Language and Version**: Python 3.11.8
- **Environment Dependencies**:
  - json
  - logging
  - os
  - colorlog
  - pandas
  - requests

## Configuration Instructions

### Configure Environment

Create a file called `env.txt1`, which can contain multiple lines, each separated by a tab character. Refer to the "Environment Configuration" file. The contents are as follows:

1. **ID**: Numeric type, must be unique
2. **Environment Name**: Will be displayed in the console after running the program
3. **Secondary Environment Name**: For example, `local:dev`, separated by a colon
4. **Environment Prefix**: For example, `http://localhost:8081/api`
5. **Required Headers**: Used to set request headers, cookies, tokens, internationalization, etc.
6. **Specified Request Content**: Customizable, points to the file name of the configuration interface

### Configure Interfaces

This file is specified by the last parameter of the environment configuration. Like the environment configuration, it can contain multiple lines and comments. Refer to the "Interface Configuration" file. Each line has multiple fields, separated by a tab character. Interfaces can be repeated to achieve as much code branch coverage as possible through different parameters. The contents are as follows:

1. **Request Method**: post/get, etc.
2. **Interface Description**: Add a note to the interface for easy identification
3. **Interface URL**
4. **Request Parameters**: JSON request parameters, if none, use an empty JSON
5. **Assertions**: Represented in JSON, both key and value must match for success, can support multiple keys and values

## Testing Instructions

After configuring the environment and interface list, when executing `easy_test.py`, you will be prompted to select an environment. By selecting the corresponding environment, you can test the interface list under different environments. If the return results match the assertions exactly under different parameters, the test is considered successful. If not successful, it will be highlighted in yellow.
