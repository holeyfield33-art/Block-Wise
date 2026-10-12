// Blockwise Studio lessons. Each lesson's `solution` is a valid blockwise-plan-v1 plan
// (tests/test_studio.py checks that it compiles). `starter` is the guided, partly
// pre-filled version; "blank" mode keeps only the files and function signatures.
window.BLOCKWISE_LESSONS = [
  {
    "id": "first-function",
    "title": "1 · Your first function",
    "level": "Beginner",
    "minutes": 5,
    "goal": "Write a function that takes a name and gives back a greeting.",
    "concepts": ["function", "parameter", "return"],
    "steps": [
      {"title": "Look at the function card", "text": "A function is a named recipe. This one is called greet and takes one input (a parameter) called name of type str (text)."},
      {"title": "Add a Return block", "text": "Click '+ add a block' inside greet and choose Return. A return hands a value back to whoever called the function."},
      {"title": "Fill in what to return", "text": "Type f'Hello, {name}!' in the Return block. The f before the quotes lets you drop the name into the text."},
      {"title": "Check your work", "text": "Press Check my work. Then read the Python on the right: that is exactly what you built."}
    ],
    "explain": "Every function has a name, inputs in brackets, and usually a return. greet('Ana') now gives back 'Hello, Ana!'.",
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
    "concepts": ["if", "else", "condition", "boolean"],
    "steps": [
      {"title": "Add an If block", "text": "Inside can_vote, add an If / Else block. Its condition is a question with a yes/no answer. Type age >= 18."},
      {"title": "Fill the 'if' side", "text": "Inside the if part, add Return with True. This runs only when the condition is true."},
      {"title": "Fill the 'else' side", "text": "Inside the else part, add Return with False. This runs when the condition is false."},
      {"title": "Check, then compare", "text": "Check your work. Notice the boundary: 18 counts, because >= means 'greater than or equal'."}
    ],
    "explain": "If / Else splits your program into two paths. Getting the boundary right (>= versus >) is one of the most common bugs in real code.",
    "starter": {"format": "blockwise-plan-v1", "title": "Voting age", "modules": [{"path": "voting.py", "imports": [], "functions": [
      {"name": "can_vote", "parameters": [{"name": "age", "type": "int"}], "returns": "bool", "requirements": ["True for age 18 and over, else False."], "body": [
        {"kind": "branch", "condition": "age >= 18", "body": [], "otherwise": []}]}]}]},
    "solution": {"format": "blockwise-plan-v1", "title": "Voting age", "modules": [{"path": "voting.py", "imports": [], "functions": [
      {"name": "can_vote", "parameters": [{"name": "age", "type": "int"}], "returns": "bool", "requirements": ["True for age 18 and over, else False."], "body": [
        {"kind": "branch", "condition": "age >= 18", "body": [{"kind": "return", "expression": "True"}],
         "otherwise": [{"kind": "return", "expression": "False"}]}]}]}]}
  },
  {
    "id": "guard-inputs",
    "title": "3 · Guard your inputs",
    "level": "Beginner+",
    "minutes": 10,
    "goal": "Reject bad amounts with an error, then use that check inside another function.",
    "concepts": ["raise", "validation", "calling functions", "guard clause"],
    "steps": [
      {"title": "Write the check", "text": "In require_positive add If with condition amount <= 0. Inside it add Raise with ValueError('amount must be positive')."},
      {"title": "Finish the check", "text": "After the If (not inside it), add Return with None. The function only reaches this line when the amount is fine."},
      {"title": "Use the check", "text": "In order_total, add a Check (validate) block first: require_positive(quantity). Checking first is called a guard clause."},
      {"title": "Do the work", "text": "Then add Return with quantity * price. Check your work."}
    ],
    "explain": "Small check functions can be reused everywhere. Putting them first means bad data stops at the door instead of causing bugs deep inside.",
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
    "title": "4 · Loops: shopping cart total",
    "level": "Intermediate",
    "minutes": 12,
    "goal": "Add up price × quantity for every item in a cart, skipping items with no quantity.",
    "concepts": ["loop", "variable", "nesting", "accumulator"],
    "steps": [
      {"title": "Start a running total", "text": "Add Set variable: total = 0. This is the accumulator that grows as we loop."},
      {"title": "Loop over the items", "text": "Add Repeat for each with item in items. Everything inside runs once per item."},
      {"title": "Nest a decision", "text": "Inside the loop add If with condition item['qty'] > 0. This is nesting: a block inside a block inside a block."},
      {"title": "Grow the total", "text": "Inside that If add Set variable: total = total + item['price'] * item['qty']."},
      {"title": "Give back the answer", "text": "After the loop (back at the function level) add Return total. Check your work."}
    ],
    "explain": "Loop + accumulator is one of the most-used patterns in programming. If nesting gets deeper than about 3 levels, the advisor will suggest a helper function.",
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
    "id": "split-files",
    "title": "5 · Split code into files: login check",
    "level": "Intermediate",
    "minutes": 15,
    "goal": "Keep user lookup in one file and login logic in another, connected by an import.",
    "concepts": ["modules (files)", "folders", "import", "separation of concerns"],
    "steps": [
      {"title": "Two files, two jobs", "text": "auth/users.py finds users. auth/login.py decides if a login is allowed. One job per file keeps code easy to find and test."},
      {"title": "Finish find_user", "text": "In users.py add If with name not in users, then inside it Raise KeyError(name). After the If, Return users[name]."},
      {"title": "Import it", "text": "Select login.py. Its imports already say from auth.users import find_user. That line connects the two files."},
      {"title": "Write login", "text": "Add Set variable user = find_user(users, name). Then If user.get('active') is not True → Raise PermissionError('account disabled')."},
      {"title": "Finish", "text": "After the If, Return user.get('password_hash') == password_hash. Check your work, then read the advisor tips about folders."}
    ],
    "explain": "Real projects grow by adding files, then folders (packages). Rule of thumb: a file per topic, a folder per feature. Never store plain passwords; real apps compare password hashes.",
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
  }
];
