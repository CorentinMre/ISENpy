<p align="center"><img width="400" alt="Logo" src="https://raw.githubusercontent.com/CorentinMre/ISENpy/main/images/icon.jpg"></a></p>

<br/>


<h2 style="font-family: sans-serif; font-weight: normal;" align="center"><strong>An API for ISEN-OUEST</strong> (unofficial)</h2>


<br/>

<h2 style="font-family: sans-serif; font-weight: normal;" align="center"><strong>⚠️ In development !!</strong></h2>

## Dépendance

- requests
- bs4

## Usage


- `pip install ISENpy`

Here is an example script:

```python
import ISENpy

# Create a new instance of the ISENpy class
client = ISENpy.ISEN(
                        username="<username>", 
                        password="<password>",

                        cycle="<cycle>", #Ex. "CIR" 
                        annee="<annee>", #Ex. "1" 
                        ville="<ville>"  #Ex. "Caen"
                    )

#Check if the user is logged in
if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

#Example of use
classMember = client.classMember("CIR", "1", "Caen") #Get all the students of the class CIR1 Caen
print(classMember)

yourClass = client.classMember() #Get all the students of the class you are in
print(yourClass) 

userInfo = client.userInfo() #Get your user info
print(userInfo) 

#Get the webAurion object
webAurion = client.webAurion()

absence = webAurion.absences() #Get your absences
print(absence)

grade = webAurion.grades() #Get your grades
print(grade)

planning = webAurion.planning() #Get your planning of the week. Argument(Optional) is the beginning of the week (The Monday day) in the format "dd/mm/yyyy" Ex. "03/10/2022"
print(planning)

```

## Other example if you  want to get your planning in the calendar of your computer

- This script uses the 'ics' and 'datetime' modules
- `pip3 install ics datetime`

```python
import ISENpy
from ics import Calendar, Event
from datetime import datetime


client = ISENpy.ISEN(
                        username="<username>", 
                        password="<password>",

                        cycle="<cycle>", #Ex. "CIR" 
                        annee="<annee>", #Ex. "1" 
                        ville="<ville>"  #Ex. "Caen"
                    )

if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

webAurion = client.webAurion() #Get the webAurion object

planning = webAurion.planning() #Get your planning of the week. Argument(Optional) is the beginning of the week (The Monday day) in the format "dd/mm/yyyy" Ex. "03/10/2022"

c = Calendar()

for i in planning:
    e = Event()
    e.name = i["matiere"] + " - " + i["type"]
    e.description = i["description"] + " - intervenants: " + i["intervenants"] + " - classe: " + i["classe"]
    e.location = "salle: " + i["salle"]
    e.begin = datetime.fromisoformat(i["start"][:-2] + ':00')
    e.end = datetime.fromisoformat(i["end"][:-2] + ':00')
    c.events.add(e)

with open('week.ics', 'w') as my_file:
    my_file.writelines(c.serialize_iter())

```

- ***And now double click on the new 'week.ics' file***


## LICENSE

Copyright (c) 2022 CorentinMre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
