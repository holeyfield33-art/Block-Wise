// Blockwise Studio lessons. Each lesson's `solution` is a valid blockwise-plan-v1 plan
// (tests/test_studio.py checks that it compiles). `starter` is the guided, partly
// pre-filled version; "blank" mode keeps only the files and function signatures.
// `tests` are real calls run against the learner's code ("Run tests"); the test suite runs
// them against every solution. Each test has `call` plus `expect` (a Python value) or `raises`.
// Every entry in `concepts` must exist in the Studio glossary.
window.BLOCKWISE_LESSONS = [
  {
    "id": "first-function",
    "title": "1 · Your first function",
    "level": "Beginner",
    "minutes": 5,
    "goal": "Write a function that takes a name and gives back a greeting.",
    "concepts": ["function", "parameter", "return", "string"],
    "steps": [
      {"title": "Look at the function card", "text": "A function is a named recipe. This one is called greet and takes one input (a parameter) called name of type str (text)."},
      {"title": "Add a Return block", "text": "Click '+ add a block' inside greet and choose Return. A return hands a value back to whoever called the function."},
      {"title": "Fill in what to return", "text": "Type f'Hello, {name}!' in the Return block. The f before the quotes lets you drop the name into the text."},
      {"title": "Check, then run it", "text": "Press Check my work, then Run tests to call greet for real. The Python tab shows exactly what you built."}
    ],
    "explain": "Every function has a name, inputs in brackets, and usually a return. greet('Ana') now gives back 'Hello, Ana!'.",
    "tests": [
      {"call": "greet('Ana')", "expect": "'Hello, Ana!'"},
      {"call": "greet('Sam')", "expect": "'Hello, Sam!'"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Greeting", "modules": [{"path": "greetings.py", "imports": [], "functions": [
      {"name": "greet", "parameters": [{"name": "name", "type": "str"}], "returns": "str", "requirements": ["Give back a friendly greeting that uses the name."], "body": []}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Greeting", "modules": [{"path": "greetings.py", "imports": [], "functions": [
      {"name": "greet", "parameters": [{"name": "name", "type": "str"}], "returns": "str", "requirements": ["Give back a friendly greeting that uses the name."], "body": [
        {"kind": "return", "expression": "f'Hello, {name}!'"}]}]}]}
  },
  {
    "id": "if-else",
    "title": "2 · Make a decision with If / Else",
    "level": "Beginner",
    "minutes": 8,
    "goal": "Decide if someone can vote: True for 18 and over, otherwise False.",
    "concepts": ["if / else", "condition", "boolean"],
    "steps": [
      {"title": "Add an If block", "text": "Inside can_vote, add an If / Else block. Its condition is a question with a yes/no answer. Type age >= 18."},
      {"title": "Fill the 'if' side", "text": "Inside the if part, add Return with True. This runs only when the condition is true."},
      {"title": "Fill the 'else' side", "text": "Inside the else part, add Return with False. This runs when the condition is false."},
      {"title": "Check, then compare", "text": "Check your work. Notice the boundary: 18 counts, because >= means 'greater than or equal'. Run tests tries 17, 18 and 40."}
    ],
    "explain": "If / Else splits your program into two paths. Getting the boundary right (>= versus >) is one of the most common bugs in real code.",
    "tests": [
      {"call": "can_vote(18)", "expect": "True"},
      {"call": "can_vote(17)", "expect": "False"},
      {"call": "can_vote(40)", "expect": "True"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Voting age", "modules": [{"path": "voting.py", "imports": [], "functions": [
      {"name": "can_vote", "parameters": [{"name": "age", "type": "int"}], "returns": "bool", "requirements": ["True for age 18 and over, else False."], "body": [
        {"kind": "branch", "condition": "age >= 18", "body": [], "otherwise": []}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Voting age", "modules": [{"path": "voting.py", "imports": [], "functions": [
      {"name": "can_vote", "parameters": [{"name": "age", "type": "int"}], "returns": "bool", "requirements": ["True for age 18 and over, else False."], "body": [
        {"kind": "branch", "condition": "age >= 18", "body": [{"kind": "return", "expression": "True"}],
         "otherwise": [{"kind": "return", "expression": "False"}]}]}]}]}
  },
  {
    "id": "elif-grades",
    "title": "3 · More than two choices: elif",
    "level": "Beginner",
    "minutes": 10,
    "goal": "Turn a test score into a letter: 90+ is A, 80+ is B, 70+ is C, anything lower is F.",
    "concepts": ["elif", "if / else", "condition", "nesting"],
    "steps": [
      {"title": "The first question is done", "text": "letter_grade already asks score >= 90 and returns 'A'. The else side holds a second If / Else: that is what Python writes as elif."},
      {"title": "Answer the second question", "text": "In the inner If (score >= 80), add Return 'B' on its if side."},
      {"title": "Add a third question", "text": "On the inner else side, add another If / Else with condition score >= 70. Put Return 'C' on its if side."},
      {"title": "Catch everything else", "text": "On the last else side, add Return 'F'. Watch the Python tab: each If inside an else becomes elif."},
      {"title": "Check and run", "text": "Check your work, then Run tests. Order matters: the questions go from the highest score down."}
    ],
    "explain": "An If inside an else is so common that Python has a short word for it: elif. Python asks each question in order and stops at the first one that is true.",
    "tests": [
      {"call": "letter_grade(95)", "expect": "'A'"},
      {"call": "letter_grade(90)", "expect": "'A'"},
      {"call": "letter_grade(85)", "expect": "'B'"},
      {"call": "letter_grade(70)", "expect": "'C'"},
      {"call": "letter_grade(42)", "expect": "'F'"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Grades", "modules": [{"path": "grades.py", "imports": [], "functions": [
      {"name": "letter_grade", "parameters": [{"name": "score", "type": "int"}], "returns": "str", "requirements": ["90+ is A, 80+ is B, 70+ is C, lower is F."], "body": [
        {"kind": "branch", "condition": "score >= 90", "body": [{"kind": "return", "expression": "'A'"}], "otherwise": [
          {"kind": "branch", "condition": "score >= 80", "body": [], "otherwise": []}]}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Grades", "modules": [{"path": "grades.py", "imports": [], "functions": [
      {"name": "letter_grade", "parameters": [{"name": "score", "type": "int"}], "returns": "str", "requirements": ["90+ is A, 80+ is B, 70+ is C, lower is F."], "body": [
        {"kind": "branch", "condition": "score >= 90", "body": [{"kind": "return", "expression": "'A'"}], "otherwise": [
          {"kind": "branch", "condition": "score >= 80", "body": [{"kind": "return", "expression": "'B'"}], "otherwise": [
            {"kind": "branch", "condition": "score >= 70", "body": [{"kind": "return", "expression": "'C'"}], "otherwise": [
              {"kind": "return", "expression": "'F'"}]}]}]}]}]}]}
  },
  {
    "id": "guard-inputs",
    "title": "4 · Guard your inputs",
    "level": "Beginner+",
    "minutes": 10,
    "goal": "Reject bad amounts with an error, then use that check inside another function.",
    "concepts": ["raise", "validation", "calling functions", "guard clause"],
    "steps": [
      {"title": "Write the check", "text": "In require_positive add If with condition amount <= 0. Inside it add Raise with ValueError('amount must be positive')."},
      {"title": "Finish the check", "text": "After the If (not inside it), add Return with None. The function only reaches this line when the amount is fine."},
      {"title": "Use the check", "text": "In order_total, add a Check block first: require_positive(quantity). Checking first is called a guard clause."},
      {"title": "Do the work", "text": "Then add Return with quantity * price. Check your work, then Run tests: one test makes sure 0 is refused."}
    ],
    "explain": "Small check functions can be reused everywhere. Putting them first means bad data stops at the door instead of causing bugs deep inside.",
    "tests": [
      {"call": "order_total(3, 5)", "expect": "15"},
      {"call": "order_total(0, 5)", "raises": "ValueError"},
      {"call": "order_total(-2, 5)", "raises": "ValueError"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Orders", "modules": [{"path": "orders.py", "imports": [], "functions": [
      {"name": "require_positive", "parameters": [{"name": "amount", "type": "int"}], "returns": "None", "requirements": [], "body": [
        {"kind": "hole", "label": "Raise ValueError when amount is 0 or less", "allowed_calls": []}]},
      {"name": "order_total", "parameters": [{"name": "quantity", "type": "int"}, {"name": "price", "type": "int"}], "returns": "int", "requirements": ["Validate quantity first."], "body": []}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Orders", "modules": [{"path": "orders.py", "imports": [], "functions": [
      {"name": "require_positive", "parameters": [{"name": "amount", "type": "int"}], "returns": "None", "requirements": [], "body": [
        {"kind": "branch", "condition": "amount <= 0", "body": [{"kind": "raise", "expression": "ValueError('amount must be positive')"}], "otherwise": []},
        {"kind": "return", "expression": "None"}]},
      {"name": "order_total", "parameters": [{"name": "quantity", "type": "int"}, {"name": "price", "type": "int"}], "returns": "int", "requirements": ["Validate quantity first."], "body": [
        {"kind": "validate", "expression": "require_positive(quantity)"},
        {"kind": "return", "expression": "quantity * price"}]}]}]}
  },
  {
    "id": "cart-loop",
    "title": "5 · Loops: shopping cart total",
    "level": "Intermediate",
    "minutes": 12,
    "goal": "Add up price × quantity for every item in a cart, skipping items with no quantity.",
    "concepts": ["loop", "variable", "nesting", "accumulator", "dictionary"],
    "steps": [
      {"title": "Start a running total", "text": "Add Set variable: total = 0. This is the accumulator that grows as we loop."},
      {"title": "Loop over the items", "text": "Add Repeat for each with item in items. Everything inside runs once per item."},
      {"title": "Nest a decision", "text": "Inside the loop add If with condition item['qty'] > 0. This is nesting: a block inside a block inside a block."},
      {"title": "Grow the total", "text": "Inside that If add Set variable: total = total + item['price'] * item['qty']."},
      {"title": "Give back the answer", "text": "After the loop (back at the function level) add Return total. Check your work, then Run tests."}
    ],
    "explain": "Loop + accumulator is one of the most-used patterns in programming. If nesting gets deeper than about 3 levels, the advisor will suggest a helper function.",
    "tests": [
      {"call": "cart_total([{'price': 2, 'qty': 3}, {'price': 5, 'qty': 1}])", "expect": "11"},
      {"call": "cart_total([{'price': 2, 'qty': 3}, {'price': 9, 'qty': 0}])", "expect": "6"},
      {"call": "cart_total([])", "expect": "0"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Cart", "modules": [{"path": "cart.py", "imports": [], "functions": [
      {"name": "cart_total", "parameters": [{"name": "items", "type": "list"}], "returns": "int", "requirements": ["Skip items whose qty is 0 or less."], "body": [
        {"kind": "assign", "target": "total", "expression": "0"},
        {"kind": "loop", "target": "item", "iterable": "items", "body": []}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Cart", "modules": [{"path": "cart.py", "imports": [], "functions": [
      {"name": "cart_total", "parameters": [{"name": "items", "type": "list"}], "returns": "int", "requirements": ["Skip items whose qty is 0 or less."], "body": [
        {"kind": "assign", "target": "total", "expression": "0"},
        {"kind": "loop", "target": "item", "iterable": "items", "body": [
          {"kind": "branch", "condition": "item['qty'] > 0", "body": [
            {"kind": "assign", "target": "total", "expression": "total + item['price'] * item['qty']"}], "otherwise": []}]},
        {"kind": "return", "expression": "total"}]}]}]}
  },
  {
    "id": "filter-list",
    "title": "6 · Build a list: keep the even numbers",
    "level": "Intermediate",
    "minutes": 10,
    "goal": "Give back a new list holding only the even numbers from the input list.",
    "concepts": ["list", "loop", "method call", "condition"],
    "steps": [
      {"title": "Start with an empty list", "text": "The function already sets evens = [] and returns it at the end. [] is an empty list: a box that can hold many values in order."},
      {"title": "Ask about each number", "text": "Inside the loop add If with condition n % 2 == 0. The % sign gives the remainder after dividing, so an even number leaves 0."},
      {"title": "Keep the even ones", "text": "Inside that If add a Call block: evens.append(n). append is a method: a function that belongs to the list and adds to its end."},
      {"title": "Check and run", "text": "Check your work, then Run tests. Try your own call too, like keep_evens([10, 11, 12])."}
    ],
    "explain": "Filtering is the cousin of the accumulator: start empty, loop, keep what passes the test. A Call block runs a function or method for what it does, not for a value it gives back.",
    "tests": [
      {"call": "keep_evens([1, 2, 3, 4])", "expect": "[2, 4]"},
      {"call": "keep_evens([7, 9])", "expect": "[]"},
      {"call": "keep_evens([])", "expect": "[]"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Evens", "modules": [{"path": "numbers_tools.py", "imports": [], "functions": [
      {"name": "keep_evens", "parameters": [{"name": "numbers", "type": "list"}], "returns": "list", "requirements": ["Keep only the numbers that divide evenly by 2."], "body": [
        {"kind": "assign", "target": "evens", "expression": "[]"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": []},
        {"kind": "return", "expression": "evens"}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Evens", "modules": [{"path": "numbers_tools.py", "imports": [], "functions": [
      {"name": "keep_evens", "parameters": [{"name": "numbers", "type": "list"}], "returns": "list", "requirements": ["Keep only the numbers that divide evenly by 2."], "body": [
        {"kind": "assign", "target": "evens", "expression": "[]"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": [
          {"kind": "branch", "condition": "n % 2 == 0", "body": [{"kind": "call", "expression": "evens.append(n)"}], "otherwise": []}]},
        {"kind": "return", "expression": "evens"}]}]}]}
  },
  {
    "id": "find-largest",
    "title": "7 · Find the biggest number",
    "level": "Intermediate",
    "minutes": 12,
    "goal": "Return the largest number in a list, and refuse an empty list with a clear error.",
    "concepts": ["guard clause", "variable", "loop", "comparison"],
    "steps": [
      {"title": "Guard first", "text": "Add If with condition not numbers. An empty list counts as false, so not numbers is true when there is nothing to look at. Inside it, Raise ValueError('empty list')."},
      {"title": "Remember a best guess", "text": "After the If, add Set variable: best = numbers[0]. Lists count from 0, so this is the first number."},
      {"title": "Compare each number", "text": "Add Repeat for each: n in numbers. Inside it add If with condition n > best, and inside that Set variable: best = n."},
      {"title": "Return the winner", "text": "After the loop add Return best. Check your work, then Run tests: they include negative numbers."}
    ],
    "explain": "Keep a best-so-far and update it when you find something better: the same idea finds the cheapest price, the oldest user or the longest word. The guard makes numbers[0] safe.",
    "tests": [
      {"call": "largest([3, 9, 2])", "expect": "9"},
      {"call": "largest([-5, -2, -9])", "expect": "-2"},
      {"call": "largest([7])", "expect": "7"},
      {"call": "largest([])", "raises": "ValueError"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Largest", "modules": [{"path": "stats.py", "imports": [], "functions": [
      {"name": "largest", "parameters": [{"name": "numbers", "type": "list"}], "returns": "int", "requirements": ["Raise ValueError for an empty list."], "body": [
        {"kind": "hole", "label": "Refuse an empty list", "allowed_calls": []},
        {"kind": "assign", "target": "best", "expression": "numbers[0]"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": []},
        {"kind": "return", "expression": "best"}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Largest", "modules": [{"path": "stats.py", "imports": [], "functions": [
      {"name": "largest", "parameters": [{"name": "numbers", "type": "list"}], "returns": "int", "requirements": ["Raise ValueError for an empty list."], "body": [
        {"kind": "branch", "condition": "not numbers", "body": [{"kind": "raise", "expression": "ValueError('empty list')"}], "otherwise": []},
        {"kind": "assign", "target": "best", "expression": "numbers[0]"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": [
          {"kind": "branch", "condition": "n > best", "body": [{"kind": "assign", "target": "best", "expression": "n"}], "otherwise": []}]},
        {"kind": "return", "expression": "best"}]}]}]}
  },
  {
    "id": "split-files",
    "title": "8 · Split code into files: login check",
    "level": "Intermediate",
    "minutes": 15,
    "goal": "Keep user lookup in one file and login logic in another, connected by an import.",
    "concepts": ["module", "folder (package)", "import", "separation of concerns"],
    "steps": [
      {"title": "Two files, two jobs", "text": "auth/users.py finds users. auth/login.py decides if a login is allowed. One job per file keeps code easy to find and test."},
      {"title": "Finish find_user", "text": "In users.py add If with name not in users, then inside it Raise KeyError(name). After the If, Return users[name]."},
      {"title": "Import it", "text": "Select login.py. Its imports already say from auth.users import find_user. That line connects the two files."},
      {"title": "Write login", "text": "Replace the TODO: add Set variable user = find_user(users, name). Then If user.get('active') is not True → Raise PermissionError('account disabled')."},
      {"title": "Finish", "text": "After the If, Return user.get('password_hash') == password_hash. Check your work, Run tests, then read the advisor tips about folders."}
    ],
    "explain": "Real projects grow by adding files, then folders (packages). Rule of thumb: a file per topic, a folder per feature. Never store plain passwords; real apps compare password hashes.",
    "tests": [
      {"call": "login({'ana': {'active': True, 'password_hash': 'h1'}}, 'ana', 'h1')", "expect": "True"},
      {"call": "login({'ana': {'active': True, 'password_hash': 'h1'}}, 'ana', 'nope')", "expect": "False"},
      {"call": "login({'bo': {'active': False, 'password_hash': 'h2'}}, 'bo', 'h2')", "raises": "PermissionError"},
      {"call": "login({}, 'ghost', 'h3')", "raises": "KeyError"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Login", "modules": [
      {"path": "auth/users.py", "imports": [], "functions": [
        {"name": "find_user", "parameters": [{"name": "users", "type": "dict"}, {"name": "name", "type": "str"}], "returns": "dict", "requirements": [], "body": []}]},
      {"path": "auth/login.py", "imports": ["from auth.users import find_user"], "functions": [
        {"name": "login", "parameters": [{"name": "users", "type": "dict"}, {"name": "name", "type": "str"}, {"name": "password_hash", "type": "str"}], "returns": "bool", "requirements": ["Disabled accounts can never log in."], "body": [
          {"kind": "hole", "label": "Look up the user, refuse disabled accounts, compare hashes", "allowed_calls": ["find_user", "user.get"]}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Login", "modules": [
      {"path": "auth/users.py", "imports": [], "functions": [
        {"name": "find_user", "parameters": [{"name": "users", "type": "dict"}, {"name": "name", "type": "str"}], "returns": "dict", "requirements": [], "body": [
          {"kind": "branch", "condition": "name not in users", "body": [{"kind": "raise", "expression": "KeyError(name)"}], "otherwise": []},
          {"kind": "return", "expression": "users[name]"}]}]},
      {"path": "auth/login.py", "imports": ["from auth.users import find_user"], "functions": [
        {"name": "login", "parameters": [{"name": "users", "type": "dict"}, {"name": "name", "type": "str"}, {"name": "password_hash", "type": "str"}], "returns": "bool", "requirements": ["Disabled accounts can never log in."], "body": [
          {"kind": "assign", "target": "user", "expression": "find_user(users, name)"},
          {"kind": "branch", "condition": "user.get('active') is not True", "body": [{"kind": "raise", "expression": "PermissionError('account disabled')"}], "otherwise": []},
          {"kind": "return", "expression": "user.get('password_hash') == password_hash"}]}]}]}
  },
  {
    "id": "try-except",
    "title": "9 · Handle mistakes with try / except",
    "level": "Intermediate",
    "minutes": 10,
    "goal": "Turn text like '3' into a number, and give back a fallback instead of crashing when the text isn't a number.",
    "concepts": ["try / except", "default value", "raise"],
    "steps": [
      {"title": "See the default value", "text": "The inputs say fallback: int=0. The =0 is a default value: callers can leave fallback out, and it will be 0."},
      {"title": "Try the risky part", "text": "In the Try / Except block's try side, add Return with int(text). int('3') gives 3, but int('abc') raises ValueError."},
      {"title": "Catch the mistake", "text": "The except side runs only when ValueError happens. Add Return with fallback there."},
      {"title": "Check and run", "text": "Check your work, then Run tests. Try your own call too, like to_quantity('ten', 1)."}
    ],
    "explain": "try / except lets your code recover from an error you expect. Catch only the error you mean (ValueError here): catching everything can hide real bugs.",
    "tests": [
      {"call": "to_quantity('3')", "expect": "3"},
      {"call": "to_quantity(' 7 ')", "expect": "7"},
      {"call": "to_quantity('abc')", "expect": "0"},
      {"call": "to_quantity('abc', 5)", "expect": "5"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Quantities", "modules": [{"path": "parsing.py", "imports": [], "functions": [
      {"name": "to_quantity", "parameters": [{"name": "text", "type": "str"}, {"name": "fallback", "type": "int", "default": "0"}], "returns": "int", "requirements": ["Return fallback when text is not a whole number."], "body": [
        {"kind": "try", "body": [], "exception": "ValueError", "alias": "", "handler": [], "finally": []}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Quantities", "modules": [{"path": "parsing.py", "imports": [], "functions": [
      {"name": "to_quantity", "parameters": [{"name": "text", "type": "str"}, {"name": "fallback", "type": "int", "default": "0"}], "returns": "int", "requirements": ["Return fallback when text is not a whole number."], "body": [
        {"kind": "try", "body": [{"kind": "return", "expression": "int(text)"}], "exception": "ValueError", "alias": "",
         "handler": [{"kind": "return", "expression": "fallback"}], "finally": []}]}]}]}
  },
  {
    "id": "while-digits",
    "title": "10 · Repeat while: add up the digits",
    "level": "Intermediate",
    "minutes": 12,
    "goal": "Add up the digits of a whole number: 123 gives 1 + 2 + 3 = 6.",
    "concepts": ["while loop", "augmented assignment", "variable"],
    "steps": [
      {"title": "Read the loop", "text": "Repeat while runs its inside again and again as long as its condition, n > 0, is true. Something inside must make n smaller, or it never stops."},
      {"title": "Take the last digit", "text": "Replace the TODO with Set variable: total, choose += in the middle box, and type n % 10. n % 10 is the last digit (123 % 10 is 3), and += adds it on."},
      {"title": "Drop the last digit", "text": "Add another Set variable: n, choose //=, and type 10. n //= 10 divides and drops the remainder, so 123 becomes 12. This is what makes the loop stop."},
      {"title": "Check and run", "text": "Check your work, then Run tests. If you ever make a loop that never stops, Run stops it after 10 seconds."}
    ],
    "explain": "Use Repeat for each when you have a list to walk through, and Repeat while when you repeat until something changes. total += x is short for total = total + x.",
    "tests": [
      {"call": "digit_sum(123)", "expect": "6"},
      {"call": "digit_sum(1005)", "expect": "6"},
      {"call": "digit_sum(9)", "expect": "9"},
      {"call": "digit_sum(0)", "expect": "0"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "Digits", "modules": [{"path": "digits.py", "imports": [], "functions": [
      {"name": "digit_sum", "parameters": [{"name": "n", "type": "int"}], "returns": "int", "requirements": ["n is 0 or more."], "body": [
        {"kind": "assign", "target": "total", "expression": "0"},
        {"kind": "while", "condition": "n > 0", "body": [
          {"kind": "hole", "label": "Add the last digit to total, then drop it from n", "allowed_calls": []}]},
        {"kind": "return", "expression": "total"}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Digits", "modules": [{"path": "digits.py", "imports": [], "functions": [
      {"name": "digit_sum", "parameters": [{"name": "n", "type": "int"}], "returns": "int", "requirements": ["n is 0 or more."], "body": [
        {"kind": "assign", "target": "total", "expression": "0"},
        {"kind": "while", "condition": "n > 0", "body": [
          {"kind": "assign", "target": "total", "operator": "+=", "expression": "n % 10"},
          {"kind": "assign", "target": "n", "operator": "//=", "expression": "10"}]},
        {"kind": "return", "expression": "total"}]}]}]}
  },
  {
    "id": "break-early",
    "title": "11 · Stop early with break",
    "level": "Intermediate",
    "minutes": 8,
    "goal": "Find the first negative number in a list, or None if there isn't one, without looking further than you need to.",
    "concepts": ["break / continue", "loop", "condition"],
    "steps": [
      {"title": "Look at the plan", "text": "result starts as None (Python's word for 'nothing'). The loop walks through numbers, and the function returns result at the end."},
      {"title": "Spot a negative", "text": "Inside the loop add If with condition n < 0."},
      {"title": "Remember it and stop", "text": "Inside that If add Set variable: result = n, then a Stop loop block. Stop loop is Python's break: it leaves the loop right away."},
      {"title": "Check and run", "text": "Check your work, then Run tests. Without the Stop loop, you'd get the last negative instead of the first: try it and see."}
    ],
    "explain": "break leaves a loop early; its partner continue (Skip to next) jumps straight to the next item. Stopping as soon as you have the answer saves work on long lists.",
    "tests": [
      {"call": "first_negative([3, -1, -5])", "expect": "-1"},
      {"call": "first_negative([-4])", "expect": "-4"},
      {"call": "first_negative([1, 2])", "expect": "None"},
      {"call": "first_negative([])", "expect": "None"}
    ],
    "starter": {"format": "blockwise-plan-v1", "title": "First negative", "modules": [{"path": "search.py", "imports": [], "functions": [
      {"name": "first_negative", "parameters": [{"name": "numbers", "type": "list"}], "returns": "int | None", "requirements": [], "body": [
        {"kind": "assign", "target": "result", "expression": "None"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": []},
        {"kind": "return", "expression": "result"}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "First negative", "modules": [{"path": "search.py", "imports": [], "functions": [
      {"name": "first_negative", "parameters": [{"name": "numbers", "type": "list"}], "returns": "int | None", "requirements": [], "body": [
        {"kind": "assign", "target": "result", "expression": "None"},
        {"kind": "loop", "target": "n", "iterable": "numbers", "body": [
          {"kind": "branch", "condition": "n < 0", "body": [
            {"kind": "assign", "target": "result", "expression": "n"},
            {"kind": "break"}], "otherwise": []}]},
        {"kind": "return", "expression": "result"}]}]}]}
  }
];
