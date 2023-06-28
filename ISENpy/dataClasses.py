from typing import Optional
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
            start_date:str Optional -> The start of the planning (format : "dd-mm-yyyy")
            end_end:str Optional -> The end of the planning  (format : "dd-mm-yyyy")
        otherPlanning() -> list of dict of planning of the user
            start_date:str Optional -> The start of the planning (format : "dd-mm-yyyy")
            end_end:str Optional -> The end of the planning  (format : "dd-mm-yyyy")
            classPlanning:str Optional -> The class of the planning (Ex. : "CIR")
            classCity:str Optional -> The city of the planning (Ex. : "Caen")
            classYear:str Optional -> The year of the planning (Ex. : "1")
            classGroup:str Optional -> The group of the planning (Ex. : "CBIO1 CIR1 Caen 2022-2023 Groupe 1")
        getClassPlanning() -> list of dict of class in webAurion
        getClassCity() -> list of dict of city in webAurion
            classPlanning:str Optional -> The class of the planning (Ex. : "CIR")
        getClassYear() -> list of dict of year in webAurion
            classPlanning:str Optional -> The class of the planning (Ex. : "CIR")
            classCity:str Optional -> The city of the planning (Ex. : "Caen")
        getClassGroup() -> list of dict of group in webAurion
            classPlanning:str Optional -> The class of the planning (Ex. : "CIR")
            classCity:str Optional -> The city of the planning (Ex. : "Caen")
            classYear:str Optional -> The year of the planning (Ex. : "1")
            
        getSchoolReport() -> dict of report of the user
        downloadReport() -> download the report of the user
            path:str Optional -> The path of the report (Default : the name of the file in WebAurion)
            idReport:str Optional -> The id of the report (Default : all the report of the user)
        
        """
    
        def __init__(self, session):
            #Get the session of the user
            self.session = session
            #Base WebAurion url
            self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
            self.baseMainPageUrl = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"
            baseReq = self.session.get(self.baseWebAurionUrl)
            if baseReq.status_code != 200:
                raise Exception(f"WebAuiron is not available for the moment: Error {baseReq.status_code}")
            #Get the payload of the page
            self.payload = self.__getPayloadOfThePage(baseReq.text, {})[0]
            #Set the language to french
            self.language = {"form:j_idt755_input" : "275805"} # Langue Francaise
            self.payload.update(self.language)
            #Scrap the payload for the grades, absences and planning
            soup = BeautifulSoup(baseReq.text, "html.parser")
            # Get the ids of the left menu
            leftMenu = soup.find("div", {"class": "ui-slidemenu-content"})
            self.id_leftMenu = {}
            self.classPlanning = {}
            self.classCity = {}
            self.classYear = {}
            self.classGroup = {}
            
            #Url of the page of the planning
            self.planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"
            for i in leftMenu.find_all("li"):
                self.id_leftMenu[i.find("span", {"class": "ui-menuitem-text"}).text] = i["class"][-2].split("_")[-1]

            #Get the payload for the grades, absences and planning
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
                
            #Get the payload for the OtherPlanning function
            id_selection = "form:j_idt52"
            self.dataOtherPlanning = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": id_selection,
                "javax.faces.partial.execute": id_selection,
                "javax.faces.partial.render": "form:sidebar",
                id_selection: id_selection,
            }
            self.dataOtherPlanning.update(self.payload)
            
            self.payloadReport = {}
            self.infoReport = {}
            
            
        def __webAurion(self, url:str, data:dict) -> requests.Response:
            """Requests a page of WebAurion

            Args:
                url (str): The url of the page we want to request
                data (dict): The data we want to send

            Returns:
                requests.Response: The response of the request
            """

            #Url of the main page of webAurion
            mainPageUrl = self.baseMainPageUrl
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

#        def myInformation(self) -> dict:
#            """User information (WebAurion)
#            Returns:
#                dict: user information
#            """
#            
#            url = "https://web.isen-ouest.fr/webAurion/faces/TeacherPage.xhtml"
#            
#            response = self.__webAurion(url,{"form:sidebar":"form:sidebar","form:sidebar_menuid":"0_0"})
#
#            return response.text
        
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
                if grade["note"] != "" and grade["note"] != "-": gradeAverage += float(grade["note"])
                else: noGrade += 1
            gradeInfo["gradeAverage"] = round(gradeAverage / (len(gradeInfo["data"]) - noGrade) , 2 )
            
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
            checkAbs = soup.find_all("tr")[6:]
            result = soup.find_all("tbody")[1].find_all("tr")
            total = soup.find_all("tbody")[2].find_all("tr") # [1].find_all("td")[1].text
            
            #If the user not have any absence
            if len(result) == 1 and checkAbs[0].find_all("td")[0].text == "Aucune absence.":
                return {"nbAbsences":"0", "time" : "0", "data":[]}

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
            absencesInfo["nbAbsences"] = total[0].find_all("td")[1].text
            absencesInfo["time"] = total[1].find_all("td")[1].text
            #Return the list of dict of the absences
            return absencesInfo
        
        
        def __getWorkingTime(self, req:requests.get, start_date:str=None, end_date:str=None, isOtherPlanning:bool= False, classe:str = "") -> list:
            """ Get the working time of the user

            Args:
                req (requests.get): request of the page
                start_date (str, optional): the start date of the planning. Defaults to None.
                end_date (str, optional): the end date of the planning. Defaults to None.
                isOtherPlanning (bool, optional): if the planning is for another user. Defaults to False.
                classe (str, optional): the classe of the planning. Defaults to "".

            Raises:
                Exception: if the planning is not found

            Returns:
                list: the list of dict of the planning
            """
            
            #Get the payload of the page
            payload = self.__getPayloadOfThePage(req.text, {})[0]
            #Set timestamp of the beginning of the week
            timestamp = int(datetime.datetime.strptime(payload["form:date_input"], '%d/%m/%Y').timestamp())
            #Set the first day for the planning
            start_date = (timestamp*1000) if not start_date else (int(datetime.datetime.strptime(start_date, '%d-%m-%Y').timestamp())*1000)
            #Set the last day for the planning
            end_date = ((timestamp+518400)*1000) if not end_date else (int(datetime.datetime.strptime(end_date, '%d-%m-%Y').timestamp())*1000)
            
            #Set the "form:??"
            idform = list(payload.keys())[list(payload.values()).index("agendaWeek")][:-5]
            #Set the payload
            data = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": idform,
                "javax.faces.partial.execute": idform,
                "javax.faces.partial.render": idform,
                idform: idform,
                idform + "_start": start_date,
                idform + "_end": end_date,
                "form:offsetFuseauNavigateur": "-7200000",
            }
            payload.update(data)
            payload.update(self.language)
            
            #Request the page for get the planning
            req = self.session.post(self.planningUrl, data=payload)
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
                #check if is the planning of the user planning
                if isOtherPlanning:
                    workingTime.append({
                        "id":i["id"],
                        "start" : i["start"],
                        "end" : i["end"],
                        "className" : i["className"],
                        "debut" : info[0],
                        "fin" : info[1],
                        "salle" : info[-1],
                        "type" : info[2],
                        "matiere" : info[3] if i["className"] != "DS" else ", ".join(info[4:-3]),
                        "description" : ", ".join(info[4:-2]) if i["className"] != "DS" else ", ".join(info[4:-3]),
                        "intervenants" : info[-2],
                        "classe" : classe
                    })
                else:
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

        def planning(self, start_date:Optional[str] = None, end_date:Optional[str] = None) -> list:
            """
            Args:
                start (str, optional): The start date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                end (str, optional): The end date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                    If 'start' and 'end' are not initialized, the planning will be for the current week
            
            Return a dict with the planning of the user for the time interval
            """
            
            
            #Request the page for get payload
            pagePlanning = self.__webAurion(self.planningUrl, self.payloadForPlanning)
            
            return self.__getWorkingTime(req=pagePlanning, start_date=start_date, end_date=end_date)
            
        
        def __soupForPlanning(self, data:dict, id:str) -> BeautifulSoup:
            """ Get the soup page for the planning
            Args:
                data (dict): payload for the request
                id (str): id of the next page

            Returns:
                BeautifulSoup: soup page
            """

            
            url = self.baseMainPageUrl
            data["webscolaapp.Sidebar.ID_SUBMENU"] = "submenu_"+id
            
            req = self.session.post(url, data=data)
            
            soup = BeautifulSoup(req.text, "xml")
            
            inf = soup.find("update", {"id": "form:sidebar"}).text
            
            return BeautifulSoup(inf, "html.parser")
        

        def getClassPlanning(self):
            
            """ Get the planning of the class of webAurion

            Returns:
                list: list of the class
            """
            
            
            information = "Plannings des groupes"
            id_information = self.id_leftMenu[information]
            soup = self.__soupForPlanning(self.dataOtherPlanning, id_information)
            
            listOfClasses = soup.find("li", {"class": "enfants-entierement-charges"}).find_all("li")
            for child in listOfClasses:
                self.classPlanning[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
            
            return list(self.classPlanning.keys())

        def getClassCity(self, classPlanning:str = "CIR"):
            """ Get the city of the class

            Args:
                classPlanning (str, optional): class of planning. Defaults to "CIR".

            Returns:
                list: list of the city
            """
            classPlanning = "Plannings " + classPlanning
            id_classPlanning = self.classPlanning[classPlanning]
            
            soup = self.__soupForPlanning(self.dataOtherPlanning, id_classPlanning)

            listOfClasses = soup.find("li", {"class": f"submenu_{id_classPlanning}"}).find_all("li")
            
            for child in listOfClasses:
                self.classCity[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
            
            self.classPlanning[classPlanning] = {"city" : self.classCity}
            
            return list(self.classCity.keys())
        
        def getClassYear(self, classPlanning:str = "CIR", classCity:str = "Caen"):
            """ Get the year of the class

            Args:
                classPlanning (str, optional): class of planning. Defaults to "CIR".
                classCity (str, optional): city of planning. Defaults to "Caen".

            Returns:
                list: list of the year
            """
            classPlanning = "Plannings " + classPlanning
            classCity = classPlanning + " " + classCity
            id_classCity = self.classPlanning[classPlanning]["city"][classCity]
            
            soup = self.__soupForPlanning(self.dataOtherPlanning, id_classCity)

            listOfClasses = soup.find("li", {"class": f"submenu_{id_classCity}"}).find_all("li")
            
            for child in listOfClasses:
                dictionary = child.find("a")["onclick"].split("'form',")[1].split(").submit")[0].replace("'", '"')
                try:
                    dictionary = json.loads(dictionary)
                except:
                    dictionary = {}
                self.classYear[child.find("span", {"class": "ui-menuitem-text"}).text] = dictionary
                
                
            self.classPlanning[classPlanning]["city"][classCity] = {"year" : self.classYear}
            
            return list(self.classYear.keys())

        def getClassGroup(self, classPlanning:str = "CIR", classCity:str = "Caen", classYear:str = "1"):
            """ Get the group of the class

            Args:
                classPlanning (str, optional): class of planning. Defaults to "CIR".
                classCity (str, optional): city of the planning. Defaults to "Caen".
                classYear (str, optional): year of the planning. Defaults to "1".

            Returns:
                list: list of the group
            """
            
            classPlanning = "Plannings " + classPlanning
            classCity = classPlanning + " " + classCity
            classYear = classPlanning + " " + classYear
            
            payloadOfLastClass = self.classYear[classYear]
            
            payloadOfLastClass.update(self.payload)
            
            req = self.session.post(self.baseMainPageUrl, data=payloadOfLastClass)
            
            soup = BeautifulSoup(req.text, "html.parser")
            
            allLastClass = soup.find("tbody", {"class": "ui-datatable-data"}).find_all("tr")
            
            for child in allLastClass:
                self.classGroup[child.find("span", {"class": "preformatted"}).text] = child["data-rk"]
                
            
            self.classPlanning[classPlanning]["city"][classCity]["year"][classYear] = {"group" : self.classGroup}
            self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["extraInfo"] = req
            
            
            
            return list(self.classGroup.keys())

        
        def getOtherPlanning(self, 
                             start_date:Optional[str] = None,
                             end_date:Optional[str] = None,
                             classPlanning:str = "CIR",
                             classCity:str = "Caen",
                             classYear:str = "1",
                             classGroup:str = "CBIO1 CIR1 Caen 2022-2023 Groupe 1") -> list:
            """
            Args:
                start_date (str, optional): The start date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                end_date (str, optional): The end date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                    If 'start_date' and 'end_date' are not initialized, the planning will be for the current week
                classPlanning (str, optional): The planning of the user. Defaults to "CIR".
                classCity (str, optional): The city of the user. Defaults to "Caen".
                classYear (str, optional): The year of the user. Defaults to "1".
                classGroup (str, optional): The group of the user. Defaults to "CBIO1 CIR1 Caen 2022-2023 Groupe 1".
            
            Return a dict with the planning of the user for the time interval
            
            """
            
            allYearsPossible = ["1", "2", "3"]
            allClassesPossible = {
                "CBIO": [{"Brest" : allYearsPossible}, {"Caen" : allYearsPossible}], 
                "CIR" : [{"Caen" : allYearsPossible}, {"Nantes" : allYearsPossible}, {"Rennes" : ["1", "2"]}, {"Brest" : allYearsPossible}],
                "CSI" : [{"Caen" : allYearsPossible}, {"Nantes" : allYearsPossible}, {"Brest" : allYearsPossible}]
            }
            
            
            
            #verification of informations
            if not classPlanning in allClassesPossible.keys():
                raise Exception("The classPlanning is not in the list of the planning", list(allClassesPossible.keys()))



            for city in allClassesPossible[classPlanning]:
                if classCity in city.keys():
                    if not classYear in city[classCity]:
                        raise Exception("The classYear is not in the list of the planning", city[classCity])
            

            classPlanning = "Plannings " + classPlanning
            classCity = classPlanning + " " + classCity
            classYear = classPlanning + " " + classYear
            
            
            ##############################################

            
            self.getClassPlanning()
            
            #############################################
            
            if not classPlanning in self.classPlanning:
                raise Exception("The classPlanning is not in the list of the planning")

            if not classPlanning:
                raise Exception("Enter value of",list(self.classPlanning.keys()))
                

            if not classCity:
                raise Exception("Enter value of",list(self.classPlanning[classPlanning]["city"].keys()))
            
            self.getClassCity(classPlanning)
            
            
            ############################################
            
            if not classYear:
                raise Exception("Enter value of",list(self.classPlanning[classPlanning]["city"][classCity]["year"].keys()))
            
            self.getClassYear(classPlanning, classCity)
            
            
            #############################################

            if not classGroup:
                raise Exception("Enter value of", list(self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["group"].keys()))
            
            self.getClassGroup(classPlanning, classCity, classYear)
            
            #####################################################

            if not classGroup in self.classGroup:
                raise Exception("The classGroup is not in the list of the planning", list(self.classGroup.keys()))
            
            ################################################
            
            lastPayload = {
                "form:j_idt181_reflowDD":"0_0",
                "form:j_idt181:j_idt186:filter":"",
                "form:j_idt181_checkbox":"on",
                "form:j_idt181_selection" : self.classGroup[classGroup],
                "form:j_idt238":"",
                "form:j_idt248_input" : "275805"    
            }
            
            payloadForChoicePlanning = {classYear : self.__getPayloadOfThePage(self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["extraInfo"].text, {})[0]}
            
            payloadForChoicePlanning[classYear].update(lastPayload)

            req = self.session.post("https://web.isen-ouest.fr/webAurion/faces/ChoixPlanning.xhtml", data=payloadForChoicePlanning[classYear])

            return self.__getWorkingTime(req, start_date, end_date, True ,classGroup)
        

        
        
        def getSchoolReport(self) -> dict:
            """ Get the report of the user

            Returns:
                dict: dict of the report
                    format : {"nbReport": int, "data": {"name": "id"}}
            
            Raises:
                Exception: if the user not have any report
            """
            
            urlPost = self.baseMainPageUrl
            
            information = "Scolarité"
            id_information = self.id_leftMenu[information]
            soup = self.__soupForPlanning(self.dataOtherPlanning, id_information)
            
            id_info = {}
            listOfInformation = soup.find("li", {"class": "enfants-entierement-charges"}).find_all("li")
            for child in listOfInformation:
                id_info[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
                
            information2 = "Mes documents"
            id_information2 = id_info[information2]
            
            soup = self.__soupForPlanning(self.dataOtherPlanning, id_information2)
            id_info2 = {}
            listOfInformation2 = soup.find("li", {"class": "enfants-entierement-charges"}).find_all("li")
            for child in listOfInformation2:
                id_info2[child.find("span", {"class": "ui-menuitem-text"}).text] = child.find("a", {"class": "ui-menuitem-link"})["class"][-2].split("_")[-1]
            

            payload = {
                'form:sidebar':'form:sidebar','form:sidebar_menuid':'1_0_1',
                "form:j_idt780:j_idt782_dropdown":"1", "form:j_idt780:j_idt782_mobiledropdown":"1"
            }
            
            req = self.session.post(urlPost, data=payload)
            
            if req.status_code != 200:
                raise Exception(f"WebAuiron is not available for the moment: Error {req.status_code}, 1")
            
            payload2 = self.__getPayloadOfThePage(req.text, {})[0]
            
            payload2.update(payload)
            payload2.update(self.language)
            
            req = self.session.post(urlPost, data=payload2)
            
            if req.status_code != 200:
                raise Exception(f"WebAuiron is not available for the moment: Error {req.status_code}, 2")
            
            self.payloadReport = self.__getPayloadOfThePage(req.text, {})[0]
            
            soup = BeautifulSoup(req.text, "html.parser")
            
            report = soup.find("div", {"class": "ui-datatable-tablewrapper"}).find("select").find_all("option")
            
            result = {"nbReport": len(report), "data":{}}
            
            for i in report:
                nameFile = i.text.split(".pdf")[0] # because we have space after the name of the file
                nameFile += ".pdf"
                result["data"][nameFile] = i["value"]
            
            
            self.infoReport = result
        
            return result
        
        def downloadReport(self, path:str = None, idReport:str = None) -> None:
            """ Download the report of the user

            Args:
                path (str, optional): path of the report. Defaults to the name in WebAurion.
                idReport (str, optional): id of the report. Defaults all the report of the user

            Raises:
                Exception: if the user not have any report
                Exception: if the report is not found
            """
            
            if self.payloadReport == {}:
                self.infoReport = self.getSchoolReport()
                

            if self.infoReport["nbReport"] == 0:
                raise Exception("The user not have any report")
            
            if self.infoReport["nbReport"] > 1 and path != None:
                raise Exception("The user have more than one report, please choose no one path or no path")
            
            if idReport == None:
                for i in self.infoReport["data"].keys():
                    if path == None:
                        path = i
                    self.downloadReport(path, self.infoReport["data"][i])
                    return
                    

            urlChoixDonnee = "https://web.isen-ouest.fr/webAurion/faces/ChoixDonnee.xhtml"
            
            payload = {
                'form:j_idt193:0:j_idt209':'form:j_idt193:0:j_idt209',
                "form:j_idt193:0:documents_input":idReport,
            }
            
            payload.update(self.payloadReport)
            
            req = self.session.post(urlChoixDonnee, data=payload)
            
            if req.status_code != 200:
                raise Exception(f"WebAuiron is not available for the moment: Error {req.status_code}")
            
            with open(path, "wb") as f:
                f.write(req.content)
            

class Moodle:
    
    def __init__(self, session):
        #Get the session of the user
        self.session = session
        
        self.baseUrl = "https://web.isen-ouest.fr/moodle/my/index.php?mynumber=-2"
    
    def getCoursesLink(self):
        
        req = self.session.get(self.baseUrl)
        
        soup = BeautifulSoup(req.text, "html.parser")
        
        allCourses = soup.find_all("div", {"class": "course_title"})
        courses = {}
        for title in allCourses:
            courses[title.find("h2").text] = title.find("a")["href"]
        
        return courses

    def getCourseResources(self, courseLink):
            
            req = self.session.get(courseLink)
            
            soup = BeautifulSoup(req.text, "html.parser")
            
            topics = soup.find_all("li", {"class": "section main clearfix"})
            resources = {}
            for topic in topics:
                res = topic.find("div", {"class": "content"}).find("ul", {"class": "section img-text"})
                listOfResources = {}
                for ress in res.findAll("li", {"class": "activity resource modtype_resource"}):
                    listOfResources[ress.find("span", {"class": "instancename"}).text] = ress.find("a")["href"]
                
                resources[topic["aria-label"]] = listOfResources

            return resources
    
    def downloadResources(self, link, path):
        
        path = path.replace(" ", "_").replace(":", "_").replace("-", "_").replace("?", "_").replace("!", "_").replace("(", "_").replace(")", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        baseUrl = "https://web.isen-ouest.fr/moodle/pluginfile.php/"
        req = self.session.get(link)
        soup = BeautifulSoup(req.text, "html.parser")
        if ".pdf" in req.url:
            with open(path + ".pdf", "wb") as f:
                f.write(req.content)
            return True
        else: return False
        # if not baseUrl in req.url:
            
        #     for a in soup.find_all("a", href=True):
        #         if a["href"].startswith(baseUrl) and "mod_resource/content" in a["href"]:
        #             link = a["href"]
        #             break
        #     if link == "":
        #         for img in soup.find_all("img", src=True):
        #             if img["src"].startswith(baseUrl) and "mod_resource/content" in img["src"]:
        #                 link = img["src"]
        #                 break
        #     if link == "":
        #         print(path + " not found")
        #         return False

        #     req = self.session.get(link)
        # with open(path + "." +req.url.split(".")[-1], "wb") as f:# path + req.url.split("/")[-1]
        #     f.write(req.content)
        # return True
        #req = self.session.get(link)
       # print(req.url)