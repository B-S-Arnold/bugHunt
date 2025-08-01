from bugSprAI import *

if __name__ == "__main__":
    with open("example_buggy.py") as f:
        code = f.read()

    fixer = BugFixer()
    fixed = fixer.fix_code(code)

    print("------ FIXED CODE ------")
    print(fixed)
