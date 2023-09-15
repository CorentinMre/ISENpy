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


- `pip3 install ISENpy -U`

Here is an example script:

```python
import ISENpy

# Create a new instance of the ISENpy class
client = ISENpy.Client(
                        username="<username>", 
                        password="<password>",
                    )

#Check if the user is logged in
if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

#Example of use
classMember = client.classMember("CIR", "1", "Caen") #Get all the students of the class CIR1 Caen
print(f"nb of member : {classMember.nbMembers}")
for student in classMember.data:
    print(f"{student.name} | {student.mail} | {student.avatar_url}")

# or more simply

# print(classMember)
# print(f"nb of member : {classMember['nbMembers']}")
# for student in classMember['data']:
#     print(f"{student['name']} | {student['mail']} | {student['avatar_url']}")


userInfo = client.userInfo() #Get your user info
print(userInfo) 

```

## Example for get your grades

```python

...

webAurion = client.webAurion()

grades = webAurion.grades()

print(grades.average)
for grade in grades.data:
    print(f"{grade.date} : {grade.grade} ({grade.name} | {grade.instructors}), {grade.appreciation}, {grade.absence}")

# Or more simply

# print(grades)
# print(grades["data"][0]["date"]) # ... (use like a dict)

```

## Example for get your absences

```python

...

webAurion = client.webAurion()

absences = webAurion.absences()

print(absences.nbAbsences)
print(absences.time)
for absence in absences.data:
    print(f" \
            {absence.date} : {absence.reason} \
            ({absence.duration} | {absence.schedule} | {absence.course} | \
            {absence.instructor} | {absence.subject}) \
        ")
    
# Or more simply

# print(absences)
# print(absences["data"][0]["date"]) # ... (use like a dict)

```

## Example for get your planning

```python

...

webAurion = client.webAurion()

planning = webAurion.planning()

for event in planning.data:
    print(f" \
            {event.subject} ({event.start} | {event.end} , \
            {event.start_time} | {event.end_time},  {event.instructor} | {event.room}), \
            {event.type}, {event.class_name}, {event.description}, {event.class_info} \
        ")
    
# Or more simply

# print(planning)
# print(planning["data"][0]["subject"]) # ... (use like a dict)

```

## Example for get your school report

```python

...

webAurion = client.webAurion()

schoolReport = webAurion.getSchoolReport()

print(schoolReport.nbReports)
for report in schoolReport.data:
    print(f"{report.name} : {report.id}")

# Or more simply

# print(schoolReport)
# print(schoolReport["data"][0]["name"]) # ... (use like a dict)


```

## And for download your school report

```python

...

webAurion = client.webAurion()

webAurion.downloadReport() #Download all your school report with the default name

# if you want only one report

# webAurion.downloadReport(idReport="report_id") 
# Download the report with the id "report_id" with the default name (you have the id with the schoolReport object Ex. schoolReport = webAurion.getSchoolReport() ) 

```

## Other example if you  want to get your planning in the calendar of your computer

- This script uses the 'ics' and 'datetime' modules
- `pip3 install ics datetime`

```python
import ISENpy
from ics import Calendar, Event
from datetime import datetime


client = ISENpy.Client(
                        username="<username>", 
                        password="<password>",
                    )

if not client.logged_in:
    print("Identifiant ou mot de passe incorect !!")
    exit()

webAurion = client.webAurion() #Get the webAurion object

planning = webAurion.planning() #Get your planning of the week. Argument(Optional) : 'start_date' (format : "dd-mm-yyyy") and 'end_date' (format : "dd-mm-yyyy")

c = Calendar()

for event in planning.data:
    e = Event()
    e.name = event.subject + " - " + event.type
    e.description = event.description + " - intervenants: " + event.instructors + " - classe: " + event.class_info
    e.location = event.room
    e.begin = datetime.fromisoformat(event.start[:-2] + ':00')
    e.end = datetime.fromisoformat(event.end[:-2] + ':00')
    c.events.add(e)

with open('week.ics', 'w') as my_file:
    my_file.writelines(c.serialize_iter())

```

- ***And now double click on the new 'week.ics' file***


## Example for get Moodle Resources

```python
import ISENpy

client = ISENpy.Client(
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

Copyright (c) 2022-2023 CorentinMre

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
