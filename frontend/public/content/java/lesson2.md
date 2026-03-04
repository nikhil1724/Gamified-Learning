# Control Flow in Java

Master decision-making and repetition in Java with conditional statements and loops.

## Conditional Statements

### If Statement

```java
int age = 18;

if (age >= 18) {
    System.out.println("You are an adult");
}
```

### If-Else Statement

```java
int temperature = 25;

if (temperature > 30) {
    System.out.println("It's hot outside!");
} else {
    System.out.println("The weather is nice.");
}
```

### If-Else-If Ladder

```java
int score = 85;
String grade;

if (score >= 90) {
    grade = "A";
} else if (score >= 80) {
    grade = "B";
} else if (score >= 70) {
    grade = "C";
} else if (score >= 60) {
    grade = "D";
} else {
    grade = "F";
}

System.out.println("Your grade is: " + grade);
```

### Nested If Statements

```java
int age = 25;
boolean hasLicense = true;

if (age >= 18) {
    if (hasLicense) {
        System.out.println("You can drive");
    } else {
        System.out.println("You need a license");
    }
} else {
    System.out.println("You are too young to drive");
}
```

### Ternary Operator

A shorthand for if-else:

```java
int age = 20;
String result = (age >= 18) ? "Adult" : "Minor";
System.out.println(result);

// Multiple ternary operators
int score = 85;
String grade = (score >= 90) ? "A" : 
               (score >= 80) ? "B" : 
               (score >= 70) ? "C" : "F";
```

## Switch Statement

```java
int day = 3;
String dayName;

switch (day) {
    case 1:
        dayName = "Monday";
        break;
    case 2:
        dayName = "Tuesday";
        break;
    case 3:
        dayName = "Wednesday";
        break;
    case 4:
        dayName = "Thursday";
        break;
    case 5:
        dayName = "Friday";
        break;
    case 6:
        dayName = "Saturday";
        break;
    case 7:
        dayName = "Sunday";
        break;
    default:
        dayName = "Invalid day";
        break;
}

System.out.println(dayName);
```

### Switch with Strings (Java 7+)

```java
String fruit = "apple";

switch (fruit) {
    case "apple":
        System.out.println("Red and crunchy");
        break;
    case "banana":
        System.out.println("Yellow and soft");
        break;
    case "orange":
        System.out.println("Orange and juicy");
        break;
    default:
        System.out.println("Unknown fruit");
}
```

### Enhanced Switch (Java 14+)

```java
int day = 3;
String dayType = switch (day) {
    case 1, 2, 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
    default -> "Invalid";
};
System.out.println(dayType);
```

## Loops

### For Loop

```java
// Basic for loop
for (int i = 0; i < 5; i++) {
    System.out.println("Count: " + i);
}

// Loop with different increments
for (int i = 0; i <= 10; i += 2) {
    System.out.println(i);  // Prints even numbers
}

// Countdown
for (int i = 10; i >= 1; i--) {
    System.out.println(i);
}
System.out.println("Blast off!");
```

### Enhanced For Loop (For-Each)

```java
// Array iteration
int[] numbers = {1, 2, 3, 4, 5};
for (int num : numbers) {
    System.out.println(num);
}

// String array
String[] fruits = {"Apple", "Banana", "Cherry"};
for (String fruit : fruits) {
    System.out.println(fruit);
}
```

### While Loop

```java
int count = 0;
while (count < 5) {
    System.out.println("Count: " + count);
    count++;
}

// Password validator
Scanner scanner = new Scanner(System.in);
String password = "";
while (!password.equals("secret")) {
    System.out.print("Enter password: ");
    password = scanner.nextLine();
}
System.out.println("Access granted!");
```

### Do-While Loop

Executes at least once:

```java
int num = 0;
do {
    System.out.println("Number: " + num);
    num++;
} while (num < 5);

// Menu system
Scanner scanner = new Scanner(System.in);
int choice;
do {
    System.out.println("1. Option A");
    System.out.println("2. Option B");
    System.out.println("0. Exit");
    System.out.print("Choose: ");
    choice = scanner.nextInt();
} while (choice != 0);
```

## Loop Control Statements

### Break Statement

```java
// Exit loop early
for (int i = 0; i < 10; i++) {
    if (i == 5) {
        break;  // Exit loop when i equals 5
    }
    System.out.println(i);
}

// Search in array
int[] numbers = {10, 20, 30, 40, 50};
int target = 30;
for (int num : numbers) {
    if (num == target) {
        System.out.println("Found: " + target);
        break;
    }
}
```

### Continue Statement

```java
// Skip current iteration
for (int i = 0; i < 10; i++) {
    if (i % 2 == 0) {
        continue;  // Skip even numbers
    }
    System.out.println(i);  // Only odd numbers
}

// Skip specific values
for (int i = 1; i <= 10; i++) {
    if (i == 5 || i == 7) {
        continue;
    }
    System.out.println(i);
}
```

### Labeled Break and Continue

```java
// Break out of nested loops
outerLoop:
for (int i = 1; i <= 3; i++) {
    for (int j = 1; j <= 3; j++) {
        if (i == 2 && j == 2) {
            break outerLoop;  // Break outer loop
        }
        System.out.println(i + ", " + j);
    }
}
```

## Nested Loops

### Multiplication Table

```java
for (int i = 1; i <= 5; i++) {
    for (int j = 1; j <= 5; j++) {
        System.out.printf("%4d", i * j);
    }
    System.out.println();
}
```

### Pattern Printing

```java
// Right triangle
for (int i = 1; i <= 5; i++) {
    for (int j = 1; j <= i; j++) {
        System.out.print("* ");
    }
    System.out.println();
}
// Output:
// *
// * *
// * * *
// * * * *
// * * * * *
```

## Practice Problems

### Problem 1: FizzBuzz

```java
public class FizzBuzz {
    public static void main(String[] args) {
        for (int i = 1; i <= 20; i++) {
            if (i % 3 == 0 && i % 5 == 0) {
                System.out.println("FizzBuzz");
            } else if (i % 3 == 0) {
                System.out.println("Fizz");
            } else if (i % 5 == 0) {
                System.out.println("Buzz");
            } else {
                System.out.println(i);
            }
        }
    }
}
```

### Problem 2: Prime Number Checker

```java
import java.util.Scanner;

public class PrimeChecker {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int num = scanner.nextInt();
        
        boolean isPrime = true;
        
        if (num <= 1) {
            isPrime = false;
        } else {
            for (int i = 2; i <= Math.sqrt(num); i++) {
                if (num % i == 0) {
                    isPrime = false;
                    break;
                }
            }
        }
        
        if (isPrime) {
            System.out.println(num + " is prime");
        } else {
            System.out.println(num + " is not prime");
        }
        
        scanner.close();
    }
}
```

### Problem 3: Factorial Calculator

```java
import java.util.Scanner;

public class Factorial {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int n = scanner.nextInt();
        
        long factorial = 1;
        for (int i = 1; i <= n; i++) {
            factorial *= i;
        }
        
        System.out.println("Factorial of " + n + " is: " + factorial);
        scanner.close();
    }
}
```

### Problem 4: Sum of Digits

```java
import java.util.Scanner;

public class SumOfDigits {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter a number: ");
        int num = scanner.nextInt();
        
        int sum = 0;
        while (num > 0) {
            sum += num % 10;  // Add last digit
            num /= 10;        // Remove last digit
        }
        
        System.out.println("Sum of digits: " + sum);
        scanner.close();
    }
}
```

## Best Practices

1. **Always use braces** even for single statements
   ```java
   // Good
   if (condition) {
       doSomething();
   }
   
   // Avoid
   if (condition)
       doSomething();
   ```

2. **Use meaningful variable names** in loops
   ```java
   // Good
   for (int studentIndex = 0; studentIndex < students.length; studentIndex++)
   
   // Acceptable for simple loops
   for (int i = 0; i < 10; i++)
   ```

3. **Avoid infinite loops**
   ```java
   // Dangerous!
   while (true) {
       // Make sure there's a break condition
   }
   ```

## Summary

You mastered:
- ✅ If-else and switch statements
- ✅ Ternary operator
- ✅ For, while, and do-while loops
- ✅ Enhanced for-each loop
- ✅ Break and continue statements
- ✅ Nested loops and patterns

---

**Excellent work!** Time to practice with coding challenges!
