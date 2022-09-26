
import ISENpy


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



print(client.classMember("CIR", "1", "Caen")) #Get all the students of the class CIR1 Caen
print(client.classMember()) #Get all the students of the class you are in
print(client.userInfo()) #Get your user info

webAurion = client.webAuron() #Get the webAurion object
grade = webAurion.grades() #Get your grades

print(grade)


client.logout()
