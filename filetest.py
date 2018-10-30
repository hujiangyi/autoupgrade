cmdfile = open('./collectDataCmd.txt', "r")
for line in cmdfile.readlines():
    print line.strip()