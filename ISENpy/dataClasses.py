import requests
from bs4 import BeautifulSoup
import datetime
import json

class WebAurion:
    
        def __init__(self, session):
    
            self.session = session
            self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
            req = self.session.get(self.baseWebAurionUrl)
            
            self.payload = self.__getPayloadOfThePage(req.text, {})[0]
            self.language = {"form:j_idt755_input" : "275805"} # Langue Francaise
            self.payload.update(self.language)
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
            #if self.payloadForAbsences == "" or self.payloadForGrades == "" or self.payloadForPlanning == "":
                #raise Exception("Error while getting the payload for absences, grades or calendar")
        def __webAurion(self, url:str, data:dict) -> requests.Response:

            
            mainPageUrl = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"

            data.update(self.payload)
            self.session.post(mainPageUrl, data=data)

            return self.session.get(url)

        def __getPayloadOfThePage(self, text, firstpayload):
            
            soup = BeautifulSoup(text, "html.parser")

            inputPayload = soup.find_all("input")

            payload2 = {}

            for i in inputPayload:

                if not "value" in i.attrs.keys():
                    value = ""
                else:
                    value = i["value"]

                payload2[i["name"]] = value

            firstpayload.update(payload2)

            return firstpayload, payload2

        
        def grades(self) -> dict:
            """
            Return a dict with all the grades of the user
            """

            gradeUrl = "https://web.isen-ouest.fr/webAurion/faces/LearnerNotationListPage.xhtml"

            payload = self.payloadForGrades
            pageGrade = self.__webAurion(gradeUrl, payload)

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

            gradeAverage = 0
            noGrade = 0
            for grade in gradeInfo["data"]:
                if grade["note"] != "": gradeAverage += float(grade["note"])
                else: noGrade += 1
            gradeInfo["gradeAverage"] = gradeAverage / (len(gradeInfo["data"]) - noGrade)
            

            return gradeInfo


        def absences(self) -> dict:
            """
            Return a dict with all the absences of the user
            """

            absencesUrl = "https://web.isen-ouest.fr/webAurion/faces/MesAbsences.xhtml"
            payload = self.payloadForAbsences
            pageAbsences = self.__webAurion(absencesUrl, payload)

            soup = BeautifulSoup(pageAbsences.text, "html.parser")

            result = soup.find_all("tr")[6:]
            
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

            return result

        def planning(self, beginningOfTheWeek:str = None) -> dict:
            """
            Args:
                beginningOfTheWeek (str): (Optional) The beginning of the week in the format "dd/mm/yyyy" Ex. "03/10/2022"
                                                     If not specified, the beginning of the week will be the current week
            
            Return a dict with the planning of the user for the week
            """
            
            planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"
            pagePlanning = self.__webAurion(planningUrl, self.payloadForPlanning)
            payload = self.__getPayloadOfThePage(pagePlanning.text, {})[0]
            
            timestamp = int(datetime.datetime.strptime(payload["form:date_input"] if not beginningOfTheWeek else beginningOfTheWeek, '%d/%m/%Y').strftime("%s"))
            
            idform = list(payload.keys())[list(payload.values()).index("agendaWeek")][:-5]
            
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
            
            req = self.session.post(planningUrl, data=payload)
            soup = BeautifulSoup(req.text, "xml")
            planning = soup.find("update", {"id": idform}).text
            
            try: planning = json.loads(planning)
            except: raise Exception("Error while parsing the planning")
            
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

            return workingTime