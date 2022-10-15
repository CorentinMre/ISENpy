import requests
from bs4 import BeautifulSoup
import datetime
import json

class WebAurion:
        """
        WebAurion Information
        Parameters
        ----------
        session : requests.Session
            The session of the user
        Attributes
        ----------
        session : requests.Session
            The session of the user
        Functions
        ----------
        grades() -> dict of grades of the user
        absences() -> list of dict of absences of the user
        planning() -> list ofdict of planning of the user
            beginningOfTheWeek : datetime.datetime
                The beginning of the week (the Monday day of the week)
        """
    
        def __init__(self, session):
            #Get the session of the user
            self.session = session
            #Base WebAurion url
            self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
            req = self.session.get(self.baseWebAurionUrl)
            #Get the payload of the page
            self.payload = self.__getPayloadOfThePage(req.text, {})[0]
            #Set the language to french
            self.language = {"form:j_idt755_input" : "275805"} # Langue Francaise
            self.payload.update(self.language)
            #Scrap the payload for the grades, absences and planning
            soup = BeautifulSoup(req.text, "html.parser")
            result = soup.find_all("div", {"class":"DispInline"})
            self.payloadForAbsences = ""
            self.payloadForGrades = ""
            self.payloadForPlanning = ""
            for i in result:
                if i.find("a").text == "Dernière note":
                    try : self.payloadForGrades = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                    except : raise Exception("Error while getting the payload for grades")
                if i.find("a").text == "Absences à justifier":
                    try : self.payloadForAbsences = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                    except : raise Exception("Error while getting the payload for absences")
                if i.find("a").text == "Planning":
                    try : self.payloadForPlanning = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                    except : raise Exception("Error while getting the payload for calendar")
            #Check if the payload is not empty
            #if self.payloadForAbsences == "" or self.payloadForGrades == "" or self.payloadForPlanning == "":
                #raise Exception("Error while getting the payload for absences, grades or calendar")
        def __webAurion(self, url:str, data:dict) -> requests.Response:
            """Requests a page of WebAurion

            Args:
                url (str): The url of the page we want to request
                data (dict): The data we want to send

            Returns:
                requests.Response: The response of the request
            """

            #Url of the main page of webAurion
            mainPageUrl = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"
            #Set the payload
            data.update(self.payload)
            self.session.post(mainPageUrl, data=data)
            
            #return the requests.Response of the url
            return self.session.get(url)

        def __getPayloadOfThePage(self, text, firstpayload):
            """
            Get the payload of the page
            Args:
                text (str): The text of the page
                firstpayload (dict): The first payload of the page (for update the payload)
            Returns:
                (dict, dict): The first payload is the default payload updated, the second payload is the payload of the page
            """
            
            #Scrap the input of the page for add it to the payload
            soup = BeautifulSoup(text, "html.parser")
            inputPayload = soup.find_all("input")
            #Init the payload
            payload2 = {}

            for i in inputPayload:

                if not "value" in i.attrs.keys():
                    value = ""
                else:
                    value = i["value"]

                payload2[i["name"]] = value

            #Update the payload
            firstpayload.update(payload2)
            #Return 2 payloads
            return firstpayload, payload2

        
        def grades(self) -> dict:
            """
            Return a dict with all the grades of the user
            """
            #Url of the page of the grades
            gradeUrl = "https://web.isen-ouest.fr/webAurion/faces/LearnerNotationListPage.xhtml"
            #Init the payload
            payload = self.payloadForGrades
            #Request the page
            pageGrade = self.__webAurion(gradeUrl, payload)
            #Scrap the page for get information about the grades
            soup = BeautifulSoup(pageGrade.text, "html.parser")
            result = soup.find_all("tr")[1:]
            gradeInfo = {"gradeAverage":"", "data":[]}
            for tr in result:
                gradeInfo["data"].append({
                    "date" : tr.find_all("td")[0].text,
                    "code" : tr.find_all("td")[1].text,
                    "nom" : tr.find_all("td")[2].text,
                    "note" : tr.find_all("td")[3].text,
                    "abs" : tr.find_all("td")[4].text,
                    "appreciation" : tr.find_all("td")[5].text,
                    "intervenants" : tr.find_all("td")[6].text
                })
            #Init the grade average
            gradeAverage = 0
            #Init if the user not have any grade
            noGrade = 0
            for grade in gradeInfo["data"]:
                if grade["note"] != "": gradeAverage += float(grade["note"])
                else: noGrade += 1
            gradeInfo["gradeAverage"] = gradeAverage / (len(gradeInfo["data"]) - noGrade)
            
            #Return the dict of the grades
            return gradeInfo


        def absences(self) -> list:
            """
            Return a dict with all the absences of the user
            """

            #Url of the page of the absences
            absencesUrl = "https://web.isen-ouest.fr/webAurion/faces/MesAbsences.xhtml"
            #Set the payload
            payload = self.payloadForAbsences
            pageAbsences = self.__webAurion(absencesUrl, payload)
            #Scrap the page for get information about the absences
            soup = BeautifulSoup(pageAbsences.text, "html.parser")
            result = soup.find_all("tr")[6:]
            
            #If the user not have any absence
            if len(result) == 1 and result[0].find_all("td")[0].text == "Aucune absence.":
                return {"nbAbsences":"0", "data":[]}

            absencesInfo = {"nbAbsences":"", "data":[]}
            for tr in result:
                absencesInfo["data"].append({
                    "date" : tr.find_all("td")[0].text,
                    "motif" : tr.find_all("td")[1].text,
                    "duree" : tr.find_all("td")[2].text,
                    "horaire" : tr.find_all("td")[3].text,
                    "cours" : tr.find_all("td")[4].text,
                    "intervenant" : tr.find_all("td")[5].text,
                    "matiere" : tr.find_all("td")[6].text
                })
            absencesInfo["nbAbsences"] = len(absencesInfo["data"])
            #Return the list of dict of the absences
            return result

        def planning(self, beginningOfTheWeek:str = None) -> list:
            """
            Args:
                beginningOfTheWeek (str): (Optional) The beginning of the week in the format "dd/mm/yyyy" Ex. "03/10/2022"
                                                     If not specified, the beginning of the week will be the current week
            
            Return a dict with the planning of the user for the week
            """
            
            #Url of the page of the planning
            planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"
            #Request the page for get payload
            pagePlanning = self.__webAurion(planningUrl, self.payloadForPlanning)
            payload = self.__getPayloadOfThePage(pagePlanning.text, {})[0]
            #Set timestamp of the beginning of the week
            timestamp = int(datetime.datetime.strptime(payload["form:date_input"] if not beginningOfTheWeek else beginningOfTheWeek, '%d/%m/%Y').strftime("%s"))
            #Set the "form:??"
            idform = list(payload.keys())[list(payload.values()).index("agendaWeek")][:-5]
            #Set the payload
            data = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": idform,
                "javax.faces.partial.execute": idform,
                "javax.faces.partial.render": idform,
                idform: idform,
                idform + "_start": timestamp * 1000,
                idform + "_end": (timestamp+518400) * 1000,
                "form:offsetFuseauNavigateur": "-7200000"
            }
            payload.update(data)
            payload.update(self.language)
            
            #Request the page for get the planning
            req = self.session.post(planningUrl, data=payload)
            #Scrap the page for get information about the planning
            soup = BeautifulSoup(req.text, "xml")
            planning = soup.find("update", {"id": idform}).text
            
            #Check if the user not have any planning
            try: planning = json.loads(planning)
            except: raise Exception("Error while parsing the planning")
            
            #Set the workingTime list for the week
            workingTime = []

            for i in planning["events"]:

                info = i["title"].split(" - ")
                workingTime.append({
                    "id":i["id"],
                    "start" : i["start"],
                    "end" : i["end"],
                    "className" : i["className"],
                    "debut" : info[0].split(" à ")[0],
                    "fin" : info[0].split(" à ")[1],
                    "salle" : info[1],
                    "type" : info[2],
                    "matiere" : info[3] if i["className"] != "DS" else ", ".join(info[4:-3]),
                    "description" : ", ".join(info[4:-2]) if i["className"] != "DS" else ", ".join(info[4:-3]),
                    "intervenants" : info[-2],
                    "classe" : info[-1]
                })

            #Return the list of dict of the planning
            return workingTime