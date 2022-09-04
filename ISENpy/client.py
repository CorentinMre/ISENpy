
import requests
from bs4 import BeautifulSoup


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

        cycles = ["CIR", "CBIO", "CENT", "CEST", "CBIAST", "CSI"]
        annees = ["1", "2", "3"]
        villes = ["Caen", "Brest", "Nantes", "Rennes"]

        if not self.cycle.upper() in cycles: raise Exception("Vous devez renseigner un cycle de la liste suivante: " + ', '.join(cycles))
        if not self.annee in annees: raise Exception("Vous devez renseigner une année de la liste suivante: " + ', '.join(annees))
        if not self.ville.capitalize() in villes: raise Exception("Vous devez renseigner une ville de la liste suivante: " + ', '.join(villes))

        self.session = requests.Session()
        self.session.headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"}

        self.logged_in = self._login()


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
        #print(req.text)
        if req.status_code == 200: return True
        else: return False


    def logout(self):

        self.session.get("https://auth.isen-ouest.fr/cas/logout?url=https://web.isen-ouest.fr/uPortal/Login")

    def webAurion(self):

        req = self.session.get("https://web.isen-ouest.fr/webAurion/?portail=false")

        soup = BeautifulSoup(req.text,'html.parser')

        self.nbAbsences = soup.find("span",{"class":"texteIndicateur"})

        return req.text
    
    def maClasse(self):

        baseUrl = "https://web.isen-ouest.fr/trombino"


        payload = {
            "nombre_colonnes":5,
            "choix_groupe": f"{self.cycle.upper()}{self.annee} {self.ville} 2022-2023",
            "statut":"etudiant"
        }

        

        self.session.get(baseUrl)
        req = self.session.post(f"{baseUrl}/fonctions/ajax/lister_etudiants.php",data=payload)
        soup = BeautifulSoup(req.text, "html.parser")

        eleves = soup.find_all("td",{"id":"tdTrombi"})

        result = {
            "nbEleves":len(eleves),
            "data": [{
                "nom":eleve.find("b").text,
                "mail":eleve.find("a").text,
                "avatar":(baseUrl + eleve.find("img")["src"]).replace(" ./","/")} 
                for eleve in eleves]
        }

        return result
    
    #def _notif(self):

        #req = self.session.get("https://web.isen-ouest.fr/NotificationPortlet/api/v2/notifications")
        #print(self.session.cookies)
        #return req.text

if __name__ == "__main__":

    client = ISEN("", "", "", "", "")

    if not client.logged_in:
        print("Identifiant ou mot de passe incorect !!")
        exit()


    print(client.webAurion())


    client.logout()
