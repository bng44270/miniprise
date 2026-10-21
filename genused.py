allmods = {}
usedmods = []

with open("tmp/used_modules","r") as f:
  usedmods = f.readlines()

with open("tmp/available_modules","r") as f:
  line = f.readline().split(",")
  allmods[line[1]] = line[0]

with open("miniprise/conf/usedmods.py","w") as f:
  for lib in usedmods:
    f.write(f"from {allmods[lib]} import {lib}\n")
  
  f.write("UsedModules = []\n")
  for lib in usedmods:
    f.write(f"UseModules.append({lib})\n")