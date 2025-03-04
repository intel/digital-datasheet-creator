# Coding Standards
In this section you will find the guidelines that you must use in order to add code to the project.
## Naming Style
This code has it's own naming convention. You must consider the following table:

| **Type**  | **Naming convention**                                                                                     | **Examples**                 |
|-----------|-----------------------------------------------------------------------------------------------------------|------------------------------|
| Function  | Camel case, starting the first letter with lower case\.                                                   | myFunction\(\), function\(\) |
| Variable  | Camel case, starting the first letter with lower case\.                                                   | myVariable, variable         |
| attribute | Camel case, starting the first letter with lower case\.                                                   | myAttribute, attribute       |
| Class     | Camel case, start each word with a capital letter\.                                                       | MyClass, Class               |
| Method    | Camel case, starting the first letter with lower case\.                                                   | myMethod\(\), method\(\)     |
| Constant  | Use an uppercase single letter, word, or words\. Separate words with underscores to improve readability\. | MY\_CONSTANT, CONSTANT       |
| Module    | Camel case, starting the first letter with lower case\.                                                   | myModule\.py, module\.py     |
| Package   | Use a short, lowercase word or words\. Do not separate words with underscores\.                           | mypackage, package           |

In case to use private attributes or methods:

| **Type**  | **Naming convention**                                                          | **Examples**                     |
|-----------|--------------------------------------------------------------------------------|----------------------------------|
| attribute | Camel case, starting with one underscore and the first letter in lower case\.  | \_myAttribute, \_attribute       |
| Method    | Camel case, starting with two underscores and the first letter in lower case\. | \_\_myMethod\(\), \_\_method\(\) |

## Linting
The code must comply with Flake8 standard, for that reason, it is necessary for you to install in your code editor an extension that helps you to write Flake8 compliance code. You can also install [TOX](https://tox.wiki/en/latest/index.html) in the virtual environment and run it, it has the configuration to run Flake8 linter via command line:
```
pip install tox
tox -e lintfix
```
## Use constants
Magic numbers, strings and values are avoided, for that reason you'll find a package named "constants":
```
edatasheets_creator/
 | - constants
```
In that folder you'll define in modules, all the fixed values that you need in your code.

## Add exception handling
Always manage the possible exceptions that your code could present, for this use the try/except block:
```python
try:
  print(x)
except:
  print("An exception occurred")
```
If need more information about handling exceptions in python, look at the official [Python documentation] (https://docs.python.org/3/reference/compound_stmts.html#the-try-statement)

## Submitting code
To submit code in the repository, you must create a branch. The name of the branch must start with a verb and separate the rest of the name with underscores or dashes \(\<verb\>-\<feature brief\>\), for instance, if you are developing a new feature your branch, its name looks like:
```
develop-<feature brief>
```
To submit code to the main branch, you must create a pull request and add at least 2 code reviewers/approvers.