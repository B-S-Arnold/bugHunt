import os
from bug_fixer3 import BugFixer

def main():
    target_file = os.path.join("..", "testCode", "example_buggy.py")

    with open(target_file, "r") as f:
        code = f.read()

    fixer = BugFixer()
    fixed_code, logs = fixer.fix_code(code)

    fixed_path = target_file.replace(".py", "_fixed.py")
    with open(fixed_path, "w") as f:
        f.write(fixed_code)

    log_path = target_file + "_fix_log.txt"
    with open(log_path, "w") as f:
        f.write(f"Fix Log ({len(logs)} changes):\n\n")
        for log in logs:
            f.write(
                f"- Line {log['line_number']}: \"{log['original']}\" → \"{log['fixed']}\" (type: {log['fix_type']})\n"
            )

    print("✅ Bug fix complete.")
    print(f"➡️ Fixed file: {fixed_path}")
    print(f"📝 Log: {log_path}")

if __name__ == "__main__":
    main()

