
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

schoolReport = webAurion.getSchoolReport() #Get your school report
print(schoolReport)

# for download the report
#webAurion.downloadReport() #Download the school report. Argument(Optional) : 'path' (format : "path/to/file.pdf") and 'idReport' (format : "id")
