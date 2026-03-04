# Control Flow in Python

In this lesson, you'll learn how to control the flow of your programs using conditional statements and loops.

## Conditional Statements

### If-Else Statements

```python
age = 18

if age >= 18:
    print("You are an adult")
else:
    print("You are a minor")
```

### Multiple Conditions with elif

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Your grade is: {grade}")
```

### Comparison Operators

- `==` Equal to
- `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal to
- `<=` Less than or equal to

### Logical Operators

```python
age = 25
has_license = True

if age >= 18 and has_license:
    print("You can drive")
    
is_weekend = True
is_holiday = False

if is_weekend or is_holiday:
    print("Time to relax!")
```

## Loops

### For Loops

Iterate over sequences (lists, strings, ranges):

```python
# Loop through a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Loop through a range
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

# Loop through a string
for char in "Python":
    print(char)
```

### While Loops

Execute as long as a condition is true:

```python
count = 0
while count < 5:
    print(f"Count is: {count}")
    count += 1

# Password validator
password = ""
while password != "secret":
    password = input("Enter password: ")
print("Access granted!")
```

### Loop Control Statements

```python
# break - exit the loop
for num in range(10):
    if num == 5:
        break  # Stop at 5
    print(num)

# continue - skip to next iteration
for num in range(10):
    if num % 2 == 0:
        continue  # Skip even numbers
    print(num)

# else clause in loops
for num in range(5):
    print(num)
else:
    print("Loop completed!")
```

## Nested Loops

```python
# Multiplication table
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i} x {j} = {i*j}")
    print()  # New line after each row
```

## List Comprehensions

A concise way to create lists:

```python
# Traditional way
squares = []
for i in range(10):
    squares.append(i**2)

# List comprehension
squares = [i**2 for i in range(10)]

# With condition
even_squares = [i**2 for i in range(10) if i % 2 == 0]
```

## Practice Problems

### Problem 1: FizzBuzz
Write a program that prints numbers 1 to 20, but:
- For multiples of 3, print "Fizz"
- For multiples of 5, print "Buzz"
- For multiples of both, print "FizzBuzz"

```python
for num in range(1, 21):
    if num % 3 == 0 and num % 5 == 0:
        print("FizzBuzz")
    elif num % 3 == 0:
        print("Fizz")
    elif num % 5 == 0:
        print("Buzz")
    else:
        print(num)
```

### Problem 2: Sum of Even Numbers
Calculate the sum of even numbers from 1 to 100:

```python
total = sum([num for num in range(1, 101) if num % 2 == 0])
print(f"Sum of even numbers: {total}")
```

## Summary

You learned about:
- ✅ If-else conditional statements
- ✅ Comparison and logical operators
- ✅ For and while loops
- ✅ Loop control (break, continue)
- ✅ List comprehensions

---

**Ready for the next challenge?** Test your control flow skills!
