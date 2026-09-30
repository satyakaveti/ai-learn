print("Hello");

name = "Satya"
age = 30
weight = 68.56
isGood = False

print(name)
print(age)
print(weight)
print(isGood)

msg = f"Hello, {name}!, Your age is {age} and your weight is {weight}"
print(msg)

list1 = [1,2,3,4,5]
map1 = {"1":"one", "2":"two", "3":"three", "4":"four", "5":"five"};
tuple1 = ("one", "two", "three", "four", "five");
print(list1[0])
print(map1["1"])
print(tuple1[1])


for l in list1:
    print(f"No is : {l}",l)

def main():
    print("Running as the main program")

print(f"__name__ : {__name__}")

if __name__ == "__main__":
    main()


