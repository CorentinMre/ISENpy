
import requests
from bs4 import BeautifulSoup
import base64, json

#IMPORT 
from . import dataClasses


class ISEN:
    """
    A ISEN-OUEST client.
    Parameters
    ----------
    username : str
        Your username
    password : str
        Your password
    cycle : str
        Your cycle (CIR, CBIO, CENT, CEST, CBIAST, CSI)
    annee : str
        Your year (1, 2, 3)
    ville : str
        Your city (Caen, Brest, Nantes, Rennes)
    Attributes
    ----------
    logged_in : bool
        If the user is successfully logged in
    username : str
    password : str
    cycle : str
    annee : str
    ville : str
    """


    def __init__(self, username:str, password:str, cycle:str, annee:str, ville:str) -> None:
        #Set the user info
        self.username = username
        self.password = password
        self.cycle = cycle
        self.annee = annee
        self.ville = ville
        
        #check if the class exist
        self.__checkClassExist(self.cycle, self.annee, self.ville)

        #Create the session
        self.session = requests.Session()
        self.session.headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"}
        self.logged_in = self.__login()

    def __checkClassExist(self, cycle:str, annee:str, ville:str) -> bool:
        """
        Check if the class exist
        """


        cycles = ["CIR", "CBIO", "CENT", "CEST", "CBIAST", "CSI"]
        annees = ["1", "2", "3"]
        villes = ["Caen", "Brest", "Nantes", "Rennes"]

        if not cycle.upper() in cycles: raise Exception("Vous devez renseigner un cycle de la liste suivante: " + ', '.join(cycles))
        if not annee in annees: raise Exception("Vous devez renseigner une année de la liste suivante: " + ', '.join(annees))
        if not ville.capitalize() in villes: raise Exception("Vous devez renseigner une ville de la liste suivante: " + ', '.join(villes))
        
        return True


    def __login(self) -> bool:
        """
        Login to the session
        """

        #Get the login page
        req = self.session.get("https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login")
        
        #Get payload for login
        soup = BeautifulSoup(req.text,'html.parser')
        exec_value = soup.find("input",{"name":"execution"})["value"]

        #Set the payload
        payload = {
            "username":self.username,
            "password":self.password,
            "execution":exec_value,
            "_eventId":"submit",
            "geolocation":""
        }

        #Login
        req = self.session.post("https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login", data=payload)
        #Check if the login is successful
        if req.status_code == 200: return True
        else: return False


    def logout(self):
        """
        Logout from the session
        """

        #Disconnect from the session (not really necessary)
        self.session.get("https://auth.isen-ouest.fr/cas/logout?url=https://web.isen-ouest.fr/uPortal/Login")
    



    def webAurion(self):
        """
        Return the webAurion class, For check grades, absences, panning, etc...
        """
        #Get the webAurion informations file:"dataClasses.py"
        return dataClasses.WebAurion(self.session)
        

    def classMember(self, cycle:str = None, annee:str = None, ville:str = None) -> dict:
        """
        Args:
            cycle:str Optional
            annee:str Optional
            ville:str Optional
        
        Return:
            The class member
        """

        #Base url of trombinoscope
        baseUrl = "https://web.isen-ouest.fr/trombino"

        #Set payload for the request
        payload = {
            "nombre_colonnes":5,
            "choix_groupe": f"{self.cycle.upper() if not cycle else cycle.upper()}{self.annee if not annee else annee} {self.ville.capitalize() if not ville else ville.capitalize()} 2022-2023",
            "statut":"etudiant"
        }

        #Check if the class exist
        self.__checkClassExist(payload["choix_groupe"].split(" ")[0][:-1], payload["choix_groupe"].split(" ")[0][-1:], payload["choix_groupe"].split(" ")[1])

        #Get the class member
        self.session.get(baseUrl)
        req = self.session.post(f"{baseUrl}/fonctions/ajax/lister_etudiants.php",data=payload)
        soup = BeautifulSoup(req.text, "html.parser")
        eleves = soup.find_all("td",{"id":"tdTrombi"})
        #Create the dict of eleves
        result = {
            "nbEleves":len(eleves),
            "data": [{
                "nom":eleve.find("b").text,
                "mail":eleve.find("a").text,
                "avatarUrl":(baseUrl + eleve.find("img")["src"]).replace(" ./","/")} 
                for eleve in eleves]
        }
        #Return the dict of eleves
        return result
    


    def userInfo(self) -> dict:
        """
        Return your user info
        """
        
        #Get the user info
        req = self.session.get("https://web.isen-ouest.fr/uPortal/api/v5-1/userinfo")
        #Scrap the user info
        info  = json.loads(base64.urlsafe_b64decode(req.text.split(".")[1].encode()).decode())
        #Return the user info
        return info



if __name__ == "__main__":


    client = ISEN("", "", "CIR", "1", "Caen")

    if not client.logged_in:
        print("Identifiant ou mot de passe incorect !!")
        exit()


    #print(client.classMember("CIR", "1", "Caen")) #Get all the students of the class CIR1 Caen
    #print(client.classMember()) #Get all the students of the class you are in
    #print(client.userInfo()) #Get your user info

    webAurion = client.webAurion() #Get the webAurion object
    absence = webAurion.absences() #Get your absences
    grade = webAurion.grades() #Get your grades

    print(absence)
    print(grade)



    client.logout()
