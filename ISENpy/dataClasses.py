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
        """
    
        def __init__(self, session):
            #Get the session of the user
            self.session = session
            #Base WebAurion url
            self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
            baseReq = self.session.get(self.baseWebAurionUrl)
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
            self.childLeftMenu = {}
            self.menuChildChild = {}
            self.menuChildChildChild = {}
            self.lastMenu = {}
            
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

            
            url = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"
            data["webscolaapp.Sidebar.ID_SUBMENU"] = "submenu_"+id
            
            req = self.session.post(url, data=data)
            
            soup = BeautifulSoup(req.text, "xml")
            
            inf = soup.find("update", {"id": "form:sidebar"}).text
            
            return BeautifulSoup(inf, "html.parser")
        
        
        def getOtherPlanning(self, 
                             start_date:Optional[str] = None,
                             end_date:Optional[str] = None,
                             classPlanning:str = "Plannings CIR",
                             classCity:str = "Plannings CIR Caen",
                             classYear:str = "Plannings CIR 1",
                             classGroup:str = "CBIO1 CIR1 Caen 2022-2023 Groupe 1") -> list:
            """
            Args:
                start_date (str, optional): The start date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                end_date (str, optional): The end date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
                    If 'start_date' and 'end_date' are not initialized, the planning will be for the current week
                classPlanning (str, optional): The planning of the user. Defaults to "Plannings CIR".
                classCity (str, optional): The city of the user. Defaults to "Plannings CIR Caen".
                classYear (str, optional): The year of the user. Defaults to "Plannings CIR 1".
                classGroup (str, optional): The group of the user. Defaults to "CBIO1 CIR1 Caen 2022-2023 Groupe 1".
            
            Return a dict with the planning of the user for the time interval
            
            """
            
            information = "Plannings des groupes"
            classSection = classPlanning
            classInCity = classCity
            lastClassInfo = classYear
            lastClassInfoV2 = classGroup
            
            id_information = self.id_leftMenu[information]
            id_selection = "form:j_idt52"
            
            
            data = {
                "javax.faces.partial.ajax": "true",
                "javax.faces.source": id_selection,
                "javax.faces.partial.execute": id_selection,
                "javax.faces.partial.render": "form:sidebar",
                id_selection: id_selection,
            }
            
            data.update(self.payload)
            
            soup = self.__soupForPlanning(data, id_information)
            
            
            listOfClasses = soup.find("li", {"class": "enfants-entierement-charges"}).find_all("li")
            for child in listOfClasses:
                self.childLeftMenu[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
            
            
            ####################################
            
            id_classSection = self.childLeftMenu[classSection]
            
            soup = self.__soupForPlanning(data, id_classSection)
            
            listOfClasses = soup.find_all("li", {"class": "enfants-entierement-charges"})[-1].find_all("li")
            for child in listOfClasses:
                self.menuChildChild[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
            
            
            #######################################
            id_classInCity = self.menuChildChild[classInCity]
            
            soup = self.__soupForPlanning(data, id_classInCity)
            
            listOfClasses = soup.find_all("li", {"class": "enfants-entierement-charges"})[-1].find_all("li")
            
            for child in listOfClasses:
                dictionary = child.find("a")["onclick"].split("'form',")[1].split(").submit")[0].replace("'", '"')
                try:
                    dictionary = json.loads(dictionary)
                except:
                    dictionary = {}
                self.menuChildChildChild[child.find("span", {"class": "ui-menuitem-text"}).text] = dictionary
            
            
            #########################################
            payloadOfLastClass = self.menuChildChildChild[lastClassInfo]
            
            payloadOfLastClass.update(self.payload)
            
            
            
            req = self.session.post("https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml", data=payloadOfLastClass)
            
            #print(req.text)
            
            soup = BeautifulSoup(req.text, "html.parser")
            
            allLastClass = soup.find("tbody", {"class": "ui-datatable-data"}).find_all("tr")
            
            
            
            
            for child in allLastClass:
                self.lastMenu[child.find("span", {"class": "preformatted"}).text] = child["data-rk"]
            
            
            choicePlanningUrl = "https://web.isen-ouest.fr/webAurion/faces/ChoixPlanning.xhtml"
            planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"
            
            
            payload = self.__getPayloadOfThePage(req.text, {})[0]
            
            ################################################
            
            lastPayload = {
                "form:j_idt181_reflowDD":"0_0",
                "form:j_idt181:j_idt186:filter":"",
                "form:j_idt181_checkbox":"on",
                "form:j_idt181_selection" : self.lastMenu[lastClassInfoV2],
                "form:j_idt238":"",
                "form:j_idt248_input" : "275805"    
            }
            
            
            payload.update(lastPayload)

            req = self.session.post(choicePlanningUrl, data=payload)

            return self.__getWorkingTime(req, start_date, end_date, True ,lastClassInfoV2)

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