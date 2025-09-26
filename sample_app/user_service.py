"""
Sample user service module with potential KeyError
"""

class UserService:
    def __init__(self):
        self.users = {
            "123": {"name": "John Doe", "email": "john@example.com"},
            "456": {"name": "Jane Smith", "email": "jane@example.com"}
        }
    
    def get_user(self, request):
        # This line can cause KeyError if 'user_id' is not in request.data
        user_id = request.data['user_id']
        
        if user_id in self.users:
            return self.users[user_id]
        else:
            return None
    
    def create_user(self, user_data):
        user_id = str(len(self.users) + 1)
        self.users[user_id] = user_data
        return user_id
    
    def update_user(self, user_id, user_data):
        if user_id in self.users:
            self.users[user_id].update(user_data)
            return True
        return False
    
    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False

class Request:
    def __init__(self, data):
        self.data = data

def main():
    service = UserService()
    
    # This works fine
    request1 = Request({"user_id": "123"})
    user = service.get_user(request1)
    print(f"User found: {user}")
    
    # This will cause KeyError
    try:
        request2 = Request({"username": "john"})  # Missing 'user_id' key
        user = service.get_user(request2)
    except KeyError as e:
        print(f"KeyError: {e}")

if __name__ == "__main__":
    main()
