
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


print(client.maClasse())


client.logout()
