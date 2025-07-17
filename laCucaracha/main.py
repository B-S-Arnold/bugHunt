import os
from config import BugInjectionConfig, BugSeverity
from injector import BugInjector

def main():
    # Point to the file in ../testCode/
    target_file = os.path.join("..", "testCode", "example.py")
    
    with open(target_file, "r") as f:
        original_code = f.read()

    config = BugInjectionConfig(bugs_per_lines=3, severity=BugSeverity.MODERATE, seed=None)
    injector = BugInjector(config)

    # Inject and log
    buggy_code = injector.inject_bugs(original_code, source_path=target_file)

    # Save buggy code next to the original
    buggy_path = target_file.replace(".py", "_buggy.py")
    with open(buggy_path, "w") as f:
        f.write(buggy_code)

    print("✅ Bug injection complete.")
    print(f"➡️ Modified: {buggy_path}")
    print(f"📝 Log: {target_file}_bug_log.txt")

if __name__ == "__main__":
    main()