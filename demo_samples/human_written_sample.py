def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# quick tests
print(fib(10))
print(quicksort([3,6,8,10,1,2,1]))

def parse_config(file_path):
    # TODO: add error handling
    with open(file_path) as f:
        return f.read()

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.active = True
    
    def deactivate(self):
        self.active = False
