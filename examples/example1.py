print("start")

try:
    val = int(input("input number: "))
    tmp = 10 / val
    print(tmp)
except Exception as e:
    print(f"Error! {e}")

print("stop")
