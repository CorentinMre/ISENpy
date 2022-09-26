
import requests
from bs4 import BeautifulSoup
import base64, json

#IMPORT 
import dataClasses


class ISEN:

    """
    argv:
        username:str
        password:str
        cycle:str
        annee:str
        ville:str
    """

    def __init__(self, username:str, password:str, cycle:str, annee:str, ville:str) -> None:
        self.username = username
        self.password = password
        self.cycle = cycle
        self.annee = annee
        self.ville = ville

        self._checkClasExist(self.cycle, self.annee, self.ville)

        self.session = requests.Session()
        self.session.headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"}

        self.logged_in = self._login()

    def _checkClasExist(self, cycle:str, annee:str, ville:str) -> bool:


        cycles = ["CIR", "CBIO", "CENT", "CEST", "CBIAST", "CSI"]
        annees = ["1", "2", "3"]
        villes = ["Caen", "Brest", "Nantes", "Rennes"]

        if not cycle.upper() in cycles: raise Exception("Vous devez renseigner un cycle de la liste suivante: " + ', '.join(cycles))
        if not annee in annees: raise Exception("Vous devez renseigner une année de la liste suivante: " + ', '.join(annees))
        if not ville.capitalize() in villes: raise Exception("Vous devez renseigner une ville de la liste suivante: " + ', '.join(villes))
        
        return True


    def _login(self) -> bool:


        req = self.session.get("https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login")

        soup = BeautifulSoup(req.text,'html.parser')

        exec_value = soup.find("input",{"name":"execution"})["value"]

        payload = {
            "username":self.username,
            "password":self.password,
            "execution":exec_value,
            "_eventId":"submit",
            "geolocation":""
        }

        req = self.session.post("https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login", data=payload)
        if req.status_code == 200: return True
        else: return False


    def logout(self):

        self.session.get("https://auth.isen-ouest.fr/cas/logout?url=https://web.isen-ouest.fr/uPortal/Login")
    



    def webAuron(self):

        return dataClasses.WebAurion(self.session)
        

    def classMember(self, cycle:str = None, annee:str = None, ville:str = None):

        baseUrl = "https://web.isen-ouest.fr/trombino"

        

        payload = {
            "nombre_colonnes":5,
            "choix_groupe": f"{self.cycle.upper() if not cycle else cycle.upper()}{self.annee if not annee else annee} {self.ville.capitalize() if not ville else ville.capitalize()} 2022-2023",
            "statut":"etudiant"
        }

        self._checkClasExist(payload["choix_groupe"].split(" ")[0][:-1], payload["choix_groupe"].split(" ")[0][-1:], payload["choix_groupe"].split(" ")[1])

        

        self.session.get(baseUrl)
        req = self.session.post(f"{baseUrl}/fonctions/ajax/lister_etudiants.php",data=payload)
        soup = BeautifulSoup(req.text, "html.parser")

        eleves = soup.find_all("td",{"id":"tdTrombi"})

        result = {
            "nbEleves":len(eleves),
            "data": [{
                "nom":eleve.find("b").text,
                "mail":eleve.find("a").text,
                "avatarUrl":(baseUrl + eleve.find("img")["src"]).replace(" ./","/")} 
                for eleve in eleves]
        }

        return result
    


    def userInfo(self) -> dict:
        
        req = self.session.get("https://web.isen-ouest.fr/uPortal/api/v5-1/userinfo")

        info  = json.loads(base64.urlsafe_b64decode(req.text.split(".")[1].encode()).decode())

        return info



if __name__ == "__main__":


    client = ISEN("", "", "CIR", "1", "Caen")

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
