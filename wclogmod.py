#TODO LIST:
#3. Detailed mode!!!!
#4. Detailed mode requires filter of ALL parses by appropriate spec, fml
#5 Optimise loops?

import urllib.request
import urllib.parse
import re

def filter(row):   #Future function for filtering out healing spec from dps logs etc. Works with find funct. & metric
    if "holy" in row or "discipline" in row or "restoration" in row or "mistweaver" in row:
        return "hps"
    else:
        return "dps"

def dat2text(dat): #Convert URL to string list
    text=[]
    for line in dat:
        re=str(line)
        text.append(re)
    return text

def find(book): #Scan data for logs
    tot=0
    count=0
    for i, x in enumerate(book):
        if 'difficulty": 5' in book[i]:
            result=re.findall('\d+',book[i+4])
       #    if filter(book[i-7])=metric :   #Append for all specs
            tot+=float(result[0])           #Note: If top dps log is say, as healer spec
            count+=1                        #this will filter out. To fix use all parses
        if 'difficulty": 4' in book[i]:     #then find maximal parse BY proper spec
            break #we heroic now            #A lot of work, maybe later.
    if(tot!=0):
         res=format(float(tot/count),'.1f')
         return res
    else:
        return "No logs available"

def fillzones(zones,names,key): #Pull zone list and names from wclogs
    dat=urllib.request.urlopen("https://www.warcraftlogs.com/v1/zones?api_key="+key)
    book=dat2text(dat)
    for i, x in enumerate(book):
        if 'id":' in x:
            num=re.findall('\d+', x)
            if float(num[0]) < 999:
                zones.append(int(num[0]))
                name=book[i+1]
                name=name[:-5]
                name=name[19:]
                names.append(name)

def urlis(name, realm, reg): #Generic URL. Change rankings -> parses for ALL logs
    name=urllib.parse.quote_plus(name)
    url="https://www.warcraftlogs.com/v1/rankings/character/" + name + "/" + realm +"/" + reg + "?zone="
    return url

def addlist(url, metric, key, tiers, zones): #Add api key & zone number. Could remove to optimise. Future build?
    for zone in zones:
        tiers.append(url+str(zone)+"&metric="+metric+"&api_key="+key)

def finish():
    confirm=input("Type Y to search another character, or N to exit program: ")
    confirm=str(confirm)
    if confirm is "Y":
        word="stay"
        return word
    elif confirm is "N":
        word="exit"
        return word
    else:
        print("Invalid input")  #Could do recursion, but bugs out???

def filtercheck(keywords, zones, names):  #Removestuff
    for keyword in keywords:
        for i,x in enumerate(names):
            if keyword in x:
                names.pop(i)
                zones.pop(i)

def readessentials():
    file=open("config.dat","r")
    data=file.read()
    file.close()
    data=str(data)
    words=data.split()
    key=str(words[0])
    words.pop(0)
    i=0
    while i<len(words):
        if "," in words[i]:
            words[i]=words[i][:-1]
            i+=1
        else:
            words[i]+= " " + words[i+1]
            words.pop(i+1)
    return(key,words)

#Empty arrays for URLs
(key,filterwords)=readessentials()
zones=[]
names=[]
fillzones(zones,names,key)
filtercheck(filterwords,zones,names)
done="stay"
max=len(zones)
#Main block
while done is not "exit":

#User input block
    name=input("Enter name: ")
    while len(name.split()) > 1:  #Check for digits too?
        name=input("Invalid input, please enter a single word: ")

    realm=input("Enter realm: ")
    if " " in realm:   #Fix space block
        temp=realm.split()
        realm=""
        for word in temp:
            realm+=word+"-"
        realm=realm[:-1]

    regi=input("Enter region (EU/US): ") #
    while regi != "EU" and regi != "US" and regi !="eu" and regi !="us":
        regi=input("Invalid input, please type EU or US: ")

    limit=int(input("Enter how many raid tiers to display. Max is " + str(max) +": "))
    while limit > int(max):  #Check for strings? How stupid are people?
        limit=input("Invalid input, please enter an integer lower than " + str(max) +": ")
    #Still unsure about the limit thing, but pimi did ask...

    metric=input("Enter metric to display (type hps or dps): ")  #Just to define it initially
    while metric != "dps" and metric!= "hps":
        metric=input("Invalid input. Please type dps or hps: ")

    print("----------------") #Space, asthetics.
    tiers=[]
    addlist(urlis(name,realm,regi),metric, key, tiers, zones)

    for c in range(max-limit,max):
        dat = urllib.request.urlopen(tiers[c])   #Pull data
        book=dat2text(dat)
        print("Average for " + names[c] + " is: ")
        print(find(book))
        print("----------------")

    done=finish()
    while done is not "stay" and done is not "exit":  #Invalid input check
        done=finish()
