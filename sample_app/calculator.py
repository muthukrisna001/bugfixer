"""
Sample calculator module with potential division by zero error
"""

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a, b):
        # This line can cause ZeroDivisionError
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = []

def main():
    calc = Calculator()
    
    # These operations work fine
    print(calc.add(10, 5))
    print(calc.subtract(10, 5))
    print(calc.multiply(10, 5))
    
    # This will cause ZeroDivisionError
    try:
        print(calc.divide(10, 0))
    except ZeroDivisionError as e:
        print(f"Error: {e}")
    
    print("History:", calc.get_history())

if __name__ == "__main__":
    main()
