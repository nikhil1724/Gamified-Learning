# Introduction to Java

Welcome to Java programming! In this lesson, you'll learn the fundamentals of one of the most popular programming languages.

## What is Java?

Java is a **high-level**, **object-oriented** programming language known for:

- ☕ Write Once, Run Anywhere (WORA)
- 🏢 Enterprise-level applications
- 📱 Android app development
- 🔒 Strong security features
- 🚀 High performance

## Your First Java Program

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

### Understanding the Code:
1. `public class HelloWorld` - Defines a class named HelloWorld
2. `public static void main(String[] args)` - Entry point of the program
3. `System.out.println()` - Prints text to console
4. Every Java program must have a class and a main method

## Java Program Structure

```java
// Single-line comment

/*
 * Multi-line comment
 * Used for documentation
 */

/**
 * Javadoc comment
 * Used to generate documentation
 */
public class MyProgram {
    public static void main(String[] args) {
        // Your code here
    }
}
```

## Variables and Data Types

### Primitive Data Types

```java
// Integer types
byte myByte = 100;        // 8-bit (-128 to 127)
short myShort = 5000;     // 16-bit
int myInt = 100000;       // 32-bit
long myLong = 15000000000L; // 64-bit (note the L)

// Floating-point types
float myFloat = 5.99f;    // 32-bit (note the f)
double myDouble = 19.99;  // 64-bit

// Character and Boolean
char myChar = 'A';        // Single character
boolean isJavaFun = true; // true or false
```

### Reference Types

```java
// Strings
String name = "John Doe";
String greeting = "Hello, Java!";

// String concatenation
String fullName = "John" + " " + "Doe";
System.out.println(fullName);
```

## Variables

### Declaring Variables

```java
// Declaration
int age;

// Initialization
age = 25;

// Declaration + Initialization
int score = 100;

// Multiple declarations
int x = 5, y = 10, z = 15;

// Constants (cannot be changed)
final double PI = 3.14159;
final int MAX_STUDENTS = 30;
```

### Variable Naming Rules

✅ **Valid:**
- `myVariable`
- `_privateVar`
- `$specialVar`
- `age2`

❌ **Invalid:**
- `2age` (starts with number)
- `my-variable` (contains hyphen)
- `class` (reserved keyword)

## Operators

### Arithmetic Operators

```java
int a = 10, b = 3;

int sum = a + b;           // 13
int difference = a - b;     // 7
int product = a * b;        // 30
int quotient = a / b;       // 3 (integer division)
int remainder = a % b;      // 1

double preciseDiv = (double)a / b;  // 3.333... (cast to double)
```

### Increment and Decrement

```java
int count = 5;

count++;  // count = 6 (post-increment)
++count;  // count = 7 (pre-increment)

count--;  // count = 6 (post-decrement)
--count;  // count = 5 (pre-decrement)

// Compound operators
count += 5;  // count = count + 5
count -= 2;  // count = count - 2
count *= 3;  // count = count * 3
count /= 4;  // count = count / 4
```

### Comparison Operators

```java
int x = 5, y = 10;

boolean isEqual = (x == y);        // false
boolean isNotEqual = (x != y);     // true
boolean isGreater = (x > y);       // false
boolean isLess = (x < y);          // true
boolean isGreaterOrEqual = (x >= y); // false
boolean isLessOrEqual = (x <= y);  // true
```

### Logical Operators

```java
boolean a = true, b = false;

boolean and = a && b;  // false (AND)
boolean or = a || b;   // true (OR)
boolean not = !a;      // false (NOT)
```

## Input and Output

### Output

```java
System.out.println("New line after");  // With new line
System.out.print("No new line");       // Without new line

// Formatted output
String name = "Alice";
int age = 25;
System.out.printf("Name: %s, Age: %d%n", name, age);
```

### Input (using Scanner)

```java
import java.util.Scanner;

public class InputExample {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Enter your name: ");
        String name = scanner.nextLine();
        
        System.out.print("Enter your age: ");
        int age = scanner.nextInt();
        
        System.out.println("Hello, " + name + "! You are " + age + " years old.");
        
        scanner.close();
    }
}
```

## Type Casting

```java
// Widening (automatic)
int myInt = 9;
double myDouble = myInt;  // 9.0

// Narrowing (manual)
double myDouble = 9.78;
int myInt = (int) myDouble;  // 9 (loses decimal)

// String to number
String ageStr = "25";
int age = Integer.parseInt(ageStr);

double price = Double.parseDouble("19.99");

// Number to string
int num = 100;
String str = String.valueOf(num);
// or
String str2 = Integer.toString(num);
```

## Practice Exercise

Create a program that:
1. Takes two numbers as input
2. Performs all arithmetic operations
3. Displays the results

```java
import java.util.Scanner;

public class Calculator {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Enter first number: ");
        int num1 = scanner.nextInt();
        
        System.out.print("Enter second number: ");
        int num2 = scanner.nextInt();
        
        System.out.println("Sum: " + (num1 + num2));
        System.out.println("Difference: " + (num1 - num2));
        System.out.println("Product: " + (num1 * num2));
        System.out.println("Quotient: " + (num1 / num2));
        System.out.println("Remainder: " + (num1 % num2));
        
        scanner.close();
    }
}
```

## Summary

In this lesson, you learned:
- ✅ Java program structure
- ✅ Variables and data types
- ✅ Operators (arithmetic, comparison, logical)
- ✅ Input and output using Scanner
- ✅ Type casting and conversion

---

**Great start!** Ready to test your Java fundamentals?
