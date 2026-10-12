// Blockwise Studio lessons. Each lesson's `solution` is a valid blockwise-plan-v1 plan
// (tests/test_studio.py checks that it compiles). `starter` is the guided, partly
// pre-filled version; "blank" mode keeps only the files and function signatures.
// `tests` are real calls run against the learner's code ("Run tests"); the test suite runs
// them against every solution. Each test has `call` plus `expect` (a Python value) or `raises`.
// Every entry in `concepts` must exist in the Studio glossary. `learn` (explanations) and `example`
// (code plus notes keyed by line number) form the "Learn it first" section; `vocab` is optional.
// A test can also be `run` + `argv` + `stdout`: run the file as a program and compare its output.
window.BLOCKWISE_LESSONS = [
 {
  "id": "anatomy",
  "title": "0 · Anatomy of a Python file",
  "level": "Start here",
  "minutes": 8,
  "goal": "Learn the parts of a .py file and the words people use for them, then finish one small function.",
  "concepts": [
   "def",
   "parameter",
   "type hint",
   "indentation",
   "docstring",
   "return"
  ],
  "learn": [
   {
    "title": "A .py file is read from top to bottom",
    "text": "Python reads a file line by line, from the top. Most files follow the same order: a docstring that says what the file is for, then imports, then constants, then functions, and last, a main block that runs when you start the file. Blockwise builds files in exactly that order."
   },
   {
    "title": "Indentation is part of the language",
    "text": "A line that ends with a colon (:) starts a block, and the lines that belong to it are indented by 4 spaces. When the indentation ends, the block ends. In other languages braces { } do this job; in Python the spaces do. Blockwise handles the spaces for you: each block nested inside another is one level deeper."
   },
   {
    "title": "Functions are where the work happens",
    "text": "def creates a function: a named recipe you can run again and again. Its first line, the signature, gives the name, the inputs (parameters) and what it gives back. The indented lines below are its body. Nothing in the body runs until something calls the function by name, like price_with_tax(10)."
   }
  ],
  "example": {
   "caption": "A whole file, part by part",
   "code": "\"\"\"Shop helpers: prices and totals.\"\"\"\nimport math\n\nTAX_RATE = 0.2\n\n\ndef price_with_tax(price: float, rate: float = TAX_RATE) -> float:\n    \"\"\"Return the price including tax.\"\"\"\n    total = price * (1 + rate)  # a variable holds a value\n    return round(total, 2)\n\n\ndef cheapest(prices: list) -> float:\n    if not prices:\n        raise ValueError('no prices')\n    return min(prices)\n\n\nif __name__ == '__main__':\n    print(price_with_tax(10))",
   "notes": {
    "1": "Docstring: a string at the very top that explains the file. Python keeps it as documentation.",
    "2": "import: brings in code from another module. math is part of Python's standard library.",
    "4": "Constant: a value set once, written in CAPITALS so readers know not to change it.",
    "7": "def line (signature): def, the name, the parameters in brackets with type hints, a default value (= TAX_RATE), -> and the return type, then a colon.",
    "8": "The function's own docstring: says what it does.",
    "9": "Variable: total now names the computed value. # starts a comment, which Python ignores.",
    "10": "return hands the value back to the caller and ends the function.",
    "14": "if checks a condition; raise stops with an error when the input makes no sense.",
    "19": "Main block: runs only when you start this file directly (python shop.py), not when another file imports it.",
    "20": "A call: price_with_tax(10) runs the function with price = 10; print shows the result."
   }
  },
  "vocab": [
   [
    "def",
    "The keyword that starts a function definition."
   ],
   [
    "function",
    "A named block of code you can call. It can take inputs and give back a result."
   ],
   [
    "parameter",
    "A name in the def line's brackets: the input the function expects (price)."
   ],
   [
    "argument",
    "The actual value you pass when you call it: in price_with_tax(10), 10 is the argument."
   ],
   [
    "type hint",
    "The : float after a parameter and -> float after the brackets. They say what kind of value is expected. Python doesn't enforce them, but they help readers and tools."
   ],
   [
    "colon and indentation",
    "A colon ends a line that opens a block; the block's lines are indented 4 spaces."
   ],
   [
    "return",
    "Gives a value back to whoever called the function, and leaves the function."
   ],
   [
    "None",
    "Python's value for 'nothing'. A function without a return gives back None."
   ],
   [
    "variable",
    "A name that points at a value: total = 0."
   ],
   [
    "= and ==",
    "One = stores a value (total = 0). Two == asks whether two values are equal (total == 0)."
   ],
   [
    "call",
    "Running a function by writing its name and brackets: cheapest([3, 1])."
   ],
   [
    "docstring",
    "A string right after a def line or at the top of a file that explains it."
   ],
   [
    "comment",
    "Text after # on a line. Python ignores it; it's a note for people."
   ],
   [
    "import / module",
    "A module is a .py file. import makes another module's code usable in this one."
   ]
  ],
  "steps": [
   {
    "title": "Take the tour",
    "text": "Read the annotated file above, line by line. Then open the Words tab for any word you're unsure of."
   },
   {
    "title": "Name the parts",
    "text": "Look at area's def line in the builder: the name is area, the parameters are width and height (both int), and it returns an int."
   },
   {
    "title": "Write the body",
    "text": "Delete the TODO block (✕), then add a Return block with width * height. The Python tab shows it indented inside the function."
   },
   {
    "title": "Check and run",
    "text": "Press Check my work, then Run tests. Try your own call in the Python tab too, like area(7, 3)."
   }
  ],
  "explain": "You just read a whole Python file and wrote a function body. Every lesson after this one adds a new kind of block, and every one lands in the same file structure you saw here.",
  "tests": [
   {
    "call": "area(2, 3)",
    "expect": "6"
   },
   {
    "call": "area(5, 1)",
    "expect": "5"
   },
   {
    "call": "area(0, 9)",
    "expect": "0"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Area",
   "modules": [
    {
     "path": "shapes.py",
     "imports": [],
     "functions": [
      {
       "name": "area",
       "parameters": [
        {
         "name": "width",
         "type": "int"
        },
        {
         "name": "height",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "Return the area of a rectangle."
       ],
       "body": [
        {
         "kind": "hole",
         "label": "Give back width times height",
         "allowed_calls": []
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Area",
   "modules": [
    {
     "path": "shapes.py",
     "imports": [],
     "functions": [
      {
       "name": "area",
       "parameters": [
        {
         "name": "width",
         "type": "int"
        },
        {
         "name": "height",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "Return the area of a rectangle."
       ],
       "body": [
        {
         "kind": "return",
         "expression": "width * height"
        }
       ]
      }
     ]
    }
   ]
  }
 },
 {
  "id": "first-function",
  "title": "1 · Your first function",
  "level": "Beginner",
  "minutes": 5,
  "goal": "Write a function that takes a name and gives back a greeting.",
  "concepts": [
   "function",
   "parameter",
   "return",
   "string"
  ],
  "steps": [
   {
    "title": "Look at the function card",
    "text": "A function is a named recipe. This one is called greet and takes one input (a parameter) called name of type str (text)."
   },
   {
    "title": "Add a Return block",
    "text": "Click '+ add a block' inside greet and choose Return. A return hands a value back to whoever called the function."
   },
   {
    "title": "Fill in what to return",
    "text": "Type f'Hello, {name}!' in the Return block. The f before the quotes lets you drop the name into the text."
   },
   {
    "title": "Check, then run it",
    "text": "Press Check my work, then Run tests to call greet for real. The Python tab shows exactly what you built."
   }
  ],
  "explain": "Every function has a name, inputs in brackets, and usually a return. greet('Ana') now gives back 'Hello, Ana!'.",
  "tests": [
   {
    "call": "greet('Ana')",
    "expect": "'Hello, Ana!'"
   },
   {
    "call": "greet('Sam')",
    "expect": "'Hello, Sam!'"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Greeting",
   "modules": [
    {
     "path": "greetings.py",
     "imports": [],
     "functions": [
      {
       "name": "greet",
       "parameters": [
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "str",
       "requirements": [
        "Give back a friendly greeting that uses the name."
       ],
       "body": []
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Greeting",
   "modules": [
    {
     "path": "greetings.py",
     "imports": [],
     "functions": [
      {
       "name": "greet",
       "parameters": [
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "str",
       "requirements": [
        "Give back a friendly greeting that uses the name."
       ],
       "body": [
        {
         "kind": "return",
         "expression": "f'Hello, {name}!'"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Defining is not running",
    "text": "A def only teaches Python a new recipe. The body runs later, each time something calls the function. That's why the Python tab shows the code, but nothing happens until you call greet('Ana') in Try it."
   },
   {
    "title": "Parameters are placeholders",
    "text": "Inside greet, name stands for whatever value the caller passes. Call greet('Ana') and name is 'Ana'; call greet('Sam') and it's 'Sam'. The same body works for both."
   }
  ],
  "example": {
   "caption": "Calling a function twice",
   "code": "def greet(name: str) -> str:\n    return f'Hello, {name}!'\n\n\nprint(greet('Ana'))\nprint(greet('Sam'))",
   "notes": {
    "1": "The signature: name, one parameter (name, a str), and the return type str.",
    "2": "f-string: {name} is replaced by the value of name.",
    "5": "Each call runs the body again with a different name."
   }
  }
 },
 {
  "id": "if-else",
  "title": "2 · Make a decision with If / Else",
  "level": "Beginner",
  "minutes": 8,
  "goal": "Decide if someone can vote: True for 18 and over, otherwise False.",
  "concepts": [
   "if / else",
   "condition",
   "boolean"
  ],
  "steps": [
   {
    "title": "Add an If block",
    "text": "Inside can_vote, add an If / Else block. Its condition is a question with a yes/no answer. Type age >= 18."
   },
   {
    "title": "Fill the 'if' side",
    "text": "Inside the if part, add Return with True. This runs only when the condition is true."
   },
   {
    "title": "Fill the 'else' side",
    "text": "Inside the else part, add Return with False. This runs when the condition is false."
   },
   {
    "title": "Check, then compare",
    "text": "Check your work. Notice the boundary: 18 counts, because >= means 'greater than or equal'. Run tests tries 17, 18 and 40."
   }
  ],
  "explain": "If / Else splits your program into two paths. Getting the boundary right (>= versus >) is one of the most common bugs in real code.",
  "tests": [
   {
    "call": "can_vote(18)",
    "expect": "True"
   },
   {
    "call": "can_vote(17)",
    "expect": "False"
   },
   {
    "call": "can_vote(40)",
    "expect": "True"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Voting age",
   "modules": [
    {
     "path": "voting.py",
     "imports": [],
     "functions": [
      {
       "name": "can_vote",
       "parameters": [
        {
         "name": "age",
         "type": "int"
        }
       ],
       "returns": "bool",
       "requirements": [
        "True for age 18 and over, else False."
       ],
       "body": [
        {
         "kind": "branch",
         "condition": "age >= 18",
         "body": [],
         "otherwise": []
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Voting age",
   "modules": [
    {
     "path": "voting.py",
     "imports": [],
     "functions": [
      {
       "name": "can_vote",
       "parameters": [
        {
         "name": "age",
         "type": "int"
        }
       ],
       "returns": "bool",
       "requirements": [
        "True for age 18 and over, else False."
       ],
       "body": [
        {
         "kind": "branch",
         "condition": "age >= 18",
         "body": [
          {
           "kind": "return",
           "expression": "True"
          }
         ],
         "otherwise": [
          {
           "kind": "return",
           "expression": "False"
          }
         ]
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Conditions are questions",
    "text": "The text after if is a condition: Python works it out to True or False. Comparisons such as >=, <, == and != are the usual way to ask."
   },
   {
    "title": "Exactly one side runs",
    "text": "When the condition is True, the if side runs and the else side is skipped. When it's False, it's the other way round. A Return inside either side ends the function right there."
   }
  ],
  "example": {
   "caption": "Both paths, side by side",
   "code": "def can_vote(age: int) -> bool:\n    if age >= 18:\n        return True\n    else:\n        return False",
   "notes": {
    "2": "The condition. 18 >= 18 is True, so 18 goes to the if side.",
    "4": "else needs no condition: it covers every other case."
   }
  }
 },
 {
  "id": "elif-grades",
  "title": "3 · More than two choices: elif",
  "level": "Beginner",
  "minutes": 10,
  "goal": "Turn a test score into a letter: 90+ is A, 80+ is B, 70+ is C, anything lower is F.",
  "concepts": [
   "elif",
   "if / else",
   "condition",
   "nesting"
  ],
  "steps": [
   {
    "title": "The first question is done",
    "text": "letter_grade already asks score >= 90 and returns 'A'. The else side holds a second If / Else: that is what Python writes as elif."
   },
   {
    "title": "Answer the second question",
    "text": "In the inner If (score >= 80), add Return 'B' on its if side."
   },
   {
    "title": "Add a third question",
    "text": "On the inner else side, add another If / Else with condition score >= 70. Put Return 'C' on its if side."
   },
   {
    "title": "Catch everything else",
    "text": "On the last else side, add Return 'F'. Watch the Python tab: each If inside an else becomes elif."
   },
   {
    "title": "Check and run",
    "text": "Check your work, then Run tests. Order matters: the questions go from the highest score down."
   }
  ],
  "explain": "An If inside an else is so common that Python has a short word for it: elif. Python asks each question in order and stops at the first one that is true.",
  "tests": [
   {
    "call": "letter_grade(95)",
    "expect": "'A'"
   },
   {
    "call": "letter_grade(90)",
    "expect": "'A'"
   },
   {
    "call": "letter_grade(85)",
    "expect": "'B'"
   },
   {
    "call": "letter_grade(70)",
    "expect": "'C'"
   },
   {
    "call": "letter_grade(42)",
    "expect": "'F'"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Grades",
   "modules": [
    {
     "path": "grades.py",
     "imports": [],
     "functions": [
      {
       "name": "letter_grade",
       "parameters": [
        {
         "name": "score",
         "type": "int"
        }
       ],
       "returns": "str",
       "requirements": [
        "90+ is A, 80+ is B, 70+ is C, lower is F."
       ],
       "body": [
        {
         "kind": "branch",
         "condition": "score >= 90",
         "body": [
          {
           "kind": "return",
           "expression": "'A'"
          }
         ],
         "otherwise": [
          {
           "kind": "branch",
           "condition": "score >= 80",
           "body": [],
           "otherwise": []
          }
         ]
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Grades",
   "modules": [
    {
     "path": "grades.py",
     "imports": [],
     "functions": [
      {
       "name": "letter_grade",
       "parameters": [
        {
         "name": "score",
         "type": "int"
        }
       ],
       "returns": "str",
       "requirements": [
        "90+ is A, 80+ is B, 70+ is C, lower is F."
       ],
       "body": [
        {
         "kind": "branch",
         "condition": "score >= 90",
         "body": [
          {
           "kind": "return",
           "expression": "'A'"
          }
         ],
         "otherwise": [
          {
           "kind": "branch",
           "condition": "score >= 80",
           "body": [
            {
             "kind": "return",
             "expression": "'B'"
            }
           ],
           "otherwise": [
            {
             "kind": "branch",
             "condition": "score >= 70",
             "body": [
              {
               "kind": "return",
               "expression": "'C'"
              }
             ],
             "otherwise": [
              {
               "kind": "return",
               "expression": "'F'"
              }
             ]
            }
           ]
          }
         ]
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Questions in order",
    "text": "With elif, Python asks each question from the top and runs the first side whose condition is True. The rest are skipped, even if they would also be true. That's why the highest score comes first."
   },
   {
    "title": "else is the safety net",
    "text": "The final else catches everything no question matched, so the function always returns something."
   }
  ],
  "example": {
   "caption": "Order decides the answer",
   "code": "def letter_grade(score: int) -> str:\n    if score >= 90:\n        return 'A'\n    elif score >= 80:\n        return 'B'\n    else:\n        return 'F'",
   "notes": {
    "2": "Asked first. 95 stops here, even though 95 >= 80 is also true.",
    "4": "Only asked when the first question was False.",
    "6": "Runs when nothing above matched."
   }
  }
 },
 {
  "id": "guard-inputs",
  "title": "4 · Guard your inputs",
  "level": "Beginner+",
  "minutes": 10,
  "goal": "Reject bad amounts with an error, then use that check inside another function.",
  "concepts": [
   "raise",
   "validation",
   "calling functions",
   "guard clause"
  ],
  "steps": [
   {
    "title": "Write the check",
    "text": "In require_positive add If with condition amount <= 0. Inside it add Raise with ValueError('amount must be positive')."
   },
   {
    "title": "Finish the check",
    "text": "After the If (not inside it), add Return with None. The function only reaches this line when the amount is fine."
   },
   {
    "title": "Use the check",
    "text": "In order_total, add a Check block first: require_positive(quantity). Checking first is called a guard clause."
   },
   {
    "title": "Do the work",
    "text": "Then add Return with quantity * price. Check your work, then Run tests: one test makes sure 0 is refused."
   }
  ],
  "explain": "Small check functions can be reused everywhere. Putting them first means bad data stops at the door instead of causing bugs deep inside.",
  "tests": [
   {
    "call": "order_total(3, 5)",
    "expect": "15"
   },
   {
    "call": "order_total(0, 5)",
    "raises": "ValueError"
   },
   {
    "call": "order_total(-2, 5)",
    "raises": "ValueError"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Orders",
   "modules": [
    {
     "path": "orders.py",
     "imports": [],
     "functions": [
      {
       "name": "require_positive",
       "parameters": [
        {
         "name": "amount",
         "type": "int"
        }
       ],
       "returns": "None",
       "requirements": [],
       "body": [
        {
         "kind": "hole",
         "label": "Raise ValueError when amount is 0 or less",
         "allowed_calls": []
        }
       ]
      },
      {
       "name": "order_total",
       "parameters": [
        {
         "name": "quantity",
         "type": "int"
        },
        {
         "name": "price",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "Validate quantity first."
       ],
       "body": []
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Orders",
   "modules": [
    {
     "path": "orders.py",
     "imports": [],
     "functions": [
      {
       "name": "require_positive",
       "parameters": [
        {
         "name": "amount",
         "type": "int"
        }
       ],
       "returns": "None",
       "requirements": [],
       "body": [
        {
         "kind": "branch",
         "condition": "amount <= 0",
         "body": [
          {
           "kind": "raise",
           "expression": "ValueError('amount must be positive')"
          }
         ],
         "otherwise": []
        },
        {
         "kind": "return",
         "expression": "None"
        }
       ]
      },
      {
       "name": "order_total",
       "parameters": [
        {
         "name": "quantity",
         "type": "int"
        },
        {
         "name": "price",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "Validate quantity first."
       ],
       "body": [
        {
         "kind": "validate",
         "expression": "require_positive(quantity)"
        },
        {
         "kind": "return",
         "expression": "quantity * price"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Errors are messages",
    "text": "raise stops the function and sends an error (an exception) back to the caller. ValueError means 'the value makes no sense'. The text inside explains why, so whoever sees it knows what to fix."
   },
   {
    "title": "Check first, then work",
    "text": "Putting checks at the top of a function is called a guard clause. Everything below the guard can trust its inputs, which keeps the main logic simple."
   }
  ],
  "example": {
   "caption": "A guard at the door",
   "code": "def require_positive(amount: int) -> None:\n    if amount <= 0:\n        raise ValueError('amount must be positive')\n\n\ndef order_total(quantity: int, price: int) -> int:\n    require_positive(quantity)\n    return quantity * price",
   "notes": {
    "3": "Stops here with an error for 0 or negative amounts.",
    "7": "The guard runs first. If it raises, the next line never runs."
   }
  }
 },
 {
  "id": "cart-loop",
  "title": "5 · Loops: shopping cart total",
  "level": "Intermediate",
  "minutes": 12,
  "goal": "Add up price × quantity for every item in a cart, skipping items with no quantity.",
  "concepts": [
   "loop",
   "variable",
   "nesting",
   "accumulator",
   "dictionary"
  ],
  "steps": [
   {
    "title": "Start a running total",
    "text": "Add Set variable: total = 0. This is the accumulator that grows as we loop."
   },
   {
    "title": "Loop over the items",
    "text": "Add Repeat for each with item in items. Everything inside runs once per item."
   },
   {
    "title": "Nest a decision",
    "text": "Inside the loop add If with condition item['qty'] > 0. This is nesting: a block inside a block inside a block."
   },
   {
    "title": "Grow the total",
    "text": "Inside that If add Set variable: total = total + item['price'] * item['qty']."
   },
   {
    "title": "Give back the answer",
    "text": "After the loop (back at the function level) add Return total. Check your work, then Run tests."
   }
  ],
  "explain": "Loop + accumulator is one of the most-used patterns in programming. If nesting gets deeper than about 3 levels, the advisor will suggest a helper function.",
  "tests": [
   {
    "call": "cart_total([{'price': 2, 'qty': 3}, {'price': 5, 'qty': 1}])",
    "expect": "11"
   },
   {
    "call": "cart_total([{'price': 2, 'qty': 3}, {'price': 9, 'qty': 0}])",
    "expect": "6"
   },
   {
    "call": "cart_total([])",
    "expect": "0"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Cart",
   "modules": [
    {
     "path": "cart.py",
     "imports": [],
     "functions": [
      {
       "name": "cart_total",
       "parameters": [
        {
         "name": "items",
         "type": "list"
        }
       ],
       "returns": "int",
       "requirements": [
        "Skip items whose qty is 0 or less."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "total",
         "expression": "0"
        },
        {
         "kind": "loop",
         "target": "item",
         "iterable": "items",
         "body": []
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Cart",
   "modules": [
    {
     "path": "cart.py",
     "imports": [],
     "functions": [
      {
       "name": "cart_total",
       "parameters": [
        {
         "name": "items",
         "type": "list"
        }
       ],
       "returns": "int",
       "requirements": [
        "Skip items whose qty is 0 or less."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "total",
         "expression": "0"
        },
        {
         "kind": "loop",
         "target": "item",
         "iterable": "items",
         "body": [
          {
           "kind": "branch",
           "condition": "item['qty'] > 0",
           "body": [
            {
             "kind": "assign",
             "target": "total",
             "expression": "total + item['price'] * item['qty']"
            }
           ],
           "otherwise": []
          }
         ]
        },
        {
         "kind": "return",
         "expression": "total"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "A loop visits every item",
    "text": "for item in items runs the indented lines once per item, with item naming the current one. A list of 3 items means 3 runs."
   },
   {
    "title": "Start before, finish after",
    "text": "The accumulator (total = 0) is set before the loop, grows inside it, and is returned after it. Put the Return inside the loop by mistake and the function stops after the first item."
   }
  ],
  "example": {
   "caption": "Watching the total grow",
   "code": "def cart_total(items: list) -> int:\n    total = 0\n    for item in items:\n        total = total + item['price'] * item['qty']\n    return total",
   "notes": {
    "2": "Before the loop: start at 0.",
    "4": "Inside the loop: runs once per item. item['price'] reads a value from a dictionary.",
    "5": "After the loop (back at the function's indentation): give back the result."
   }
  }
 },
 {
  "id": "filter-list",
  "title": "6 · Build a list: keep the even numbers",
  "level": "Intermediate",
  "minutes": 10,
  "goal": "Give back a new list holding only the even numbers from the input list.",
  "concepts": [
   "list",
   "loop",
   "method call",
   "condition"
  ],
  "steps": [
   {
    "title": "Start with an empty list",
    "text": "The function already sets evens = [] and returns it at the end. [] is an empty list: a box that can hold many values in order."
   },
   {
    "title": "Ask about each number",
    "text": "Inside the loop add If with condition n % 2 == 0. The % sign gives the remainder after dividing, so an even number leaves 0."
   },
   {
    "title": "Keep the even ones",
    "text": "Inside that If add a Call block: evens.append(n). append is a method: a function that belongs to the list and adds to its end."
   },
   {
    "title": "Check and run",
    "text": "Check your work, then Run tests. Try your own call too, like keep_evens([10, 11, 12])."
   }
  ],
  "explain": "Filtering is the cousin of the accumulator: start empty, loop, keep what passes the test. A Call block runs a function or method for what it does, not for a value it gives back.",
  "tests": [
   {
    "call": "keep_evens([1, 2, 3, 4])",
    "expect": "[2, 4]"
   },
   {
    "call": "keep_evens([7, 9])",
    "expect": "[]"
   },
   {
    "call": "keep_evens([])",
    "expect": "[]"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Evens",
   "modules": [
    {
     "path": "numbers_tools.py",
     "imports": [],
     "functions": [
      {
       "name": "keep_evens",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "list",
       "requirements": [
        "Keep only the numbers that divide evenly by 2."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "evens",
         "expression": "[]"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": []
        },
        {
         "kind": "return",
         "expression": "evens"
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Evens",
   "modules": [
    {
     "path": "numbers_tools.py",
     "imports": [],
     "functions": [
      {
       "name": "keep_evens",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "list",
       "requirements": [
        "Keep only the numbers that divide evenly by 2."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "evens",
         "expression": "[]"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": [
          {
           "kind": "branch",
           "condition": "n % 2 == 0",
           "body": [
            {
             "kind": "call",
             "expression": "evens.append(n)"
            }
           ],
           "otherwise": []
          }
         ]
        },
        {
         "kind": "return",
         "expression": "evens"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Lists grow with append",
    "text": "[] makes an empty list. evens.append(n) adds n to its end. append changes the list itself and returns nothing, which is why it's a Call block, not a Set variable."
   },
   {
    "title": "% gives the remainder",
    "text": "7 % 2 is 1 and 8 % 2 is 0. So n % 2 == 0 asks whether n divides evenly by 2: the usual test for even numbers."
   }
  ],
  "example": {
   "caption": "Keep what passes",
   "code": "def keep_evens(numbers: list) -> list:\n    evens = []\n    for n in numbers:\n        if n % 2 == 0:\n            evens.append(n)\n    return evens",
   "notes": {
    "2": "A new, empty list.",
    "4": "The test each number must pass.",
    "5": "A method call: append belongs to the list."
   }
  }
 },
 {
  "id": "find-largest",
  "title": "7 · Find the biggest number",
  "level": "Intermediate",
  "minutes": 12,
  "goal": "Return the largest number in a list, and refuse an empty list with a clear error.",
  "concepts": [
   "guard clause",
   "variable",
   "loop",
   "comparison"
  ],
  "steps": [
   {
    "title": "Guard first",
    "text": "Add If with condition not numbers. An empty list counts as false, so not numbers is true when there is nothing to look at. Inside it, Raise ValueError('empty list')."
   },
   {
    "title": "Remember a best guess",
    "text": "After the If, add Set variable: best = numbers[0]. Lists count from 0, so this is the first number."
   },
   {
    "title": "Compare each number",
    "text": "Add Repeat for each: n in numbers. Inside it add If with condition n > best, and inside that Set variable: best = n."
   },
   {
    "title": "Return the winner",
    "text": "After the loop add Return best. Check your work, then Run tests: they include negative numbers."
   }
  ],
  "explain": "Keep a best-so-far and update it when you find something better: the same idea finds the cheapest price, the oldest user or the longest word. The guard makes numbers[0] safe.",
  "tests": [
   {
    "call": "largest([3, 9, 2])",
    "expect": "9"
   },
   {
    "call": "largest([-5, -2, -9])",
    "expect": "-2"
   },
   {
    "call": "largest([7])",
    "expect": "7"
   },
   {
    "call": "largest([])",
    "raises": "ValueError"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Largest",
   "modules": [
    {
     "path": "stats.py",
     "imports": [],
     "functions": [
      {
       "name": "largest",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "int",
       "requirements": [
        "Raise ValueError for an empty list."
       ],
       "body": [
        {
         "kind": "hole",
         "label": "Refuse an empty list",
         "allowed_calls": []
        },
        {
         "kind": "assign",
         "target": "best",
         "expression": "numbers[0]"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": []
        },
        {
         "kind": "return",
         "expression": "best"
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Largest",
   "modules": [
    {
     "path": "stats.py",
     "imports": [],
     "functions": [
      {
       "name": "largest",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "int",
       "requirements": [
        "Raise ValueError for an empty list."
       ],
       "body": [
        {
         "kind": "branch",
         "condition": "not numbers",
         "body": [
          {
           "kind": "raise",
           "expression": "ValueError('empty list')"
          }
         ],
         "otherwise": []
        },
        {
         "kind": "assign",
         "target": "best",
         "expression": "numbers[0]"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": [
          {
           "kind": "branch",
           "condition": "n > best",
           "body": [
            {
             "kind": "assign",
             "target": "best",
             "expression": "n"
            }
           ],
           "otherwise": []
          }
         ]
        },
        {
         "kind": "return",
         "expression": "best"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Best so far",
    "text": "Start with the first item as the best guess, then compare every item with it and replace it when you find a bigger one. At the end, the best guess is the answer."
   },
   {
    "title": "Why the guard matters",
    "text": "numbers[0] fails on an empty list (IndexError). Checking for an empty list first turns a confusing crash into a clear error message."
   }
  ],
  "example": {
   "caption": "Replace when better",
   "code": "def largest(numbers: list) -> int:\n    if not numbers:\n        raise ValueError('empty list')\n    best = numbers[0]\n    for n in numbers:\n        if n > best:\n            best = n\n    return best",
   "notes": {
    "2": "not numbers is True for an empty list.",
    "4": "Index 0 is the first item: Python counts from 0.",
    "7": "Point best at the new winner."
   }
  }
 },
 {
  "id": "split-files",
  "title": "8 · Split code into files: login check",
  "level": "Intermediate",
  "minutes": 15,
  "goal": "Keep user lookup in one file and login logic in another, connected by an import.",
  "concepts": [
   "module",
   "folder (package)",
   "import",
   "separation of concerns"
  ],
  "steps": [
   {
    "title": "Two files, two jobs",
    "text": "auth/users.py finds users. auth/login.py decides if a login is allowed. One job per file keeps code easy to find and test."
   },
   {
    "title": "Finish find_user",
    "text": "In users.py add If with name not in users, then inside it Raise KeyError(name). After the If, Return users[name]."
   },
   {
    "title": "Import it",
    "text": "Select login.py. Its imports already say from auth.users import find_user. That line connects the two files."
   },
   {
    "title": "Write login",
    "text": "Replace the TODO: add Set variable user = find_user(users, name). Then If user.get('active') is not True → Raise PermissionError('account disabled')."
   },
   {
    "title": "Finish",
    "text": "After the If, Return user.get('password_hash') == password_hash. Check your work, Run tests, then read the advisor tips about folders."
   }
  ],
  "explain": "Real projects grow by adding files, then folders (packages). Rule of thumb: a file per topic, a folder per feature. Never store plain passwords; real apps compare password hashes.",
  "tests": [
   {
    "call": "login({'ana': {'active': True, 'password_hash': 'h1'}}, 'ana', 'h1')",
    "expect": "True"
   },
   {
    "call": "login({'ana': {'active': True, 'password_hash': 'h1'}}, 'ana', 'nope')",
    "expect": "False"
   },
   {
    "call": "login({'bo': {'active': False, 'password_hash': 'h2'}}, 'bo', 'h2')",
    "raises": "PermissionError"
   },
   {
    "call": "login({}, 'ghost', 'h3')",
    "raises": "KeyError"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Login",
   "modules": [
    {
     "path": "auth/users.py",
     "imports": [],
     "functions": [
      {
       "name": "find_user",
       "parameters": [
        {
         "name": "users",
         "type": "dict"
        },
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "dict",
       "requirements": [],
       "body": []
      }
     ]
    },
    {
     "path": "auth/login.py",
     "imports": [
      "from auth.users import find_user"
     ],
     "functions": [
      {
       "name": "login",
       "parameters": [
        {
         "name": "users",
         "type": "dict"
        },
        {
         "name": "name",
         "type": "str"
        },
        {
         "name": "password_hash",
         "type": "str"
        }
       ],
       "returns": "bool",
       "requirements": [
        "Disabled accounts can never log in."
       ],
       "body": [
        {
         "kind": "hole",
         "label": "Look up the user, refuse disabled accounts, compare hashes",
         "allowed_calls": [
          "find_user",
          "user.get"
         ]
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Login",
   "modules": [
    {
     "path": "auth/users.py",
     "imports": [],
     "functions": [
      {
       "name": "find_user",
       "parameters": [
        {
         "name": "users",
         "type": "dict"
        },
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "dict",
       "requirements": [],
       "body": [
        {
         "kind": "branch",
         "condition": "name not in users",
         "body": [
          {
           "kind": "raise",
           "expression": "KeyError(name)"
          }
         ],
         "otherwise": []
        },
        {
         "kind": "return",
         "expression": "users[name]"
        }
       ]
      }
     ]
    },
    {
     "path": "auth/login.py",
     "imports": [
      "from auth.users import find_user"
     ],
     "functions": [
      {
       "name": "login",
       "parameters": [
        {
         "name": "users",
         "type": "dict"
        },
        {
         "name": "name",
         "type": "str"
        },
        {
         "name": "password_hash",
         "type": "str"
        }
       ],
       "returns": "bool",
       "requirements": [
        "Disabled accounts can never log in."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "user",
         "expression": "find_user(users, name)"
        },
        {
         "kind": "branch",
         "condition": "user.get('active') is not True",
         "body": [
          {
           "kind": "raise",
           "expression": "PermissionError('account disabled')"
          }
         ],
         "otherwise": []
        },
        {
         "kind": "return",
         "expression": "user.get('password_hash') == password_hash"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Each file is a module",
    "text": "auth/users.py becomes the module auth.users. Another file can use its functions after importing them: from auth.users import find_user."
   },
   {
    "title": "Why split at all",
    "text": "When each file has one job, you know where to look, you can test each part on its own, and two people can work on different files at once."
   }
  ],
  "example": {
   "caption": "Two files, one import",
   "code": "# auth/users.py\ndef find_user(users: dict, name: str) -> dict:\n    return users[name]\n\n\n# auth/login.py\nfrom auth.users import find_user\n\n\ndef login(users: dict, name: str) -> bool:\n    user = find_user(users, name)\n    return user.get('active') is True",
   "notes": {
    "1": "A comment naming the file this part belongs to.",
    "7": "The import line connects login.py to users.py.",
    "11": "Now find_user can be called here."
   }
  }
 },
 {
  "id": "try-except",
  "title": "9 · Handle mistakes with try / except",
  "level": "Intermediate",
  "minutes": 10,
  "goal": "Turn text like '3' into a number, and give back a fallback instead of crashing when the text isn't a number.",
  "concepts": [
   "try / except",
   "default value",
   "raise"
  ],
  "steps": [
   {
    "title": "See the default value",
    "text": "The inputs say fallback: int=0. The =0 is a default value: callers can leave fallback out, and it will be 0."
   },
   {
    "title": "Try the risky part",
    "text": "In the Try / Except block's try side, add Return with int(text). int('3') gives 3, but int('abc') raises ValueError."
   },
   {
    "title": "Catch the mistake",
    "text": "The except side runs only when ValueError happens. Add Return with fallback there."
   },
   {
    "title": "Check and run",
    "text": "Check your work, then Run tests. Try your own call too, like to_quantity('ten', 1)."
   }
  ],
  "explain": "try / except lets your code recover from an error you expect. Catch only the error you mean (ValueError here): catching everything can hide real bugs.",
  "tests": [
   {
    "call": "to_quantity('3')",
    "expect": "3"
   },
   {
    "call": "to_quantity(' 7 ')",
    "expect": "7"
   },
   {
    "call": "to_quantity('abc')",
    "expect": "0"
   },
   {
    "call": "to_quantity('abc', 5)",
    "expect": "5"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Quantities",
   "modules": [
    {
     "path": "parsing.py",
     "imports": [],
     "functions": [
      {
       "name": "to_quantity",
       "parameters": [
        {
         "name": "text",
         "type": "str"
        },
        {
         "name": "fallback",
         "type": "int",
         "default": "0"
        }
       ],
       "returns": "int",
       "requirements": [
        "Return fallback when text is not a whole number."
       ],
       "body": [
        {
         "kind": "try",
         "body": [],
         "exception": "ValueError",
         "alias": "",
         "handler": [],
         "finally": []
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Quantities",
   "modules": [
    {
     "path": "parsing.py",
     "imports": [],
     "functions": [
      {
       "name": "to_quantity",
       "parameters": [
        {
         "name": "text",
         "type": "str"
        },
        {
         "name": "fallback",
         "type": "int",
         "default": "0"
        }
       ],
       "returns": "int",
       "requirements": [
        "Return fallback when text is not a whole number."
       ],
       "body": [
        {
         "kind": "try",
         "body": [
          {
           "kind": "return",
           "expression": "int(text)"
          }
         ],
         "exception": "ValueError",
         "alias": "",
         "handler": [
          {
           "kind": "return",
           "expression": "fallback"
          }
         ],
         "finally": []
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Expect the error, then handle it",
    "text": "Some operations can fail for reasons outside your control: text that isn't a number, a missing file. try runs the risky part; if the named error happens, Python jumps to except instead of crashing."
   },
   {
    "title": "Defaults make inputs optional",
    "text": "fallback: int=0 gives the parameter a default value. Callers may leave it out (it's then 0) or pass their own: to_quantity('x', 5)."
   }
  ],
  "example": {
   "caption": "Recovering from a bad value",
   "code": "def to_quantity(text: str, fallback: int = 0) -> int:\n    try:\n        return int(text)\n    except ValueError:\n        return fallback",
   "notes": {
    "1": "= 0 is the default value. (Blockwise writes it as fallback: int=0; both mean the same.)",
    "3": "int('abc') raises ValueError here.",
    "4": "Only ValueError is caught; other errors still show up, which helps you find real bugs."
   }
  }
 },
 {
  "id": "while-digits",
  "title": "10 · Repeat while: add up the digits",
  "level": "Intermediate",
  "minutes": 12,
  "goal": "Add up the digits of a whole number: 123 gives 1 + 2 + 3 = 6.",
  "concepts": [
   "while loop",
   "augmented assignment",
   "variable"
  ],
  "steps": [
   {
    "title": "Read the loop",
    "text": "Repeat while runs its inside again and again as long as its condition, n > 0, is true. Something inside must make n smaller, or it never stops."
   },
   {
    "title": "Take the last digit",
    "text": "Replace the TODO with Set variable: total, choose += in the middle box, and type n % 10. n % 10 is the last digit (123 % 10 is 3), and += adds it on."
   },
   {
    "title": "Drop the last digit",
    "text": "Add another Set variable: n, choose //=, and type 10. n //= 10 divides and drops the remainder, so 123 becomes 12. This is what makes the loop stop."
   },
   {
    "title": "Check and run",
    "text": "Check your work, then Run tests. If you ever make a loop that never stops, Run stops it after 10 seconds."
   }
  ],
  "explain": "Use Repeat for each when you have a list to walk through, and Repeat while when you repeat until something changes. total += x is short for total = total + x.",
  "tests": [
   {
    "call": "digit_sum(123)",
    "expect": "6"
   },
   {
    "call": "digit_sum(1005)",
    "expect": "6"
   },
   {
    "call": "digit_sum(9)",
    "expect": "9"
   },
   {
    "call": "digit_sum(0)",
    "expect": "0"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Digits",
   "modules": [
    {
     "path": "digits.py",
     "imports": [],
     "functions": [
      {
       "name": "digit_sum",
       "parameters": [
        {
         "name": "n",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "n is 0 or more."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "total",
         "expression": "0"
        },
        {
         "kind": "while",
         "condition": "n > 0",
         "body": [
          {
           "kind": "hole",
           "label": "Add the last digit to total, then drop it from n",
           "allowed_calls": []
          }
         ]
        },
        {
         "kind": "return",
         "expression": "total"
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Digits",
   "modules": [
    {
     "path": "digits.py",
     "imports": [],
     "functions": [
      {
       "name": "digit_sum",
       "parameters": [
        {
         "name": "n",
         "type": "int"
        }
       ],
       "returns": "int",
       "requirements": [
        "n is 0 or more."
       ],
       "body": [
        {
         "kind": "assign",
         "target": "total",
         "expression": "0"
        },
        {
         "kind": "while",
         "condition": "n > 0",
         "body": [
          {
           "kind": "assign",
           "target": "total",
           "operator": "+=",
           "expression": "n % 10"
          },
          {
           "kind": "assign",
           "target": "n",
           "operator": "//=",
           "expression": "10"
          }
         ]
        },
        {
         "kind": "return",
         "expression": "total"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "while repeats until the condition is false",
    "text": "Python checks the condition before each turn. When it's False, the loop ends. Something inside must move the condition toward False, or the loop never ends."
   },
   {
    "title": "Short ways to update a variable",
    "text": "total += x means total = total + x. Likewise n //= 10 divides n by 10 and drops the remainder (123 becomes 12)."
   }
  ],
  "example": {
   "caption": "Taking a number apart",
   "code": "def digit_sum(n: int) -> int:\n    total = 0\n    while n > 0:\n        total += n % 10\n        n //= 10\n    return total",
   "notes": {
    "3": "Checked before every turn: stops once n reaches 0.",
    "4": "n % 10 is the last digit.",
    "5": "This line makes progress toward stopping."
   }
  }
 },
 {
  "id": "break-early",
  "title": "11 · Stop early with break",
  "level": "Intermediate",
  "minutes": 8,
  "goal": "Find the first negative number in a list, or None if there isn't one, without looking further than you need to.",
  "concepts": [
   "break / continue",
   "loop",
   "condition"
  ],
  "steps": [
   {
    "title": "Look at the plan",
    "text": "result starts as None (Python's word for 'nothing'). The loop walks through numbers, and the function returns result at the end."
   },
   {
    "title": "Spot a negative",
    "text": "Inside the loop add If with condition n < 0."
   },
   {
    "title": "Remember it and stop",
    "text": "Inside that If add Set variable: result = n, then a Stop loop block. Stop loop is Python's break: it leaves the loop right away."
   },
   {
    "title": "Check and run",
    "text": "Check your work, then Run tests. Without the Stop loop, you'd get the last negative instead of the first: try it and see."
   }
  ],
  "explain": "break leaves a loop early; its partner continue (Skip to next) jumps straight to the next item. Stopping as soon as you have the answer saves work on long lists.",
  "tests": [
   {
    "call": "first_negative([3, -1, -5])",
    "expect": "-1"
   },
   {
    "call": "first_negative([-4])",
    "expect": "-4"
   },
   {
    "call": "first_negative([1, 2])",
    "expect": "None"
   },
   {
    "call": "first_negative([])",
    "expect": "None"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "First negative",
   "modules": [
    {
     "path": "search.py",
     "imports": [],
     "functions": [
      {
       "name": "first_negative",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "int | None",
       "requirements": [],
       "body": [
        {
         "kind": "assign",
         "target": "result",
         "expression": "None"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": []
        },
        {
         "kind": "return",
         "expression": "result"
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "First negative",
   "modules": [
    {
     "path": "search.py",
     "imports": [],
     "functions": [
      {
       "name": "first_negative",
       "parameters": [
        {
         "name": "numbers",
         "type": "list"
        }
       ],
       "returns": "int | None",
       "requirements": [],
       "body": [
        {
         "kind": "assign",
         "target": "result",
         "expression": "None"
        },
        {
         "kind": "loop",
         "target": "n",
         "iterable": "numbers",
         "body": [
          {
           "kind": "branch",
           "condition": "n < 0",
           "body": [
            {
             "kind": "assign",
             "target": "result",
             "expression": "n"
            },
            {
             "kind": "break"
            }
           ],
           "otherwise": []
          }
         ]
        },
        {
         "kind": "return",
         "expression": "result"
        }
       ]
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "break leaves the loop",
    "text": "break ends the loop right away, even with items left. The code after the loop continues as normal."
   },
   {
    "title": "continue skips one turn",
    "text": "continue jumps straight to the next item, skipping the rest of the loop body for this one. Use it to skip items you don't care about."
   }
  ],
  "example": {
   "caption": "Stop at the first match",
   "code": "def first_negative(numbers: list) -> int | None:\n    result = None\n    for n in numbers:\n        if n < 0:\n            result = n\n            break\n    return result",
   "notes": {
    "1": "int | None: the result is an int, or None when there's no negative.",
    "6": "Leaves the loop as soon as one is found.",
    "7": "Runs after the loop, whether or not break happened."
   }
  }
 },
 {
  "id": "main-block",
  "title": "12 · Make it runnable: the main block",
  "level": "Intermediate",
  "minutes": 10,
  "goal": "Turn greet.py into a program you can run from a terminal: python greet.py Ana prints Hello, Ana!",
  "concepts": [
   "main block",
   "command-line arguments",
   "import"
  ],
  "steps": [
   {
    "title": "The function is ready",
    "text": "greeting('Ana') already gives back 'Hello, Ana!'. But running python greet.py would do nothing yet: nothing calls greeting."
   },
   {
    "title": "Add a main block",
    "text": "In the Project panel, click + main block under greet.py. It adds a Call block that runs when the file is started directly."
   },
   {
    "title": "Read the command line",
    "text": "Change the Call to print(greeting(sys.argv[1])). sys.argv holds the words typed after python; sys.argv[1] is the first one. import sys is already at the top."
   },
   {
    "title": "Run it",
    "text": "In the Python tab, type Ana next to Run file and press it. Then Check my work and Run tests."
   }
  ],
  "explain": "The main block is a file's front door: it runs when you start the file, but not when another file imports it, so the same file can be a program and a library. Every blueprint in the Templates tab ends with one.",
  "tests": [
   {
    "call": "greeting('Ana')",
    "expect": "'Hello, Ana!'"
   },
   {
    "run": "greet.py",
    "argv": [
     "Ana"
    ],
    "stdout": "Hello, Ana!\n"
   },
   {
    "run": "greet.py",
    "argv": [
     "Sam"
    ],
    "stdout": "Hello, Sam!\n"
   }
  ],
  "starter": {
   "format": "blockwise-plan-v1",
   "title": "Greeter",
   "modules": [
    {
     "path": "greet.py",
     "imports": [
      "import sys"
     ],
     "functions": [
      {
       "name": "greeting",
       "parameters": [
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "str",
       "requirements": [],
       "body": [
        {
         "kind": "return",
         "expression": "f'Hello, {name}!'"
        }
       ]
      }
     ]
    }
   ]
  },
  "solution": {
   "format": "blockwise-plan-v1",
   "title": "Greeter",
   "modules": [
    {
     "path": "greet.py",
     "imports": [
      "import sys"
     ],
     "functions": [
      {
       "name": "greeting",
       "parameters": [
        {
         "name": "name",
         "type": "str"
        }
       ],
       "returns": "str",
       "requirements": [],
       "body": [
        {
         "kind": "return",
         "expression": "f'Hello, {name}!'"
        }
       ]
      }
     ],
     "entry": [
      {
       "kind": "call",
       "expression": "print(greeting(sys.argv[1]))"
      }
     ]
    }
   ]
  },
  "learn": [
   {
    "title": "Two ways to use a file",
    "text": "You can run a file (python greet.py) or import it from another file. When it's run, Python sets the special name __name__ to '__main__'; when it's imported, __name__ is the module's name. The main block uses that to run only when started directly."
   },
   {
    "title": "Arguments from the terminal",
    "text": "sys.argv is the list of words typed to start the program. sys.argv[0] is the file name, and the words after it follow: python greet.py Ana gives ['greet.py', 'Ana']."
   }
  ],
  "example": {
   "caption": "A file that is also a program",
   "code": "import sys\n\n\ndef greeting(name: str) -> str:\n    return f'Hello, {name}!'\n\n\nif __name__ == '__main__':\n    print(greeting(sys.argv[1]))",
   "notes": {
    "1": "sys gives access to the command line.",
    "8": "True only when this file was started directly.",
    "9": "sys.argv[1] is the first word after the file name."
   }
  }
 }
];
