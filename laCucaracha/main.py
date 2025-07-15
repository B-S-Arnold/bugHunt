from config import BugInjectionConfig, BugSeverity
from injector import BugInjector

if __name__ == "__main__":
    code = '''
import math

def square(x):
    return x * x
'''

    config = BugInjectionConfig(bugs_per_lines=3, severity=BugSeverity.MODERATE)
    injector = BugInjector(config)
    print(injector.inject_bugs(code))