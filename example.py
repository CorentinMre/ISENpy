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
print(f"nb of member : {classMember.nbMembers}")
for student in classMember.data:
    print(f"{student.name} | {student.mail} | {student.avatar_url}")

# or more simply

# print(classMember)
# print(f"nb of member : {classMember['nbMembers']}")
# for student in classMember['data']:
#     print(f"{student['name']} | {student['mail']} | {student['avatar_url']}")


##########################################

userInfo = client.userInfo() #Get your user info
print(userInfo) 


##########################################

webAurion = client.webAurion() # WebAurion initialization

##########################################

grades = webAurion.grades()

print(grades.average)
for grade in grades.data:
    print(f"{grade.date} : {grade.grade} ({grade.name} | {grade.instructors}), {grade.appreciation}, {grade.absence}")

# Or more simply

# print(grades)
# print(grades["data"][0]["date"]) # ... (use like a dict)



##########################################

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

##########################################

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

##########################################

schoolReport = webAurion.getSchoolReport()

print(schoolReport.nbReports)
for report in schoolReport.data:
    print(f"{report.name} : {report.id}")

# Or more simply

# print(schoolReport)
# print(schoolReport["data"][0]["name"]) # ... (use like a dict)