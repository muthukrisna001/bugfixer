"""
Sample data processor module with potential IndexError
"""

class DataProcessor:
    def __init__(self):
        self.processed_count = 0
    
    def process_items(self, items, index):
        # This line can cause IndexError if index is out of range
        item = items[index]
        
        # Process the item
        processed_item = self.transform_item(item)
        self.processed_count += 1
        
        return processed_item
    
    def transform_item(self, item):
        if isinstance(item, str):
            return item.upper()
        elif isinstance(item, (int, float)):
            return item * 2
        else:
            return str(item)
    
    def process_all_items(self, items):
        results = []
        for i in range(len(items)):
            try:
                result = self.process_items(items, i)
                results.append(result)
            except IndexError as e:
                print(f"IndexError at index {i}: {e}")
                break
        return results
    
    def get_stats(self):
        return {"processed_count": self.processed_count}

def main():
    processor = DataProcessor()
    
    items = ["hello", "world", 42, 3.14]
    
    # This works fine
    for i in range(len(items)):
        result = processor.process_items(items, i)
        print(f"Processed item {i}: {result}")
    
    # This will cause IndexError
    try:
        result = processor.process_items(items, 10)  # Index 10 is out of range
    except IndexError as e:
        print(f"IndexError: {e}")
    
    print("Stats:", processor.get_stats())

if __name__ == "__main__":
    main()
