from werkzeug.security import generate_password_hash

from database import db
from models import (
    Badge,
    CodeSubmission,
    CodingProblem,
    Course,
    DailyChallenge,
    Enrollment,
    Lesson,
    LessonProgress,
    Note,
    Problem,
    ProblemProgress,
    ProblemTestCase,
    Progress,
    Question,
    Quiz,
    QuizAttempt,
    Reward,
    Skill,
    Submission,
    User,
    UserBadge,
    UserReward,
    UserSkill,
)


DEMO_PASSWORD = "Demo@123"
DEMO_PASSWORD_HASH = generate_password_hash(DEMO_PASSWORD)

DEMO_USER_EMAILS = [
    "admin@lms.com",
    "john@lms.com",
    "priya@lms.com",
    "rahul@student.com",
    "anita@student.com",
]

DEMO_COURSE_TITLES = [
    "Python Programming Basics",
    "Java Programming Mastery",
    "Data Structures & Algorithms",
    "Web Development (HTML, CSS, JS)",
    "DBMS Fundamentals",
    "C++ Programming",
    "Operating Systems Basics",
]

DEMO_QUIZ_TITLES = [
    "Python Basics Quiz 1 (XP 50)",
    "Python Basics Quiz 2 (XP 75)",
    "Python Basics Quiz 3 (XP 100)",
    "Java Mastery Quiz 1 (XP 50)",
    "Java Mastery Quiz 2 (XP 75)",
    "Java Mastery Quiz 3 (XP 100)",
    "DSA Quiz 1 (XP 75)",
    "DSA Quiz 2 (XP 100)",
    "DSA Quiz 3 (XP 150)",
    "Web Development Quiz 1 (XP 80)",
    "DBMS Fundamentals Quiz 1 (XP 80)",
    "Operating Systems Quiz 1 (XP 90)",
]

DEMO_PROBLEM_TITLES = [
    "Reverse a String",
    "Check Palindrome",
    "Two Sum",
    "Fibonacci Series",
    "Merge Sorted Arrays",
    "Valid Parentheses",
    "FizzBuzz",
    "Anagram Check",
    "Climbing Stairs",
    "Binary Search",
    "Longest Substring Without Repeating Characters",
    "Maximum Subarray",
    "Top K Frequent Elements",
    "Kth Largest Element in Array",
    "Course Schedule",
    "Binary Tree Level Order Traversal",
    "Rotate Matrix",
    "Longest Increasing Subsequence",
    "LRU Cache",
    "Median of Two Sorted Arrays",
    "N-Queens",
    "Merge K Sorted Lists",
    "Trapping Rain Water",
]

DEMO_CODING_PROBLEM_TITLES = [
    "Reverse a String",
    "Check Prime Number",
    "Palindrome Check",
    "Factorial",
]

DEMO_SKILLS = [
    "Python Basics",
    "Web Development Fundamentals",
]

DEMO_BADGES = [
    "Beginner Solver",
    "Python Master",
    "5-Day Streak",
]

DEMO_REWARDS = [
    "Quiz Explorer",
    "Course Finisher",
    "Streak Keeper",
]


def _get_or_create_user(email, defaults):
    user = User.query.filter_by(email=email).first()
    if user:
        return user, False
    user = User(email=email, **defaults)
    db.session.add(user)
    return user, True


def _get_or_create_course(title, defaults):
    course = Course.query.filter_by(title=title).first()
    if course:
        return course, False
    course = Course(title=title, **defaults)
    db.session.add(course)
    return course, True


def _get_or_create_badge(name, defaults):
    badge = Badge.query.filter_by(name=name).first()
    if badge:
        return badge, False
    badge = Badge(name=name, **defaults)
    db.session.add(badge)
    return badge, True


def _get_or_create_reward(name, defaults):
    reward = Reward.query.filter_by(badge_name=name).first()
    if reward:
        return reward, False
    reward = Reward(badge_name=name, **defaults)
    db.session.add(reward)
    return reward, True


def seed_quiz_data():
    created_any = False

    # Users
    admin, created = _get_or_create_user(
        "admin@lms.com",
        {
            "name": "Admin User",
            "password_hash": DEMO_PASSWORD_HASH,
            "role": "admin",
            "is_approved": True,
            "level": 6,
            "xp_points": 1800,
            "coins": 450,
            "daily_streak": 7,
        },
    )
    created_any = created_any or created

    john, created = _get_or_create_user(
        "john@lms.com",
        {
            "name": "John Parker",
            "password_hash": DEMO_PASSWORD_HASH,
            "role": "teacher",
            "is_approved": True,
            "level": 4,
            "xp_points": 1200,
            "coins": 220,
            "daily_streak": 3,
        },
    )
    created_any = created_any or created

    priya, created = _get_or_create_user(
        "priya@lms.com",
        {
            "name": "Priya Sharma",
            "password_hash": DEMO_PASSWORD_HASH,
            "role": "teacher",
            "is_approved": True,
            "level": 5,
            "xp_points": 1500,
            "coins": 300,
            "daily_streak": 5,
        },
    )
    created_any = created_any or created

    rahul, created = _get_or_create_user(
        "rahul@student.com",
        {
            "name": "Rahul Verma",
            "password_hash": DEMO_PASSWORD_HASH,
            "role": "student",
            "is_approved": True,
            "level": 2,
            "xp_points": 420,
            "coins": 90,
            "daily_streak": 2,
        },
    )
    created_any = created_any or created

    anita, created = _get_or_create_user(
        "anita@student.com",
        {
            "name": "Anita Nair",
            "password_hash": DEMO_PASSWORD_HASH,
            "role": "student",
            "is_approved": True,
            "level": 3,
            "xp_points": 680,
            "coins": 130,
            "daily_streak": 4,
        },
    )
    created_any = created_any or created

    db.session.flush()

    # Courses (metadata stored in description since schema lacks dedicated fields)
    python_course, created = _get_or_create_course(
        "Python Programming Basics",
        {
            "description": (
                "Learn core Python syntax, data types, loops, functions, and problem solving.\n"
                "Difficulty: Beginner\n"
                "Category: Programming\n"
                "XP Reward: 260\n"
                "Tags: variables, loops, functions, strings"
            ),
            "teacher_id": priya.id,
        },
    )
    created_any = created_any or created

    java_course, created = _get_or_create_course(
        "Java Programming Mastery",
        {
            "description": (
                "Build strong Java fundamentals with OOP, collections, and exception handling.\n"
                "Difficulty: Intermediate\n"
                "Category: Programming\n"
                "XP Reward: 320\n"
                "Tags: oop, classes, inheritance, collections"
            ),
            "teacher_id": john.id,
        },
    )
    created_any = created_any or created

    dsa_course, created = _get_or_create_course(
        "Data Structures & Algorithms",
        {
            "description": (
                "Master arrays, linked lists, trees, graphs, and algorithmic optimization.\n"
                "Difficulty: Advanced\n"
                "Category: DSA\n"
                "XP Reward: 460\n"
                "Tags: arrays, trees, graphs, dynamic programming"
            ),
            "teacher_id": john.id,
        },
    )
    created_any = created_any or created

    web_course, created = _get_or_create_course(
        "Web Development (HTML, CSS, JS)",
        {
            "description": (
                "Build responsive interfaces and interactive pages with modern web standards.\n"
                "Difficulty: Intermediate\n"
                "Category: Web\n"
                "XP Reward: 340\n"
                "Tags: html, css, javascript, dom"
            ),
            "teacher_id": priya.id,
        },
    )
    created_any = created_any or created

    dbms_course, created = _get_or_create_course(
        "DBMS Fundamentals",
        {
            "description": (
                "Master relational modeling, SQL queries, indexing, and ACID transactions.\n"
                "Difficulty: Intermediate\n"
                "Category: Database\n"
                "XP Reward: 300\n"
                "Tags: sql, normalization, joins, indexing"
            ),
            "teacher_id": john.id,
        },
    )
    created_any = created_any or created

    cpp_course, created = _get_or_create_course(
        "C++ Programming",
        {
            "description": (
                "Learn C++ syntax, STL containers, pointers, and object-oriented design.\n"
                "Difficulty: Intermediate\n"
                "Category: Programming\n"
                "XP Reward: 350\n"
                "Tags: pointers, stl, oop, memory"
            ),
            "teacher_id": john.id,
        },
    )
    created_any = created_any or created

    os_course, created = _get_or_create_course(
        "Operating Systems Basics",
        {
            "description": (
                "Understand processes, threads, memory management, scheduling, and file systems.\n"
                "Difficulty: Beginner\n"
                "Category: Systems\n"
                "XP Reward: 280\n"
                "Tags: process, threads, scheduling, memory"
            ),
            "teacher_id": priya.id,
        },
    )
    created_any = created_any or created

    db.session.flush()

    # Lessons (markdown content)
    lesson_specs = [
        (
            python_course,
            [
                (
                    "Introduction to Python",
                    """# Introduction to Python\n\nPython is a beginner-friendly language used in web, data, and automation.\n\n## Why Python?\n- Simple, readable syntax\n- Huge standard library\n- Great for beginners and pros\n\n## Hello World\n```python\nprint(\"Hello, World!\")\n```\n\n**Tip:** Python uses indentation to define code blocks.\n""",
                    1,
                ),
                (
                    "Variables and Data Types",
                    """# Variables and Data Types\n\nVariables store data you can reuse.\n\n## Common Types\n- `int` (whole numbers)\n- `float` (decimal numbers)\n- `str` (text)\n- `bool` (True/False)\n\n## Example\n```python\nname = \"Anita\"\nage = 20\npi = 3.14\nis_active = True\n```\n\nUse `type(value)` to check a variable's type.\n""",
                    2,
                ),
                (
                    "Control Flow",
                    """# Control Flow\n\nControl flow lets your program make decisions.\n\n## If-Else\n```python\nscore = 78\nif score >= 60:\n    print(\"Pass\")\nelse:\n    print(\"Retry\")\n```\n\n## Loops\n```python\nfor i in range(3):\n    print(i)\n```\n""",
                    3,
                ),
            ],
        ),
        (
            java_course,
            [
                (
                    "Introduction to Java",
                    """# Introduction to Java\n\nJava is a strongly typed, object-oriented language used in enterprise systems.\n\n## Hello World\n```java\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, Java!\");\n    }\n}\n```\n\nCompile with `javac` and run with `java`.\n""",
                    1,
                ),
                (
                    "OOP Concepts",
                    """# OOP Concepts\n\nObject-Oriented Programming focuses on classes and objects.\n\n## Core Ideas\n- Encapsulation\n- Inheritance\n- Polymorphism\n- Abstraction\n\n## Example\n```java\nclass Student {\n    String name;\n    Student(String name) { this.name = name; }\n}\n```\n""",
                    2,
                ),
                (
                    "Collections Framework",
                    """# Collections Framework\n\nCollections store groups of objects.\n\n## Common Collections\n- `ArrayList`\n- `HashMap`\n- `HashSet`\n\n## Example\n```java\nList<String> names = new ArrayList<>();\nnames.add(\"Rahul\");\n```\n""",
                    3,
                ),
            ],
        ),
        (
            web_course,
            [
                (
                    "HTML, CSS and JS Essentials",
                    """# Web Development Basics\n\nUnderstand structure (HTML), style (CSS), and behavior (JavaScript).\n\n## Core Concepts\n- Semantic HTML\n- CSS Flexbox/Grid\n- Event handling\n\n## Mini Example\n```html\n<button id=\"btn\">Click</button>\n<script>document.getElementById('btn').onclick = () => alert('Hello');</script>\n```\n""",
                    1,
                ),
            ],
        ),
        (
            dbms_course,
            [
                (
                    "Relational Database Basics",
                    """# DBMS Fundamentals\n\nDatabases store structured data efficiently.\n\n## Learn\n- Tables and keys\n- SQL queries\n- Joins and normalization\n\n## SQL Example\n```sql\nSELECT name, score FROM students ORDER BY score DESC;\n```\n""",
                    1,
                ),
            ],
        ),
        (
            cpp_course,
            [
                (
                    "C++ Fundamentals and STL",
                    """# C++ Fundamentals\n\nLearn syntax, data types, references, and the STL.\n\n## Core Topics\n- Variables and control flow\n- Functions and references\n- Vectors and maps\n\n## Example\n```cpp\n#include <vector>\nstd::vector<int> nums = {1,2,3};\n```\n""",
                    1,
                ),
            ],
        ),
        (
            os_course,
            [
                (
                    "Processes, Threads, and Scheduling",
                    """# Operating Systems Basics\n\nUnderstand how an OS manages CPU, memory, and tasks.\n\n## Key Concepts\n- Process vs thread\n- CPU scheduling\n- Deadlocks and synchronization\n\n## Quick Check\nRound Robin is a preemptive scheduling algorithm.\n""",
                    1,
                ),
            ],
        ),
    ]

    for course, lessons in lesson_specs:
        for title, content, order_index in lessons:
            exists = Lesson.query.filter_by(course_id=course.id, title=title).first()
            if exists:
                continue
            db.session.add(
                Lesson(
                    course_id=course.id,
                    title=title,
                    content=content,
                    order_index=order_index,
                )
            )
            created_any = True

    # Skills (optional for skill-based quizzes)
    python_skill = Skill.query.filter_by(skill_name="Python Basics").first()
    if not python_skill:
        python_skill = Skill(
            skill_name="Python Basics",
            description="Learn Python fundamentals and core syntax.",
        )
        db.session.add(python_skill)
        created_any = True

    web_skill = Skill.query.filter_by(skill_name="Web Development Fundamentals").first()
    if not web_skill:
        web_skill = Skill(
            skill_name="Web Development Fundamentals",
            description="Understand web basics, HTML, CSS, and HTTP.",
        )
        db.session.add(web_skill)
        created_any = True

    db.session.flush()

    # Quizzes (8-12 total, 5+ questions each)
    quiz_specs = [
        (python_course, "Python Basics Quiz 1 (XP 50)", "Python", "Easy"),
        (python_course, "Python Basics Quiz 2 (XP 75)", "Python", "Easy"),
        (python_course, "Python Basics Quiz 3 (XP 100)", "Python", "Medium"),
        (java_course, "Java Mastery Quiz 1 (XP 50)", "Java", "Easy"),
        (java_course, "Java Mastery Quiz 2 (XP 75)", "Java", "Medium"),
        (java_course, "Java Mastery Quiz 3 (XP 100)", "Java", "Medium"),
        (dsa_course, "DSA Quiz 1 (XP 75)", "DSA", "Medium"),
        (dsa_course, "DSA Quiz 2 (XP 100)", "DSA", "Medium"),
        (dsa_course, "DSA Quiz 3 (XP 150)", "DSA", "Hard"),
        (web_course, "Web Development Quiz 1 (XP 80)", "Web", "Medium"),
        (dbms_course, "DBMS Fundamentals Quiz 1 (XP 80)", "DBMS", "Medium"),
        (os_course, "Operating Systems Quiz 1 (XP 90)", "OS", "Medium"),
    ]

    quiz_map = {}
    for course, title, topic, difficulty in quiz_specs:
        quiz = Quiz.query.filter_by(title=title, course_id=course.id).first()
        if not quiz:
            quiz = Quiz(
                title=title,
                topic=topic,
                difficulty=difficulty,
                course_id=course.id,
                skill_id=python_skill.id if topic == "Python" else (web_skill.id if topic == "Web" else None),
            )
            db.session.add(quiz)
            created_any = True
        quiz_map[title] = quiz

    db.session.flush()

    question_bank = {
        "Python Basics Quiz 1 (XP 50)": [
            (
                "Which keyword defines a function in Python?",
                "func",
                "def",
                "function",
                "lambda",
                "B",
            ),
            (
                "Which data type is immutable?",
                "List",
                "Dictionary",
                "Set",
                "Tuple",
                "D",
            ),
            (
                "How do you add an item to a list named numbers?",
                "numbers.add(5)",
                "numbers.append(5)",
                "numbers.insert(5)",
                "numbers.push(5)",
                "B",
            ),
            (
                "What is the output of len('Python')?",
                "5",
                "6",
                "7",
                "None",
                "B",
            ),
            (
                "Which operator is used for exponentiation?",
                "^",
                "**",
                "//",
                "%",
                "B",
            ),
        ],
        "Python Basics Quiz 2 (XP 75)": [
            (
                "Which function converts a string to integer?",
                "str()",
                "int()",
                "float()",
                "bool()",
                "B",
            ),
            (
                "What does input() return?",
                "int",
                "float",
                "str",
                "bool",
                "C",
            ),
            (
                "Which keyword is used for loops?",
                "loop",
                "iterate",
                "for",
                "repeat",
                "C",
            ),
            (
                "What is list slicing syntax?",
                "list[start:end]",
                "list(start:end)",
                "list<start:end>",
                "list{start:end}",
                "A",
            ),
            (
                "Which statement handles exceptions?",
                "try/except",
                "catch/throw",
                "error/handle",
                "safe/guard",
                "A",
            ),
        ],
        "Python Basics Quiz 3 (XP 100)": [
            (
                "What is a dictionary in Python?",
                "Ordered list",
                "Key-value store",
                "Tuple",
                "Set",
                "B",
            ),
            (
                "Which method adds a key to dict?",
                "dict.add()",
                "dict.insert()",
                "dict[key] = value",
                "dict.push()",
                "C",
            ),
            (
                "What does enumerate() return?",
                "Only values",
                "Index and value",
                "Keys only",
                "None",
                "B",
            ),
            (
                "Which loop is best for known count?",
                "while",
                "for",
                "do-while",
                "repeat",
                "B",
            ),
            (
                "What does break do?",
                "Skips current iteration",
                "Stops the loop",
                "Restarts the loop",
                "Ends program",
                "B",
            ),
        ],
        "Java Mastery Quiz 1 (XP 50)": [
            (
                "Which method is the entry point of a Java program?",
                "start()",
                "main()",
                "run()",
                "init()",
                "B",
            ),
            (
                "Java is a ____ typed language.",
                "dynamically",
                "strongly",
                "weakly",
                "loosely",
                "B",
            ),
            (
                "Which keyword creates an object?",
                "make",
                "new",
                "create",
                "class",
                "B",
            ),
            (
                "Which data type stores whole numbers?",
                "float",
                "double",
                "int",
                "char",
                "C",
            ),
            (
                "Which operator is used for equality?",
                "=",
                "==",
                "===",
                "equals",
                "B",
            ),
        ],
        "Java Mastery Quiz 2 (XP 75)": [
            (
                "Which OOP concept allows method overriding?",
                "Encapsulation",
                "Inheritance",
                "Polymorphism",
                "Abstraction",
                "C",
            ),
            (
                "Which access modifier is most restrictive?",
                "public",
                "protected",
                "private",
                "default",
                "C",
            ),
            (
                "Which keyword prevents inheritance?",
                "final",
                "static",
                "sealed",
                "stop",
                "A",
            ),
            (
                "What does 'this' refer to?",
                "Parent class",
                "Current object",
                "Static context",
                "Package",
                "B",
            ),
            (
                "Which is an interface keyword?",
                "interface",
                "implements",
                "extends",
                "class",
                "A",
            ),
        ],
        "Java Mastery Quiz 3 (XP 100)": [
            (
                "Which collection allows duplicates?",
                "Set",
                "Map",
                "List",
                "Queue",
                "C",
            ),
            (
                "Which class is a Map implementation?",
                "ArrayList",
                "HashMap",
                "HashSet",
                "LinkedList",
                "B",
            ),
            (
                "Which loop checks condition first?",
                "do-while",
                "while",
                "for-each",
                "repeat",
                "B",
            ),
            (
                "Which keyword handles exceptions?",
                "catch",
                "throws",
                "try",
                "error",
                "C",
            ),
            (
                "Which package has ArrayList?",
                "java.util",
                "java.io",
                "java.lang",
                "java.net",
                "A",
            ),
        ],
        "DSA Quiz 1 (XP 75)": [
            (
                "Which data structure uses FIFO?",
                "Stack",
                "Queue",
                "Tree",
                "Graph",
                "B",
            ),
            (
                "Which data structure uses LIFO?",
                "Queue",
                "Stack",
                "Heap",
                "Graph",
                "B",
            ),
            (
                "Binary search requires the array to be:",
                "Unsorted",
                "Sorted",
                "Random",
                "Rotated",
                "B",
            ),
            (
                "Time complexity of binary search:",
                "O(n)",
                "O(log n)",
                "O(n log n)",
                "O(1)",
                "B",
            ),
            (
                "Which structure is best for BFS?",
                "Stack",
                "Queue",
                "List",
                "Heap",
                "B",
            ),
        ],
        "DSA Quiz 2 (XP 100)": [
            (
                "Which algorithm is used for shortest path (no negatives)?",
                "Dijkstra",
                "Kruskal",
                "Prim",
                "DFS",
                "A",
            ),
            (
                "What is the height of a balanced BST?",
                "O(n)",
                "O(log n)",
                "O(n log n)",
                "O(1)",
                "B",
            ),
            (
                "Which data structure supports priority?",
                "Queue",
                "Stack",
                "Heap",
                "Array",
                "C",
            ),
            (
                "Merge sort complexity:",
                "O(n^2)",
                "O(n log n)",
                "O(log n)",
                "O(n)",
                "B",
            ),
            (
                "Quick sort average complexity:",
                "O(n^2)",
                "O(n log n)",
                "O(log n)",
                "O(n)",
                "B",
            ),
        ],
        "DSA Quiz 3 (XP 150)": [
            (
                "Which algorithm detects negative cycles?",
                "Dijkstra",
                "Bellman-Ford",
                "Prim",
                "BFS",
                "B",
            ),
            (
                "Which tree is self-balancing?",
                "AVL",
                "Binary",
                "N-ary",
                "Trie",
                "A",
            ),
            (
                "Which graph traversal uses recursion?",
                "DFS",
                "BFS",
                "Dijkstra",
                "Prim",
                "A",
            ),
            (
                "Which structure is used in recursion?",
                "Queue",
                "Stack",
                "Heap",
                "Array",
                "B",
            ),
            (
                "Which is a divide-and-conquer algorithm?",
                "Bubble sort",
                "Merge sort",
                "Insertion sort",
                "Selection sort",
                "B",
            ),
        ],
        "Web Development Quiz 1 (XP 80)": [
            (
                "Which HTML tag is used for hyperlinks?",
                "<link>",
                "<a>",
                "<href>",
                "<url>",
                "B",
            ),
            (
                "Which CSS property controls text color?",
                "font-color",
                "text-style",
                "color",
                "text-color",
                "C",
            ),
            (
                "Which HTTP method is commonly used to create resources?",
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "B",
            ),
            (
                "In JavaScript, which keyword declares a block-scoped variable?",
                "var",
                "const",
                "both let and const",
                "define",
                "C",
            ),
            (
                "Which status code indicates success?",
                "404",
                "500",
                "301",
                "200",
                "D",
            ),
        ],
        "DBMS Fundamentals Quiz 1 (XP 80)": [
            (
                "Which normal form removes partial dependency?",
                "1NF",
                "2NF",
                "3NF",
                "BCNF",
                "B",
            ),
            (
                "Which SQL clause is used to filter grouped results?",
                "WHERE",
                "GROUP BY",
                "HAVING",
                "ORDER BY",
                "C",
            ),
            (
                "Which join returns all records from both tables?",
                "INNER JOIN",
                "LEFT JOIN",
                "RIGHT JOIN",
                "FULL OUTER JOIN",
                "D",
            ),
            (
                "ACID property that ensures all-or-nothing is:",
                "Consistency",
                "Atomicity",
                "Isolation",
                "Durability",
                "B",
            ),
            (
                "Which index type is commonly used in MySQL for primary keys?",
                "Hash",
                "B-Tree",
                "Bitmap",
                "R-Tree",
                "B",
            ),
        ],
        "Operating Systems Quiz 1 (XP 90)": [
            (
                "Which scheduling algorithm uses time slices?",
                "FCFS",
                "SJF",
                "Round Robin",
                "Priority Non-preemptive",
                "C",
            ),
            (
                "A deadlock requires all of the following except:",
                "Mutual exclusion",
                "Hold and wait",
                "Preemption",
                "Circular wait",
                "C",
            ),
            (
                "Virtual memory is primarily managed using:",
                "Registers",
                "Paging",
                "Compiler",
                "Stack only",
                "B",
            ),
            (
                "Which state represents a process waiting for I/O?",
                "Running",
                "Ready",
                "Blocked",
                "Terminated",
                "C",
            ),
            (
                "Context switch means:",
                "Switching monitor",
                "Switching from kernel to user mode only",
                "Saving and restoring CPU state between processes",
                "Formatting memory",
                "C",
            ),
        ],
    }

    for quiz_title, questions in question_bank.items():
        quiz = quiz_map.get(quiz_title)
        if not quiz:
            continue
        existing = Question.query.filter_by(quiz_id=quiz.id).first()
        if existing:
            continue
        for text, a, b, c, d, correct in questions:
            db.session.add(
                Question(
                    quiz_id=quiz.id,
                    question_text=text,
                    option_a=a,
                    option_b=b,
                    option_c=c,
                    option_d=d,
                    correct_option=correct,
                )
            )
        created_any = True

    # Problem bank (23 total, distributed as Easy 10 / Medium 8 / Hard 5)
    problem_specs = [
        # Easy (10)
        (
            "Reverse a String",
            "Easy",
            ["strings", "basics"],
            "Given a string, return the reversed string.",
            "Input contains lowercase alphabetic characters.",
            "hello",
            "olleh",
            priya,
            [("hello", "olleh", False), ("platform", "mroftalp", True)],
        ),
        (
            "Check Palindrome",
            "Easy",
            ["strings", "two-pointers"],
            "Check if the given string reads the same forward and backward.",
            "String length <= 10^4.",
            "level",
            "true",
            john,
            [("level", "true", False), ("coding", "false", True)],
        ),
        (
            "Two Sum",
            "Easy",
            ["arrays", "hash-map"],
            "Find two indices whose values sum to target.",
            "Exactly one valid answer exists.",
            "[2,7,11,15],9",
            "[0,1]",
            priya,
            [("[2,7,11,15],9", "[0,1]", False), ("[3,2,4],6", "[1,2]", True)],
        ),
        (
            "Fibonacci Series",
            "Easy",
            ["math", "dp"],
            "Return the nth Fibonacci number (0-indexed).",
            "0 <= n <= 30.",
            "7",
            "13",
            john,
            [("7", "13", False), ("10", "55", True)],
        ),
        (
            "Merge Sorted Arrays",
            "Easy",
            ["arrays", "two-pointers"],
            "Merge two sorted arrays into one sorted array.",
            "Both input arrays are sorted in non-decreasing order.",
            "[1,3,5],[2,4,6]",
            "[1,2,3,4,5,6]",
            priya,
            [("[1,3,5],[2,4,6]", "[1,2,3,4,5,6]", False), ("[1],[2]", "[1,2]", True)],
        ),
        (
            "Valid Parentheses",
            "Easy",
            ["stack", "strings"],
            "Validate whether parentheses in the string are balanced.",
            "Input contains only ()[]{} characters.",
            "()[]{}",
            "true",
            john,
            [("()[]{}", "true", False), ("([)]", "false", True)],
        ),
        (
            "FizzBuzz",
            "Easy",
            ["math", "simulation"],
            "Print numbers from 1..n using Fizz/Buzz rules.",
            "n <= 100.",
            "5",
            "1,2,Fizz,4,Buzz",
            priya,
            [("5", "1,2,Fizz,4,Buzz", False), ("3", "1,2,Fizz", True)],
        ),
        (
            "Anagram Check",
            "Easy",
            ["strings", "hash-map"],
            "Determine whether two strings are anagrams.",
            "Strings contain lowercase letters.",
            "listen,silent",
            "true",
            john,
            [("listen,silent", "true", False), ("rat,car", "false", True)],
        ),
        (
            "Climbing Stairs",
            "Easy",
            ["dp"],
            "Count distinct ways to climb n stairs using 1 or 2 steps.",
            "1 <= n <= 45.",
            "5",
            "8",
            priya,
            [("5", "8", False), ("3", "3", True)],
        ),
        (
            "Binary Search",
            "Easy",
            ["arrays", "binary-search"],
            "Return index of target in sorted array, else -1.",
            "Array is sorted ascending.",
            "[-1,0,3,5,9,12],9",
            "4",
            john,
            [("[-1,0,3,5,9,12],9", "4", False), ("[-1,0,3,5,9,12],2", "-1", True)],
        ),

        # Medium (8)
        (
            "Longest Substring Without Repeating Characters",
            "Medium",
            ["strings", "sliding-window"],
            "Find length of longest substring without duplicate characters.",
            "String length <= 5 * 10^4.",
            "abcabcbb",
            "3",
            priya,
            [("abcabcbb", "3", False), ("bbbbb", "1", True)],
        ),
        (
            "Maximum Subarray",
            "Medium",
            ["arrays", "kadane"],
            "Find contiguous subarray with maximum sum.",
            "Array length <= 10^5.",
            "[-2,1,-3,4,-1,2,1,-5,4]",
            "6",
            john,
            [("[-2,1,-3,4,-1,2,1,-5,4]", "6", False), ("[1]", "1", True)],
        ),
        (
            "Top K Frequent Elements",
            "Medium",
            ["heap", "hash-map"],
            "Return k most frequent elements from array.",
            "k is always valid.",
            "[1,1,1,2,2,3],2",
            "[1,2]",
            priya,
            [("[1,1,1,2,2,3],2", "[1,2]", False), ("[4,4,4,6,6,7],1", "[4]", True)],
        ),
        (
            "Kth Largest Element in Array",
            "Medium",
            ["heap", "quickselect"],
            "Find kth largest element in an unsorted array.",
            "1 <= k <= array length.",
            "[3,2,1,5,6,4],2",
            "5",
            john,
            [("[3,2,1,5,6,4],2", "5", False), ("[3,2,3,1,2,4,5,5,6],4", "4", True)],
        ),
        (
            "Course Schedule",
            "Medium",
            ["graphs", "topological-sort"],
            "Determine if all courses can be finished from prerequisites.",
            "Use cycle detection in directed graph.",
            "2,[[1,0]]",
            "true",
            priya,
            [("2,[[1,0]]", "true", False), ("2,[[1,0],[0,1]]", "false", True)],
        ),
        (
            "Binary Tree Level Order Traversal",
            "Medium",
            ["trees", "bfs"],
            "Return nodes level by level from left to right.",
            "Use queue-based traversal.",
            "[3,9,20,null,null,15,7]",
            "[[3],[9,20],[15,7]]",
            john,
            [("[3,9,20,null,null,15,7]", "[[3],[9,20],[15,7]]", False)],
        ),
        (
            "Rotate Matrix",
            "Medium",
            ["matrix", "arrays"],
            "Rotate n x n matrix by 90 degrees clockwise.",
            "In-place or equivalent transformed output.",
            "[[1,2,3],[4,5,6],[7,8,9]]",
            "[[7,4,1],[8,5,2],[9,6,3]]",
            priya,
            [("[[1,2,3],[4,5,6],[7,8,9]]", "[[7,4,1],[8,5,2],[9,6,3]]", False)],
        ),
        (
            "Longest Increasing Subsequence",
            "Medium",
            ["dp", "binary-search"],
            "Compute length of longest strictly increasing subsequence.",
            "Array length <= 2500.",
            "[10,9,2,5,3,7,101,18]",
            "4",
            john,
            [("[10,9,2,5,3,7,101,18]", "4", False), ("[0,1,0,3,2,3]", "4", True)],
        ),

        # Hard (5)
        (
            "LRU Cache",
            "Hard",
            ["design", "hash-map", "linked-list"],
            "Implement LRU cache supporting O(1) get and put.",
            "Capacity is positive.",
            "capacity=2,put(1,1),put(2,2),get(1)",
            "1",
            priya,
            [("capacity=2,put(1,1),put(2,2),get(1)", "1", False)],
        ),
        (
            "Median of Two Sorted Arrays",
            "Hard",
            ["arrays", "binary-search"],
            "Find median of two sorted arrays in logarithmic time.",
            "Combined length >= 1.",
            "[1,3],[2]",
            "2.0",
            john,
            [("[1,3],[2]", "2.0", False), ("[1,2],[3,4]", "2.5", True)],
        ),
        (
            "N-Queens",
            "Hard",
            ["backtracking"],
            "Count valid ways to place n queens on n x n board.",
            "1 <= n <= 9.",
            "4",
            "2",
            priya,
            [("4", "2", False), ("1", "1", True)],
        ),
        (
            "Merge K Sorted Lists",
            "Hard",
            ["heap", "linked-list"],
            "Merge k sorted linked lists into one sorted list.",
            "Total nodes can be up to 10^4.",
            "[[1,4,5],[1,3,4],[2,6]]",
            "[1,1,2,3,4,4,5,6]",
            john,
            [("[[1,4,5],[1,3,4],[2,6]]", "[1,1,2,3,4,4,5,6]", False)],
        ),
        (
            "Trapping Rain Water",
            "Hard",
            ["arrays", "two-pointers"],
            "Compute total rainwater trapped between bars.",
            "Heights are non-negative integers.",
            "[0,1,0,2,1,0,1,3,2,1,2,1]",
            "6",
            priya,
            [("[0,1,0,2,1,0,1,3,2,1,2,1]", "6", False), ("[4,2,0,3,2,5]", "9", True)],
        ),
    ]

    for title, difficulty, tags, description, constraints, example_input, example_output, creator, tests in problem_specs:
        problem = Problem.query.filter_by(title=title).first()
        if not problem:
            problem = Problem(
                title=title,
                difficulty=difficulty,
                tags=tags,
                description=description,
                constraints=constraints,
                example_input=example_input,
                example_output=example_output,
                created_by=creator.id,
            )
            db.session.add(problem)
            db.session.flush()
            created_any = True

        existing_test = ProblemTestCase.query.filter_by(problem_id=problem.id).first()
        if not existing_test:
            for input_data, expected_output, hidden in tests:
                db.session.add(
                    ProblemTestCase(
                        problem_id=problem.id,
                        input_data=input_data,
                        expected_output=expected_output,
                        is_hidden=hidden,
                    )
                )
            created_any = True

    # Course-linked coding problems
    coding_specs = [
        (
            python_course,
            "Reverse a String",
            "Easy",
            ["strings"],
            """Reverse a given string.\n\nStarter Code (Python):\n```python\ndef reverse_string(text):\n    # TODO: return the reversed string\n    pass\n```\n""",
            "hello",
            "olleh",
            priya,
        ),
        (
            python_course,
            "Check Prime Number",
            "Easy",
            ["math"],
            """Check if the given number is prime.\n\nStarter Code (Python):\n```python\ndef is_prime(n):\n    # TODO: return True if prime, else False\n    pass\n```\n""",
            "11",
            "True",
            priya,
        ),
        (
            java_course,
            "Palindrome Check",
            "Easy",
            ["strings"],
            """Check if a string is a palindrome.\n\nStarter Code (Java):\n```java\npublic static boolean isPalindrome(String text) {\n    // TODO: return true if palindrome\n    return false;\n}\n```\n""",
            "level",
            "true",
            john,
        ),
        (
            java_course,
            "Factorial",
            "Easy",
            ["math"],
            """Compute factorial of a number.\n\nStarter Code (Java):\n```java\npublic static int factorial(int n) {\n    // TODO: compute factorial\n    return 1;\n}\n```\n""",
            "5",
            "120",
            john,
        ),
    ]

    for course, title, difficulty, tags, description, example_input, example_output, creator in coding_specs:
        coding_problem = CodingProblem.query.filter_by(title=title, course_id=course.id).first()
        if coding_problem:
            continue
        db.session.add(
            CodingProblem(
                course_id=course.id,
                title=title,
                difficulty=difficulty,
                tags=tags,
                description=description,
                example_input=example_input,
                example_output=example_output,
                created_by=creator.id,
            )
        )
        created_any = True

    # Rewards and badges (gamification)
    _get_or_create_reward(
        "Quiz Explorer",
        {"description": "Complete 3 quizzes", "xp_required": 150},
    )
    _get_or_create_reward(
        "Course Finisher",
        {"description": "Complete a course", "xp_required": 400},
    )
    _get_or_create_reward(
        "Streak Keeper",
        {"description": "Maintain a 5-day streak", "xp_required": 250},
    )

    _get_or_create_badge(
        "Beginner Solver",
        {"description": "Solve your first coding problem", "rule_type": "problems_solved", "rule_value": 1},
    )
    _get_or_create_badge(
        "Python Master",
        {"description": "Complete all Python basics quizzes", "rule_type": "quiz_count", "rule_value": 3},
    )
    _get_or_create_badge(
        "5-Day Streak",
        {"description": "Log in and learn 5 days in a row", "rule_type": "streak_days", "rule_value": 5},
    )

    if created_any:
        db.session.commit()


def _delete_records(records):
    count = 0
    for record in records:
        db.session.delete(record)
        count += 1
    return count


def reseed_demo_data():
    """Delete known demo records and seed a fresh demo dataset."""
    summary = {
        "quizzes_removed": 0,
        "courses_removed": 0,
        "problems_removed": 0,
        "coding_problems_removed": 0,
        "skills_removed": 0,
        "badges_removed": 0,
        "rewards_removed": 0,
        "users_removed": 0,
    }

    try:
        demo_quiz_ids = [
            quiz_id for (quiz_id,) in db.session.query(Quiz.id).filter(Quiz.title.in_(DEMO_QUIZ_TITLES)).all()
        ]
        if demo_quiz_ids:
            Progress.query.filter(Progress.quiz_id.in_(demo_quiz_ids)).delete(synchronize_session=False)
            Submission.query.filter(Submission.quiz_id.in_(demo_quiz_ids)).delete(synchronize_session=False)
            QuizAttempt.query.filter(QuizAttempt.quiz_id.in_(demo_quiz_ids)).delete(synchronize_session=False)
            DailyChallenge.query.filter(DailyChallenge.quiz_id.in_(demo_quiz_ids)).delete(synchronize_session=False)
            Question.query.filter(Question.quiz_id.in_(demo_quiz_ids)).delete(synchronize_session=False)
            summary["quizzes_removed"] = Quiz.query.filter(Quiz.id.in_(demo_quiz_ids)).delete(synchronize_session=False)

        demo_problem_ids = [
            problem_id for (problem_id,) in db.session.query(Problem.id).filter(Problem.title.in_(DEMO_PROBLEM_TITLES)).all()
        ]
        if demo_problem_ids:
            ProblemTestCase.query.filter(ProblemTestCase.problem_id.in_(demo_problem_ids)).delete(synchronize_session=False)
            ProblemProgress.query.filter(ProblemProgress.problem_id.in_(demo_problem_ids)).delete(synchronize_session=False)
            CodeSubmission.query.filter(CodeSubmission.problem_id.in_(demo_problem_ids)).delete(synchronize_session=False)
            summary["problems_removed"] = Problem.query.filter(Problem.id.in_(demo_problem_ids)).delete(synchronize_session=False)

        demo_course_ids = [
            course_id for (course_id,) in db.session.query(Course.id).filter(Course.title.in_(DEMO_COURSE_TITLES)).all()
        ]
        if demo_course_ids:
            LessonProgress.query.filter(LessonProgress.course_id.in_(demo_course_ids)).delete(synchronize_session=False)
            Enrollment.query.filter(Enrollment.course_id.in_(demo_course_ids)).delete(synchronize_session=False)
            Note.query.filter(Note.course_id.in_(demo_course_ids)).delete(synchronize_session=False)
            Lesson.query.filter(Lesson.course_id.in_(demo_course_ids)).delete(synchronize_session=False)
            summary["coding_problems_removed"] = CodingProblem.query.filter(
                CodingProblem.course_id.in_(demo_course_ids)
            ).delete(synchronize_session=False)
            summary["courses_removed"] = Course.query.filter(Course.id.in_(demo_course_ids)).delete(synchronize_session=False)

        demo_skill_ids = [
            skill_id for (skill_id,) in db.session.query(Skill.id).filter(Skill.skill_name.in_(DEMO_SKILLS)).all()
        ]
        if demo_skill_ids:
            UserSkill.query.filter(UserSkill.skill_id.in_(demo_skill_ids)).delete(synchronize_session=False)
            summary["skills_removed"] = Skill.query.filter(Skill.id.in_(demo_skill_ids)).delete(synchronize_session=False)

        demo_badge_ids = [
            badge_id for (badge_id,) in db.session.query(Badge.id).filter(Badge.name.in_(DEMO_BADGES)).all()
        ]
        if demo_badge_ids:
            UserBadge.query.filter(UserBadge.badge_id.in_(demo_badge_ids)).delete(synchronize_session=False)
            summary["badges_removed"] = Badge.query.filter(Badge.id.in_(demo_badge_ids)).delete(synchronize_session=False)

        demo_reward_ids = [
            reward_id for (reward_id,) in db.session.query(Reward.id).filter(Reward.badge_name.in_(DEMO_REWARDS)).all()
        ]
        if demo_reward_ids:
            UserReward.query.filter(UserReward.reward_id.in_(demo_reward_ids)).delete(synchronize_session=False)
            summary["rewards_removed"] = Reward.query.filter(Reward.id.in_(demo_reward_ids)).delete(synchronize_session=False)

        # Keep demo users to preserve auth/session and avoid deleting unrelated user activity.
        summary["users_removed"] = 0

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    seed_quiz_data()
    return summary
