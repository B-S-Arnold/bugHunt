import sys
import os
from bugSprAI import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <target_file.py>")
        sys.exit(1)

    target_file = sys.argv[1]

    with open(target_file, "r") as f:
        code = f.read()

    fixer = BugFixer()
    fixed_code = fixer.fix_code(code)

    output_file = target_file.replace(".py", "_fixed.py")

    with open(output_file, "w") as f:
        f.write(fixed_code)

    print(f"✔ Fixed code saved to {output_file}")
