from PyQt5.QtWidgets import  (QDialog, QApplication, QComboBox,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout, QWidget, QMainWindow, QMessageBox)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon
import sys
import urllib.request
import urllib.parse
import re

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
max=len(zones)

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt absolute positioning - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 440
        self.height = 280
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label = QLabel('Python', self)
        self.label.move(50,50)

        self.show()

class Dialog(QDialog):
    NumGridRows = 5
    NumButtons = 4

    def __init__(self):
        super(Dialog, self).__init__()
        self.createFormGroupBox()

        btn = QPushButton("OK",self)
        btn.clicked.connect(self.on_click)

        #btn.accepted.connect(self.accept)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(btn)
        self.setLayout(mainLayout)
        self.setWindowTitle("WCLogs Scanner")

    def createFormGroupBox(self):

        metric = QLabel('Metric')
        metric.setToolTip("Chose to display dps or hps logs")
        limit = QLabel('Limit')
        limit.setToolTip("How many raid tiers to display, from most recent. Maximum is " + str(max))

        self.nameEdit = QLineEdit()
        self.realmEdit = QLineEdit()
        self.limitEdit = QSpinBox()
        self.limitEdit.setMaximum(max)
        self.limitEdit.setMinimum(1)

        self.regionEdit=QComboBox()
        self.regionEdit.addItem("EU")
        self.regionEdit.addItem("US")

        self.metricEdit=QComboBox()
        self.metricEdit.addItem("dps")
        self.metricEdit.addItem("hps")

        self.formGroupBox = QGroupBox("Form layout")
        layout = QFormLayout()
        layout.addRow(QLabel("Name:"), self.nameEdit)
        layout.addRow(QLabel("Realm:"), self.realmEdit)
        layout.addRow(QLabel("Region:"), self.regionEdit)
        layout.addRow(metric, self.metricEdit)
        layout.addRow(limit, self.limitEdit)
        self.formGroupBox.setLayout(layout)

    @pyqtSlot()
    def on_click(self):

        realm=self.realmEdit.text()
        if " " in realm:   #Fix space block
            temp=realm.split()
            realm=""
            for word in temp:
                realm+=word+"-"
            realm=realm[:-1]

        tiers=[]
        addlist(urlis(self.nameEdit.text(),realm,self.regionEdit.currentText()),self.metricEdit.currentText(), key, tiers, zones)

        output=[]
        for c in range(max-int(self.limitEdit.text()),max):
            dat = urllib.request.urlopen(tiers[c])   #Pull data
            book=dat2text(dat)
            output.append("Average for " + names[c] + " is: \n")
            output.append(find(book))
            output.append("\n ------------------- \n")
#AND BIGBOY CODE ENDS HERE
        result=" ".join(str(x) for x in output)
        QMessageBox.question(self, 'Output', result , QMessageBox.Ok, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Dialog()
sys.exit(dialog.exec_())
