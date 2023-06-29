import requests
from bs4 import BeautifulSoup
import base64
import json

# IMPORT
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
    Attributes
    ----------
    logged_in : bool
        If the user is successfully logged in
    username : str
    password : str
    Functions
    ----------
    classMember(cycle:str, annee:str, ville:str) -> dict
    webAurion() -> dataClasses.WebAurion
        grades() -> dict of grades of the user
        absences() -> list of dict of absences of the user
        planning() -> list of dict of planning of the user
            start_date:str Optional -> The start of the planning (format : "dd-mm-yyyy")
            end_end:str Optional -> The end of the planning  (format : "dd-mm-yyyy")

        getOtherPlanning() -> list of dict of planning of the user
            start_date:str Optional -> The start of the planning (format : "dd-mm-yyyy")
            end_end:str Optional -> The end of the planning  (format : "dd-mm-yyyy")
            classPlanning:str -> The class planning you want to get (Default: "CIR")
            classCity:str -> The class city you want to get (Default: "Caen")
            classYear:str -> The class year you want to get (Default: "1")
            classGroup:str -> The class group you want to get (Default: "CBIO1 CIR1 Caen 2022-2023 Groupe 1")

        getSchoolReport() -> dict of school report of the user (format : {"nbReport": int, "data": {"name": "id"}})

        downloadReport() -> Download the school report
            path (str, optional): path of the report. Defaults to the name in WebAurion.
            idReport (str, optional): id of the report. Defaults all the report of the user


    moodle() -> dataClasses.Moodle
        getCoursesLink() -> dict of courses link
        getCourseResources(courseId:str) -> dict of course resources
        downloadResources(courseId:str, resourceId:str) -> Download the resource


    userInfo() -> dict
    logout() Optional -> Logout from the session
    """

    def __init__(self, username: str, password: str) -> None:
        # Set the user info
        self.username = username
        self.password = password

        # Create the session
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
        }
        self.logged_in = self.__login()

    def __checkClassExist(self, cycle: str, annee: str, ville: str) -> bool:
        """
        Check if the class exists
        """

        cycles = ["CIR", "CBIO", "CENT", "CEST", "CBIAST", "CSI"]
        annees = ["1", "2", "3"]
        villes = ["Caen", "Brest", "Nantes", "Rennes"]

        if cycle.upper() not in cycles:
            raise Exception(
                "Vous devez renseigner un cycle de la liste suivante: " + ", ".join(cycles)
            )
        if annee not in annees:
            raise Exception(
                "Vous devez renseigner une année de la liste suivante: " + ", ".join(annees)
            )
        if ville.capitalize() not in villes:
            raise Exception(
                "Vous devez renseigner une ville de la liste suivante: " + ", ".join(villes)
            )

        return True

    def __login(self) -> bool:
        """
        Login to the session
        """

        # Get the login page
        req = self.session.get(
            "https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login"
        )

        # Get payload for login
        soup = BeautifulSoup(req.text, "html.parser")
        exec_value = soup.find("input", {"name": "execution"})["value"]

        # Set the payload
        payload = {
            "username": self.username,
            "password": self.password,
            "execution": exec_value,
            "_eventId": "submit",
            "geolocation": "",
        }

        # Login
        req = self.session.post(
            "https://auth.isen-ouest.fr/cas/login?service=https://web.isen-ouest.fr/uPortal/Login",
            data=payload,
        )
        # Check if the login is successful
        return req.status_code == 200

    def logout(self):
        """
        Logout from the session
        """

        # Disconnect from the session (not really necessary)
        self.session.get(
            "https://auth.isen-ouest.fr/cas/logout?url=https://web.isen-ouest.fr/uPortal/Login"
        )

    def webAurion(self):
        """
        Return the webAurion class, For check grades, absences, planning, etc...
        """
        # Get the webAurion informations file: "dataClasses.py"
        return dataClasses.WebAurion(self.session)

    def moodle(self):
        """
        Return moodle informations
        """
        # Get the moodle informations file: "dataClasses.py"
        return dataClasses.Moodle(self.session)

    def classMember(self, cycle: str, annee: str, ville: str) -> dict:
        """
        Args:
            cycle:str "CIR", "CBIO", "CENT", "CEST", "CBIAST", "CSI"
            annee:str "1", "2", "3"
            ville:str "Caen", "Brest", "Nantes", "Rennes"

        Return:
            The class member
        """

        # Base url of trombinoscope
        baseUrl = "https://web.isen-ouest.fr/trombino"

        # Set payload for the request
        payload = {
            "nombre_colonnes": 5,
            "choix_groupe": f"{cycle.upper()}{annee} {ville.capitalize()} 2022-2023",
            "statut": "etudiant",
        }

        # Check if the class exists
        self.__checkClassExist(
            payload["choix_groupe"].split(" ")[0][:-1],
            payload["choix_groupe"].split(" ")[0][-1:],
            payload["choix_groupe"].split(" ")[1],
        )

        # Get the class member
        self.session.get(baseUrl)
        req = self.session.post(
            f"{baseUrl}/fonctions/ajax/lister_etudiants.php", data=payload
        )
        soup = BeautifulSoup(req.text, "html.parser")
        eleves = soup.find_all("td", {"id": "tdTrombi"})
        # Create the dict of eleves
        result = {
            "nbEleves": len(eleves),
            "data": [
                {
                    "nom": eleve.find("b").text,
                    "mail": eleve.find("a").text,
                    "avatarUrl": (baseUrl + eleve.find("img")["src"]).replace(
                        " ./", "/"
                    ),
                }
                for eleve in eleves
            ],
        }
        # Return the dict of eleves
        return result

    def userInfo(self) -> dict:
        """
        Return your user info
        """

        # Get the user info
        req = self.session.get("https://web.isen-ouest.fr/uPortal/api/v5-1/userinfo")
        # Scrap the user info
        info = json.loads(
            base64.urlsafe_b64decode(req.text.split(".")[1].encode()).decode()
        )
        # Return the user info
        return info
