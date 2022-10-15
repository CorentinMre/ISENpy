
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
