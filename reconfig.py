f=open("config.dat", "w")
key=input("Enter API key: ")
f.write(key)
f.write("\n")

ignore=input("Add names or parts of names to ignore (Case sensitive). \n Different words seperated by commas, including last word e.g.: \n Mythic+, Mage Tower, Callenge Modes,: ")
f.write(ignore)
