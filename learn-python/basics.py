import module
from module import sum

# vartiables
print("======> 1. Variables ")
str = "Satya"
a = 10
b = 10.25
c = True

print(type(str))
print(type(a))
print(type(b))
print(type(c))

print(str)
print(a)
print(b)
print(c)

print("\n \n2. Collections ")
mylist = [1, 2, 3];
mySet = {"a", "b", "c"};
myDict = {"1:a", "2:b", "3:c"};

print(len(mylist))
print(mylist)
print(mySet)
print(myDict)


name = "Satya"
age = 28
message = f"{name} is {age} years old"   # f-string: put values directly inside {}
print(message)


score = 57;
if score>90:
    print("Distinction")
elif score>=70:
    print("1st CLASS")
elif score>=60:
    print("2nd CLASS")
elif score>=50:
    print("3rd CLASS")
elif score>=40:
    print("Just Pass")
else:
    print("YOU FAILED!!!")


numbers = [1, 2, 3, 4, 5];
for x in numbers:
    print(x)


def greet(name, greeting):
    return f"{greeting}, {name}!"


print(greet("Satya", "Hi"))



def show_all(*args, **kwargs):
    print("args:", args)        # a tuple of all extra positional values
    print("kwargs:", kwargs)    # a dict of all extra named values

show_all(1, 2, 3, name="Rahul", city="Pune", age=27)
# args: (1, 2, 3)
# kwargs: {'name': 'Rahul', 'city': 'Pune'}


print(f"Sum is {module.sum(10,50)}")

print(f"Only Sum is {sum(50,50)}")

def main():
    print("Running as the main program")

if __name__ == "__main__":
    main()


try:
    result = 10 / 0
except ZeroDivisionError as ex:
    print(f"Caught error: {ex}")
finally:
    print("This always runs")


class SatyaError:
    pass





def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"log_call: Calling {func.__name__} with {args}")
        return func(*args, **kwargs)
    return wrapper

@log_call
def add(a, b):
    print(f"Adding {a} and {b}")
    return a + b
    return a + b

print(add(3, 4))


import requests
print("https://dummyjson.com/recipes")
response = requests.get("https://dummyjson.com/recipes")
data = response.json()   # parses the JSON response into a Python dict
print(data["recipes"])


import asyncio

async def fetch_data(name, delay):
    print(f"Starting {name}")
    await asyncio.sleep(delay)   # simulates waiting for an API call
    print(f"Finished {name}")
    return f"{name} result"

async def main():
    results = await asyncio.gather(
        fetch_data("Task A", 1),
        fetch_data("Task B", 1),
    )
    print(results)

asyncio.run(main())


from pathlib import Path

folder = Path("/Users/satyakaveti/Downloads").expanduser()
print(folder)
folder.mkdir(parents=True, exist_ok=True)

for file in folder.glob("*.txt"):
    print(file.name)