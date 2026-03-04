# Functions and Modules

Learn how to write reusable code with functions and organize your code with modules.

## What are Functions?

Functions are **reusable blocks of code** that perform specific tasks.

### Benefits:
- 🔄 Code reusability
- 📝 Better organization
- 🐛 Easier debugging
- 🧪 Easier testing

## Defining Functions

```python
def greet():
    print("Hello, World!")

# Call the function
greet()
```

## Functions with Parameters

```python
def greet_person(name):
    print(f"Hello, {name}!")

greet_person("Alice")  # Hello, Alice!
greet_person("Bob")    # Hello, Bob!
```

### Multiple Parameters

```python
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)  # 8
```

## Return Values

```python
def calculate_area(length, width):
    area = length * width
    return area

room_area = calculate_area(10, 5)
print(f"Area: {room_area} sq ft")  # Area: 50 sq ft
```

### Multiple Return Values

```python
def get_user_info():
    name = "Alice"
    age = 25
    city = "New York"
    return name, age, city

user_name, user_age, user_city = get_user_info()
```

## Default Parameters

```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")

greet("Alice")              # Hello, Alice!
greet("Bob", "Hi")          # Hi, Bob!
greet("Charlie", "Hey")     # Hey, Charlie!
```

## Keyword Arguments

```python
def create_profile(name, age, city="Unknown"):
    print(f"Name: {name}, Age: {age}, City: {city}")

create_profile(name="Alice", age=25, city="NYC")
create_profile(age=30, name="Bob")  # Order doesn't matter
```

## *args and **kwargs

### Variable Arguments (*args)

```python
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15
```

### Keyword Arguments (**kwargs)

```python
def print_info(**info):
    for key, value in info.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")
```

## Lambda Functions

Anonymous, single-line functions:

```python
# Regular function
def square(x):
    return x ** 2

# Lambda equivalent
square = lambda x: x ** 2

# Common use case: with map()
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# With filter()
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
print(even_numbers)  # [2, 4]
```

## Scope and Global Variables

```python
# Global variable
global_var = "I'm global"

def my_function():
    # Local variable
    local_var = "I'm local"
    print(global_var)  # Can access global
    print(local_var)

my_function()
# print(local_var)  # Error: local_var not defined

# Modifying global variables
counter = 0

def increment():
    global counter
    counter += 1

increment()
print(counter)  # 1
```

## Modules and Imports

### Built-in Modules

```python
# Import entire module
import math
print(math.sqrt(16))  # 4.0
print(math.pi)        # 3.14159...

# Import specific functions
from math import sqrt, pi
print(sqrt(25))  # 5.0

# Import with alias
import math as m
print(m.ceil(4.3))  # 5

# Import all (not recommended)
from math import *
```

### Common Built-in Modules

```python
# random - Generate random numbers
import random
print(random.randint(1, 10))
print(random.choice(["apple", "banana", "cherry"]))

# datetime - Work with dates and times
from datetime import datetime
now = datetime.now()
print(now)

# os - Operating system interface
import os
print(os.getcwd())  # Current directory
```

## Creating Your Own Module

**mymodule.py:**
```python
def greeting(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

PI = 3.14159
```

**main.py:**
```python
import mymodule

print(mymodule.greeting("Alice"))
result = mymodule.add(5, 3)
print(f"PI value: {mymodule.PI}")
```

## Practice Exercises

### Exercise 1: Temperature Converter

```python
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

print(celsius_to_fahrenheit(0))   # 32.0
print(fahrenheit_to_celsius(32))  # 0.0
```

### Exercise 2: Palindrome Checker

```python
def is_palindrome(text):
    text = text.lower().replace(" ", "")
    return text == text[::-1]

print(is_palindrome("racecar"))    # True
print(is_palindrome("hello"))      # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

### Exercise 3: List Statistics

```python
def calculate_stats(numbers):
    return {
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }

data = [10, 20, 30, 40, 50]
stats = calculate_stats(data)
print(stats)
```

## Best Practices

1. **Use descriptive function names** - `calculate_total()` not `calc()`
2. **Keep functions focused** - Each function should do one thing well
3. **Add docstrings** - Document what your function does
4. **Use type hints** (Python 3.5+):

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"
```

## Summary

You mastered:
- ✅ Defining and calling functions
- ✅ Parameters and return values
- ✅ Default and keyword arguments
- ✅ Lambda functions
- ✅ Variable scope
- ✅ Importing and creating modules

---

**Excellent progress!** Ready to apply your function knowledge?
