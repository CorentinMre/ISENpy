<br>
<p align="center"><img width="400" alt="Logo" src="https://raw.githubusercontent.com/CorentinMre/ISENpy/main/images/icon.jpg"></a></p>

<br/>


<h2 style="font-family: sans-serif; font-weight: normal;" align="center"><strong>An API for ISEN-OUEST</strong></h2>


<br/>

<h2 style="font-family: sans-serif; font-weight: normal;" align="center"><strong>⚠️ Unofficial !!</strong></h2>

[![pypi version](https://img.shields.io/pypi/v/ISENpy.svg)](https://pypi.org/project/ISENpy/)
[![python version](https://img.shields.io/pypi/pyversions/ISENpy.svg)](https://pypi.org/project/ISENpy/)
[![license](https://img.shields.io/pypi/l/ISENpy.svg)](https://pypi.org/project/ISENpy/)

## Description
A python API wrapper for ISEN-OUEST, with webAurion information like calendar, grades, absences...


## Dependencies

- requests
- bs4
- lxml

## Usage


- `pip3 install ISENpy`

Here is an example script:

```python
import ISENpy

# Create a new instance of the ISENpy class
client = ISENpy.ISEN(
                        username="<username>", 
                        password="<password>",
                    )

#Check if the user is logged in
if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

#Example of use
classMember = client.classMember("CIR", "1", "Caen") #Get all the students of the class CIR1 Caen
print(classMember)

userInfo = client.userInfo() #Get your user info
print(userInfo) 

#Get the webAurion object
webAurion = client.webAurion()

absence = webAurion.absences() #Get your absences
print(absence)

grade = webAurion.grades() #Get your grades
print(grade)

planning = webAurion.planning() #Get your planning of the week. Argument(Optional) : 'start_date' (format : "dd-mm-yyyy") and 'end_date' (format : "dd-mm-yyyy")
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
                    )

if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

webAurion = client.webAurion() #Get the webAurion object

planning = webAurion.planning() #Get your planning of the week. Argument(Optional) : 'start_date' (format : "dd-mm-yyyy") and 'end_date' (format : "dd-mm-yyyy")

c = Calendar()

for i in planning:
    e = Event()
    e.name = i["matiere"] + " - " + i["type"]
    e.description = i["description"] + " - intervenants: " + i["intervenants"] + " - classe: " + i["classe"]
    e.location = i["salle"]
    e.begin = datetime.fromisoformat(i["start"][:-2] + ':00')
    e.end = datetime.fromisoformat(i["end"][:-2] + ':00')
    c.events.add(e)

with open('week.ics', 'w') as my_file:
    my_file.writelines(c.serialize_iter())

```

- ***And now double click on the new 'week.ics' file***


## Example for get Moodle Resources

```python
import ISENpy

client = ISENpy.ISEN(
                        username="<username>", 
                        password="<password>",
                    )
if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

moodle = client.moodle() #Get the moodle object

links = moodle.getCoursesLink() #Get all links of your courses

for link in links:
    resources = moodle.getCourseResources(links[link]) #Get all the assignments
    print(link + " :\n")
    print(resources)
    print("------------------------------------------------------------------")

```


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
