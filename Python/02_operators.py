# Operators: 
# 1=> Comparison Operators: >, >=, < , <=, =, ==
# 2=> Arithmetic Operators: +, -, *, /, //, %, **
# 3=> Logical Operators: and, or, not

biscuit = False
cold_drink = False
nimko = False

if biscuit and cold_drink and nimko:
    print("Shabash, jo baqaya bacha ha usy enjoy karo.")
elif biscuit and nimko:
    print("Shabash, bas ab baqaya wapis krdo 1")
elif biscuit and cold_drink:
    print("Shabash, bas ab baqaya wapis krdo 2")
elif cold_drink and nimko:
    print("Shabash, bas ab baqaya wapis krdo 3")
elif not biscuit and not nimko:
    print("Oh bad boy, you are too lazy. Go back and come back home after getting them.")
else:
    print("Please go back and try to find to cold_drink or Juice")








# if biscuit:
#     if cold_Drink:
#         if nimko:
#             print("Enter home")
#         else:
#             print("Please go back and find nimko")
#     else:
#         print("Please go back and find cold_Drink")
# else:
#     print("Please go back and find biscuit")