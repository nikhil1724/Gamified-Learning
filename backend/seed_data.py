from werkzeug.security import generate_password_hash

from database import db
from models import (
    Badge,
    CodingProblem,
    Course,
    Lesson,
    Problem,
    ProblemTestCase,
    Question,
    Quiz,
    Reward,
    Skill,
    User,
)


DEMO_PASSWORD = "Demo@123"
DEMO_PASSWORD_HASH = generate_password_hash(DEMO_PASSWORD)


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

    # Courses (difficulty/category stored in description since schema lacks fields)
    python_course, created = _get_or_create_course(
        "Python Programming Basics",
        {
            "description": (
                "Learn core Python syntax, data types, and control flow.\n"
                "Difficulty: Beginner | Category: Programming"
            ),
            "teacher_id": priya.id,
        },
    )
    created_any = created_any or created

    java_course, created = _get_or_create_course(
        "Java Programming Mastery",
        {
            "description": (
                "Build strong Java fundamentals with OOP and collections.\n"
                "Difficulty: Intermediate | Category: Programming"
            ),
            "teacher_id": john.id,
        },
    )
    created_any = created_any or created

    dsa_course, created = _get_or_create_course(
        "Data Structures & Algorithms",
        {
            "description": (
                "Practice core data structures and algorithmic thinking.\n"
                "Difficulty: Advanced | Category: Computer Science"
            ),
            "teacher_id": john.id,
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

    # Quizzes (3 per course, 5 questions each)
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
                skill_id=python_skill.id if topic == "Python" else None,
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

    # Problem bank (used by coding engine)
    problem_specs = [
        (
            "Reverse a String",
            "Easy",
            ["strings", "basics"],
            "Write a program that reverses a given string.",
            "Input: A single string.",
            "hello",
            "olleh",
            priya,
            [
                ("hello", "olleh", False),
                ("python", "nohtyp", True),
            ],
        ),
        (
            "Check Prime Number",
            "Easy",
            ["math", "loops"],
            "Determine if a number is prime.",
            "Input: An integer n (n > 1).",
            "11",
            "Prime",
            priya,
            [
                ("11", "Prime", False),
                ("12", "Not Prime", True),
            ],
        ),
        (
            "Palindrome Check",
            "Easy",
            ["strings"],
            "Check whether a string is a palindrome.",
            "Input: A single string.",
            "level",
            "Palindrome",
            john,
            [
                ("level", "Palindrome", False),
                ("world", "Not Palindrome", True),
            ],
        ),
        (
            "Factorial",
            "Easy",
            ["math"],
            "Compute the factorial of a non-negative integer.",
            "Input: An integer n (0 <= n <= 12).",
            "5",
            "120",
            john,
            [
                ("5", "120", False),
                ("0", "1", True),
            ],
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
