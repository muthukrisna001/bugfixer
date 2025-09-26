"""
Sample user manager module with potential AttributeError
"""

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.active = True
    
    def deactivate(self):
        self.active = False
    
    def activate(self):
        self.active = True

class UserManager:
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, name, email):
        user = User(name, email)
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id):
        return self.users.get(user_id)  # This can return None
    
    def get_user_name(self, user_id):
        user = self.get_user(user_id)
        # This line can cause AttributeError if user is None
        return user.name
    
    def get_user_email(self, user_id):
        user = self.get_user(user_id)
        # This line can also cause AttributeError if user is None
        return user.email
    
    def is_user_active(self, user_id):
        user = self.get_user(user_id)
        if user:
            return user.active
        return False
    
    def list_users(self):
        return list(self.users.keys())

def main():
    manager = UserManager()
    
    # Add some users
    manager.add_user("1", "John Doe", "john@example.com")
    manager.add_user("2", "Jane Smith", "jane@example.com")
    
    # This works fine
    name = manager.get_user_name("1")
    print(f"User 1 name: {name}")
    
    # This will cause AttributeError
    try:
        name = manager.get_user_name("999")  # User doesn't exist, returns None
    except AttributeError as e:
        print(f"AttributeError: {e}")
    
    print("All users:", manager.list_users())

if __name__ == "__main__":
    main()
