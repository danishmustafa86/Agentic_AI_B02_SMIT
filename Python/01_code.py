# Input and output in Python

name = input("Please enter your name: ")
marks = input("Please enter you marks: ")


# Type checking and type conversion
print("Type of name variable: ", type(name))
print("Type of marks variable: ", type(marks))
marks = int(marks)       # Now, I have convert marks variable type to interger.
marks = float(marks)
percentage = 77.349
percentage = int(percentage)
print("Student marks are: ", marks)
print("Type of marks variable after type conversion: ", type(marks))

# fstring in Python
print(f"Student name is {name}")
print("Student name is ", name)
print("Student name is " + "ali")

# Arithmetic Operators

num1 = 34
num2 = 23
sum = num1 + num2
subtraction = num1 - num2
multiplication = num1 * num2
division = num1 / num2 
divsion2 = num1 // num2
remainder = num1 % num2 
power = num1 ** num2    

# Comparison Operators
#   >, < , >=, <=, ==, !=, =
# marks = input("Please enter your marks ")
num1 = int(input("Please enter num1 "))
num2 = int(input("Please enter num2 "))
num = num1 == num2
print(num1 > num2)
print(num1 < num2)
print(num1 >= num2)
print(num1 <= num2)
print(num1 == num2)
print(num1 != num2)

# Take username anf age from user as input, print them, also print their type.
# Convert age to integer and print using fstring, without f string and using concat operator.
# print the comparison of two numbers using comaprison operators.



