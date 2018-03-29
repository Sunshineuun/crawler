# python基础类型阐述
# Number（数字），String（字符串），List（列表），Tuple（元组），Sets（集合），Dictionary（字典）

# Number数字
# 1.int、float、bool、complex（复数）
a, b, c, d = 20, 5.5, True, 4 + 3j
print(type(a), type(b), type(c), type(d))


# isinstance 和 type 的区别在于：
class A:
    pass


class B(A):
    pass


isinstance(A(), A)  # returns True
print(type(A()) == A)  # returns True
isinstance(B(), A)  # returns True
print(type(B()) == A)  # returns False
# type()不会认为子类是一种父类类型。
# isinstance()会认为子类是一种父类类型。
# 算数运算 //-整除，**乘方
# 注意：
# 1、Python可以同时为多个变量赋值，如a, b = 1, 2。
# 2、一个变量可以通过赋值指向不同类型的对象。
# 3、数值的除法（/）总是返回一个浮点数，要获取整数使用//操作符。
# 4、在混合计算时，Python会把整型转换成为浮点数。
# String（字符串）
# Python中的字符串用单引号(')或双引号(")括起来，同时使用反斜杠(\)转义特殊字符。
# 字符串的截取的语法格式如下：
# 变量[头下标:尾下标]；
# 索引值以 0 为开始值，-1 为从末尾的开始位置。；
# 加号 (+) 是字符串的连接符， 星号 (*) 表示复制当前字符串，紧跟的数字为复制的次数。
string = 'Rundoc'

print(string)  # 输出字符串
print(string[0:-1])  # 输出第一个到倒数第二个的所有字符
print(string[0])  # 输出字符串第一个字符
print(string[2:5])  # 输出从第三个开始到第五个的字符
print(string[2:])  # 输出从第三个开始的后的所有字符
print(string * 2)  # 输出字符串两次
print(string + "TEST")  # 连接字符串
# 1、反斜杠可以用来转义，使用r可以让反斜杠不发生转义。
# 2、字符串可以用+运算符连接在一起，用*运算符重复。
# 3、Python中的字符串有两种索引方式，从左往右以0开始，从右往左以-1开始。
# 4、Python中的字符串不能改变。

# List（列表） == 数据的概念
# 变量[头下标:尾下标]
# 和字符串一样，列表同样可以被索引和截取，列表被截取后返回一个包含所需元素的新列表
# 支持混合类型存储
list = ['abcd', 786, 2.23, 'runoob', 70.2]
tinylist = [123, 'runoob']

print(list)  # 输出完整列表
print(list[0])  # 输出列表第一个元素
print(list[1:3])  # 从第二个开始输出到第三个元素
print(list[2:])  # 输出从第三个元素开始的所有元素
print(tinylist * 2)  # 输出两次列表
print(list + tinylist)  # 连接列表
# 1、List写在方括号之间，元素用逗号隔开。
# 2、和字符串一样，list可以被索引和切片。
# 3、List可以使用+操作符进行拼接。
# 4、List中的元素是可以改变的。
# 5、List内置很多方法例如append()、pop()等等
# Tuple（元组）
# 元组（tuple）与列表类似，不同之处在于元组的元素不能修改。元组写在小括号(())里，元素之间用逗号隔开。
tuples = ('abcd', 786, 2.23, 'runoob', 70.2)
tinytuple = (123, 'runoob')

print(tuples)  # 输出完整元组
print(tuples[0])  # 输出元组的第一个元素
print(tuples[1:3])  # 输出从第二个元素开始到第三个元素
print(tuples[2:])  # 输出从第三个元素开始的所有元素
print(tinytuple * 2)  # 输出两次元组
print(tuples + tinytuple)  # 连接元组
# string、list和tuple都属于sequence（序列）。
# 1、与字符串一样，元组的元素不能修改。
# 2、元组也可以被索引和切片，方法一样。
# 3、注意构造包含0或1个元素的元组的特殊语法规则。
# 4、元组也可以使用+操作符进行拼接。

# Set（集合）
# 集合（set）是一个无序不重复元素的序列。
# 基本功能是进行成员关系测试和删除重复元素。
# 可以使用大括号 { } 或者 set() 函数创建集合，注意：创建一个空集合必须用 set() 而不是 { }，因为 { } 是用来创建一个空字典。
# !/usr/bin/python3

student = {'Tom', 'Jim', 'Mary', 'Tom', 'Jack', 'Rose'}

print(student)  # 输出集合，重复的元素被自动去掉

# 成员测试
if 'Rose' in student:
    print('Rose 在集合中')
else:
    print('Rose 不在集合中')

# set可以进行集合运算
a = set('abracadabra')
b = set('alacazam')

print(a)

print(a - b)  # a和b的差集

print(a | b)  # a和b的并集

print(a & b)  # a和b的交集

print(a ^ b)  # a和b中不同时存在的元素
