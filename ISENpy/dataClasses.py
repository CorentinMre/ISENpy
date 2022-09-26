import requests
from bs4 import BeautifulSoup


class WebAurion:
    
        def __init__(self, session):
    
            self.session = session
            self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
            req = self.session.get(self.baseWebAurionUrl)
            
            self.payload = self.__getPayloadOfThePage(req.text, {})[0]
            self.payload["form:j_idt755_input"] = "275805" # Langue Francaise

        def __webAurion(self, url:str, data:dict) -> requests.Response:

            
            mainPageUrl = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"

             
            payload = self.payload
            payload.update(data)

            self.session.post(mainPageUrl, data=payload)

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

            gradeUrl = "https://web.isen-ouest.fr/webAurion/faces/LearnerNotationListPage.xhtml"

            payload = {"form:j_idt780:j_idt782:j_idt786" : "form:j_idt780:j_idt782:j_idt786"}
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
        
        def planning(self) -> dict:

            planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"

            payload = {"form:j_idt823"	: "form:j_idt823"}
            pagePlanning = self.__webAurion(planningUrl, payload)

            payload = self.__getPayloadOfThePage(pagePlanning.text, {})[0]



            return self.session.post(planningUrl, data=payload).text, payload


        