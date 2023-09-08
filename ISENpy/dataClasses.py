# dataClasses.py

"""
This file defines classes to represent WebAurion, Moodle, and their respective data
"""

from typing import Optional
import requests
from bs4 import BeautifulSoup
import json
import datetime

# IMPORT 
from . import classification

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
    grades() -> classification.GradeReport:
        Return a dict with all the grades of the user and the average of the grades
            you can get value with a dict like this : grades["average"] or grades["data"][0]["date"]
            or like this :  grades.average or grades.data[0].date

    absences() -> classification.AbsenceReport:
        Return a list of dict of absences of the user
            you can get value with a dict like this : absences["nbAbsences"] or absences["data"][0]["date"]
            or like this :  absences.nbAbsences or absences.data[0].date

    planning() -> classification.PlanningReport:
        Parameters:
            start_date : str, optional
                The start of the planning (format: "dd-mm-yyyy")
            end_date : str, optional
                The end of the planning (format: "dd-mm-yyyy")
        Return a list of dict of planning of the user
            you can get value with a dict like this : planning["data"][0]["subject"] or planning["data"][0]["start"]
            or like this :  planning.data[0].subject or planning.data[0].start

    otherPlanning() -> list:
        Return a list of dict of planning of the user
        start_date : str, optional
            The start of the planning (format: "dd-mm-yyyy")
        end_date : str, optional
            The end of the planning (format: "dd-mm-yyyy")
        classPlanning : str, optional
            The class of the planning (Ex.: "CIR")
        classCity : str, optional
            The city of the planning (Ex.: "Caen")
        classYear : str, optional
            The year of the planning (Ex.: "1")
        classGroup : str, optional
            The group of the planning (Ex.: "CBIO1 CIR1 Caen 2022-2023 Groupe 1")

    getClassPlanning() -> list:
        Return a list of dict of classes in webAurion

    getClassCity() -> list:
        Return a list of dict of cities in webAurion
        classPlanning : str, optional
            The class of the planning (Ex.: "CIR")

    getClassYear() -> list:
        Return a list of dict of years in webAurion
        classPlanning : str, optional
            The class of the planning (Ex.: "CIR")
        classCity : str, optional
            The city of the planning (Ex.: "Caen")

    getClassGroup() -> list:
        Return a list of dict of groups in webAurion
        classPlanning : str, optional
            The class of the planning (Ex.: "CIR")
        classCity : str, optional
            The city of the planning (Ex.: "Caen")
        classYear : str, optional
            The year of the planning (Ex.: "1")

    getSchoolReport() -> classification.SchoolReport:
        Return a dict of the user's report (format: {"nbReports": int, "data": [{"name": "id"}, ...]})
            you can get value with a dict like this : report["nbReports"] or report["data"][0]["name"]
            or like this :  report.nbReport or report.data[0].name or report.data[0].id

    downloadReport() -> None:
        Download the user's report
        path : str, optional
            The path of the report (Default: the name of the file in WebAurion)
        idReport : str, optional
            The id of the report (Default: all the user's reports)
    """

    def __init__(self, session: requests.Session):
        self.session = session
        self.baseWebAurionUrl = "https://web.isen-ouest.fr/webAurion/?portail=false"
        self.baseMainPageUrl = "https://web.isen-ouest.fr/webAurion/faces/MainMenuPage.xhtml"
        baseReq = self.session.get(self.baseWebAurionUrl)
        if baseReq.status_code != 200:
            raise Exception(f"WebAurion is not available for the moment: Error {baseReq.status_code}")
        self.payload = self.__getPayloadOfThePage(baseReq.text)
        self.language = {"form:j_idt755_input": "275805"}  # Langue Francaise
        # self.payload.update(self.language)
        soup = BeautifulSoup(baseReq.text, "html.parser")
        leftMenu = soup.find("div", {"class": "ui-slidemenu-content"})
        self.id_leftMenu = {}
        self.classPlanning = {}
        self.classCity = {}
        self.classYear = {}
        self.classGroup = {}
        self.planningUrl = "https://web.isen-ouest.fr/webAurion/faces/Planning.xhtml"
        for i in leftMenu.find_all("li"):
            self.id_leftMenu[i.find("span", {"class": "ui-menuitem-text"}).text] = i["class"][-2].split("_")[-1]
        result = soup.find_all("div", {"class": "DispInline"})
        self.payloadForAbsences = ""
        self.payloadForGrades = ""
        self.payloadForPlanning = ""
        for i in result:
            if i.find("a").text == "Dernière note":
                try:
                    self.payloadForGrades = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                except:
                    raise Exception("Error while getting the payload for grades")
            if i.find("a").text == "Absences à justifier":
                try:
                    self.payloadForAbsences = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                except:
                    raise Exception("Error while getting the payload for absences")
            if i.find("a").text == "Planning":
                try:
                    self.payloadForPlanning = json.loads(i.find("a").get("onclick").split(",")[1].split(")")[0].replace("'", '"'))
                except:
                    raise Exception("Error while getting the payload for calendar")
        self.dataOtherPlanning = {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": "form:j_idt52",
            "javax.faces.partial.execute": "form:j_idt52",
            "javax.faces.partial.render": "form:sidebar",
            "form:j_idt52": "form:j_idt52"
        }
        self.dataOtherPlanning.update(self.payload)
        self.payloadReport = {}
        self.infoReport = {}

    def __webAurion(self, url: str, data: dict) -> requests.Response:
        mainPageUrl = self.baseMainPageUrl
        data.update(self.payload)
        self.session.post(mainPageUrl, data=data)
        return self.session.get(url)

    def __getPayloadOfThePage(self, text):
        soup = BeautifulSoup(text, "html.parser")
        inputPayload = soup.find_all("input")
        payload2 = {}

        for i in inputPayload:
            if "value" not in i.attrs.keys():
                value = ""
            else:
                value = i["value"]
            payload2[i["name"]] = value

        return payload2


    def grades(self) -> classification.GradeReport:
        # Get the grades page
        gradeUrl = "https://web.isen-ouest.fr/webAurion/faces/LearnerNotationListPage.xhtml"
        # Set the payload
        payload = self.payloadForGrades
        pageGrade = self.__webAurion(gradeUrl, payload)
        # Scrap the page to get information about the grades
        soup = BeautifulSoup(pageGrade.text, "html.parser")
        
        title = soup.find("title").text.strip()
        if title != "Mes notes":
            return {"success": False, "error": "You are not connected to WebAurion"}

        result = soup.find_all("tr")[1:]
        # Set the list of dict of the grades
        grades = []
        grade_sum = 0
        grade_count = 0

        # Check if the user does not have any grades
        for tr in result:
            date, code, name, grade, absence, appreciation, instructors = (td.text for td in tr.find_all("td"))
            if grade != "" and grade != "-":
                grade_sum += float(grade)
                grade_count += 1

            # Set the dict of the grade
            note = classification.Grade(date=date, code=code, name=name, grade=grade, absence=absence, appreciation=appreciation, instructors=instructors)
            grades.append(note)
            
        # Set the average of the grades
        grade_average = round(grade_sum / grade_count, 2) if grade_count > 0 else 0
        grade_report = classification.GradeReport(grade_average=grade_average, grades=grades)

        # Return the dict of the grades
        return grade_report



    def absences(self) -> classification.AbsenceReport:
        # Get the absences page
        absences_url = "https://web.isen-ouest.fr/webAurion/faces/MesAbsences.xhtml"
        # Set the payload
        payload = self.payloadForAbsences
        absences_page = self.__webAurion(absences_url, payload)
        # Scrap the page to get information about the absences
        soup = BeautifulSoup(absences_page.text, "html.parser")
        
        
        title = soup.find("title").text.strip()
        if title != "Mes absences":
            return {"success": False, "error": "You are not connected to WebAurion"}
        
        # Check if the user does not have any absences
        check_absences = soup.find_all("tr")[6:]
        result = soup.find_all("tbody")[1].find_all("tr")
        total = soup.find_all("tbody")[2].find_all("tr")

        # Set the list of dict of the absences
        if len(result) == 1 and check_absences[0].find_all("td")[0].text == "Aucune absence.":
            return classification.AbsenceReport(nbAbsences="0", time="0", data=[])

        # Set the dict of the absences
        absences_info = {"nbAbsences": "", "absences": []}
        for tr in result:
            absences_info["absences"].append({
                "date": tr.find_all("td")[0].text,
                "reason": tr.find_all("td")[1].text,
                "duration": tr.find_all("td")[2].text,
                "schedule": tr.find_all("td")[3].text,
                "course": tr.find_all("td")[4].text,
                "instructor": tr.find_all("td")[5].text,
                "subject": tr.find_all("td")[6].text
            })
        absences_info["nbAbsences"] = total[0].find_all("td")[1].text
        absences_info["time"] = total[1].find_all("td")[1].text

        # Return the dict of the absences
        absences_data = absences_info["absences"]
        data = [classification.Absence(date=a["date"], reason=a["reason"], duration=a["duration"], schedule=a["schedule"],
                        course=a["course"], instructor=a["instructor"], subject=a["subject"])
                    for a in absences_data]

        # Set the dict of the absences
        absencesInfo = classification.AbsenceReport(nbAbsences=absences_info["nbAbsences"], time=absences_info["time"], data=data)
        return absencesInfo


    def __getWorkingTime(self, req: requests.get, start_date: str = None, end_date: str = None,
                        isOtherPlanning: bool = False, classe: str = "") -> classification.PlanningReport:
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

        # Get the payload of the page
        payload = self.__getPayloadOfThePage(req.text)
        # Set timestamp of the beginning of the week
        timestamp = int(datetime.datetime.strptime(payload["form:date_input"], '%d/%m/%Y').timestamp())
        # Set the first day for the planning
        start_date = (timestamp * 1000) if not start_date else (int(datetime.datetime.strptime(start_date, '%d-%m-%Y').timestamp()) * 1000)
        # Set the last day for the planning
        end_date = ((timestamp + 518400) * 1000) if not end_date else (int(datetime.datetime.strptime(end_date, '%d-%m-%Y').timestamp()) * 1000)

        # Set the "form:??"
        idform = list(payload.keys())[list(payload.values()).index("agendaWeek")][:-5]
        # Set the payload
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

        # Request the page to get the planning
        req = self.session.post(self.planningUrl, data=payload)
        # Scrap the page to get information about the planning
        soup = BeautifulSoup(req.text, "xml")
        planning = soup.find("update", {"id": idform}).text

        # Check if the user does not have any planning
        try:
            planning = json.loads(planning)
        except:
            raise Exception("Error while parsing the planning")

        # Set the workingTime list for the week
        workingTime = []

        for i in planning["events"]:
            info = i["title"].split(" - ")
            event_data = {
                "id": i["id"],
                "start": i["start"],
                "end": i["end"],
                "class_name": i["className"],
                "type": info[2],
                "subject": info[3] if i["className"] != "DS" else ", ".join(info[4:-3]),
                "description": ", ".join(info[4:-2]) if i["className"] != "DS" else ", ".join(info[4:-3]),
                "instructors": info[-2]
            }

            if isOtherPlanning:
                event_data["start_time"] = info[0]
                event_data["end_time"] = info[1]
                event_data["room"] = info[-1]
                event_data["class_info"] = classe
            else:
                event_data["start_time"] = info[0].split(" à ")[0]
                event_data["end_time"] = info[0].split(" à ")[1]
                event_data["room"] = info[1]
                event_data["class_info"] = info[-1]

            event_obj = classification.Event(**event_data) # ** is for splited dict to args of the class 'Event'
            workingTime.append(event_obj)

        # get the planning report
        planning_report = classification.PlanningReport(events=workingTime)
        return planning_report


    def planning(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> list:
        """
        Args:
            start (str, optional): The start date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
            end (str, optional): The end date of the planning. Defaults to None. (Format : "dd-mm-yyyy")
            If 'start' and 'end' are not initialized, the planning will be for the current week

        Return a dictionary with the planning of the user for the time interval
        """

        # Request the page to get the payload
        pagePlanning = self.__webAurion(self.planningUrl, self.payloadForPlanning)

        return self.__getWorkingTime(req=pagePlanning, start_date=start_date, end_date=end_date)

    def __soupForPlanning(self, data: dict, id: str) -> BeautifulSoup:
        """Get the 'soup' page for the planning.

        Args:
            data (dict): Payload for the request.
            id (str): ID of the next page.

        Returns:
            BeautifulSoup: The 'soup' page.
        """
        url = self.baseMainPageUrl
        data["webscolaapp.Sidebar.ID_SUBMENU"] = "submenu_" + id
        req = self.session.post(url, data=data)
        soup = BeautifulSoup(req.text, "xml")
        inf = soup.find("update", {"id": "form:sidebar"}).text
        return BeautifulSoup(inf, "html.parser")


    def getClassPlanning(self):
        """Get the planning of the webAurion class.

        Returns:
            list: List of classes.
        """
        information = "Plannings des groupes"
        id_information = self.id_leftMenu[information]
        soup = self.__soupForPlanning(self.dataOtherPlanning, id_information)
        listOfClasses = soup.find("li", {"class": "enfants-entierement-charges"}).find_all("li")
        for child in listOfClasses:
            self.classPlanning[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
        return list(self.classPlanning.keys())


    def getClassCity(self, classPlanning: str = "Plannings CIR"):
        """Get the city of the class.

        Args:
            classPlanning (str, optional): Class of the planning. Defaults to "CIR".

        Returns:
            list: List of cities.
        """
        classPlanning = classPlanning
        id_classPlanning = self.classPlanning[classPlanning]
        soup = self.__soupForPlanning(self.dataOtherPlanning, id_classPlanning)
        listOfCities = soup.find("li", {"class": f"submenu_{id_classPlanning}"}).find_all("li")
        for child in listOfCities:
            self.classCity[child.find("span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
        self.classPlanning[classPlanning] = {"city": self.classCity}
        return list(self.classCity.keys())


    def getClassYear(self, classCity: str = "Plannings CIR Caen"):
        """Get the year of the class.

        Args:
            classPlanning (str, optional): Class of the planning. Defaults to "CIR".
            classCity (str, optional): City of the planning. Defaults to "Caen".

        Returns:
            list: List of years.
        """
        
        classPlanning = " ".join(classCity.split(" ")[:-1])

        id_classCity = self.classPlanning[classPlanning]["city"][classCity]
        soup = self.__soupForPlanning(self.dataOtherPlanning, id_classCity)
        listOfYears = soup.find("li", {"class": f"submenu_{id_classCity}"}).find_all("li")
        for child in listOfYears:
            dictionary = child.find("a")["onclick"].split("'form',")[1].split(").submit")[0].replace("'", '"')
            try:
                dictionary = json.loads(dictionary)
            except:
                dictionary = {}
            self.classYear[child.find("span", {"class": "ui-menuitem-text"}).text] = dictionary
        self.classPlanning[classPlanning]["city"][classCity] = {"year": self.classYear}
        return list(self.classYear.keys())


    def getClassGroup(self, classYear: str = "Plannings CIR Caen 1"):
        """Get the group of the class.

        Args:
            classPlanning (str, optional): Class of the planning. Defaults to "CIR".
            classCity (str, optional): City of the planning. Defaults to "Caen".
            classYear (str, optional): Year of the planning. Defaults to "1".

        Returns:
            list: List of groups.
        """

        classPlanning = " ".join(classYear.split(" ")[:-2])
        classCity = classPlanning + " " + classYear.split(" ")[-2]
        classYear = classPlanning + " " + classYear.split(" ")[-1]
        
        payloadOfLastClass = self.classYear[classYear]
        payloadOfLastClass.update(self.payload)
        req = self.session.post(self.baseMainPageUrl, data=payloadOfLastClass)
        soup = BeautifulSoup(req.text, "html.parser")
        allLastClass = soup.find("tbody", {"class": "ui-datatable-data"}).find_all("tr")
        for child in allLastClass:
            self.classGroup[child.find("span", {"class": "preformatted"}).text] = child["data-rk"]
        self.classPlanning[classPlanning]["city"][classCity]["year"][classYear] = {"group": self.classGroup}
        self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["extraInfo"] = req
        return list(self.classGroup.keys())

    def getOtherPlanning(self, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        classPlanning: str = "CIR",
                        classCity: str = "Caen",
                        classYear: str = "1",
                        classGroup: str = "CBIO1 CIR1 Caen 2022-2023 Groupe 1") -> list:
        """
        Get the planning of the user for the specified time interval.

        Args:
            start_date (str, optional): The start date of the planning. Defaults to None. (Format: "dd-mm-yyyy")
            end_date (str, optional): The end date of the planning. Defaults to None. (Format: "dd-mm-yyyy")
            classPlanning (str, optional): The planning of the user. Defaults to "CIR".
            classCity (str, optional): The city of the user. Defaults to "Caen".
            classYear (str, optional): The year of the user. Defaults to "1".
            classGroup (str, optional): The group of the user. Defaults to "CBIO1 CIR1 Caen 2022-2023 Groupe 1".

        Returns:
            list: The planning of the user for the specified time interval.
        """

        allYearsPossible = ["1", "2", "3"]
        allClassesPossible = {
            "CBIO": [{"Brest": allYearsPossible}, {"Caen": allYearsPossible}], 
            "CIR": [{"Caen": allYearsPossible}, {"Nantes": allYearsPossible}, {"Rennes": ["1", "2"]}, {"Brest": allYearsPossible}],
            "CSI": [{"Caen": allYearsPossible}, {"Nantes": allYearsPossible}, {"Brest": allYearsPossible}]
        }

        # Verification of classPlanning and classYear
        if classPlanning not in allClassesPossible.keys():
            raise Exception("The classPlanning is not in the list of the planning", list(allClassesPossible.keys()))

        for city in allClassesPossible[classPlanning]:
            if classCity in city.keys() and classYear not in city[classCity]:
                raise Exception("The classYear is not in the list of the planning", city[classCity])

        classPlanning = "Plannings " + classPlanning
        classCity = classPlanning + " " + classCity
        globalClass = classCity + " " + classYear
        classYear = classPlanning + " " + classYear
        

        self.getClassPlanning()

        if classPlanning not in self.classPlanning:
            raise Exception("The classPlanning is not in the list of the planning")

        if not classPlanning:
            raise Exception("Enter value of", list(self.classPlanning.keys()))

        if not classCity:
            raise Exception("Enter value of", list(self.classPlanning[classPlanning]["city"].keys()))

        self.getClassCity(classPlanning)

        if not classYear:
            raise Exception("Enter value of", list(self.classPlanning[classPlanning]["city"][classCity]["year"].keys()))

        self.getClassYear(classCity)

        if not classGroup:
            raise Exception("Enter value of", list(self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["group"].keys()))

        self.getClassGroup(globalClass)

        if classGroup not in self.classGroup:
            raise Exception("The classGroup is not in the list of the planning", list(self.classGroup.keys()))

        lastPayload = {
            "form:j_idt181_reflowDD": "0_0",
            "form:j_idt181:j_idt186:filter": "",
            "form:j_idt181_checkbox": "on",
            "form:j_idt181_selection": self.classGroup[classGroup],
            "form:j_idt238": "",
            "form:j_idt248_input": "275805"    
        }

        payloadForChoicePlanning = {classYear: self.__getPayloadOfThePage(self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["extraInfo"].text)}
        payloadForChoicePlanning[classYear].update(lastPayload)

        req = self.session.post("https://web.isen-ouest.fr/webAurion/faces/ChoixPlanning.xhtml", data=payloadForChoicePlanning[classYear])

        return self.__getWorkingTime(req, start_date, end_date, True, classGroup)

    def getSchoolReport(self) -> classification.SchoolReport:
        """
        Get the report of the user

        Returns:
            dict: Dictionary containing the report information.
                Format: {"num_reports": int, "data": [{"name": "id"}, ...]}

        Raises:
            Exception: If the user does not have any report.
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
            'form:sidebar': 'form:sidebar',
            'form:sidebar_menuid': '1_0_1',
            "form:j_idt780:j_idt782_dropdown": "1",
            "form:j_idt780:j_idt782_mobiledropdown": "1"
        }

        req = self.session.post(urlPost, data=payload)

        if req.status_code != 200:
            raise Exception(f"WebAuiron is not available at the moment: Error {req.status_code}, 1")

        payload2 = self.__getPayloadOfThePage(req.text)

        payload2.update(payload)
        payload2.update(self.language)

        req = self.session.post(urlPost, data=payload2)

        if req.status_code != 200:
            raise Exception(f"WebAuiron is not available at the moment: Error {req.status_code}, 2")

        self.payloadReport = self.__getPayloadOfThePage(req.text)

        soup = BeautifulSoup(req.text, "html.parser")

        report = soup.find("div", {"class": "ui-datatable-tablewrapper"}).find("select").find_all("option")

        result = {"nbReports": len(report), "data": []}

        for i in report:
            nameFile = i.text.split(".pdf")[0].strip() + ".pdf"
            report_data = classification.SchoolReportData(name=nameFile, id=i["value"])
            result["data"].append(report_data)
        
        schoolReport = classification.SchoolReport(**result)
        
        self.infoReport = schoolReport

        return schoolReport



    def downloadReport(self, path: str = None, idReport: str = None) -> None:
        """Download the report of the user

        Args:
            path (str, optional): Path of the report. Defaults to the name in WebAurion.
            idReport (str, optional): ID of the report. Defaults to all the reports of the user.

        Raises:
            Exception: If the user does not have any report.
            Exception: If the report is not found.
        """

        if not self.payloadReport:
            self.infoReport = self.getSchoolReport()

        if self.infoReport.nbReports == 0:
            raise Exception("The user does not have any report")

        if self.infoReport.nbReports > 1 and path is None and idReport is None:
            for report in self.infoReport.data:
                self.downloadReport(path=report.name, idReport=report.id)
            return

        if path is None and idReport is not None:
            # self.infoReport format : {"nbReports": int, "data":  ({"name": "name", "id":"id"}, ...)}]}
            for i in self.infoReport.data:
                if i.id == idReport:
                    path = i.name
                    break
            if path is None:
                raise Exception("The report is not found")

        if idReport is None:
            for i in self.infoReport.data:
                if path is None:
                    path = i.name
                self.downloadReport(path=i.name, idReport=i.id)
                return

        urlChoixDonnee = "https://web.isen-ouest.fr/webAurion/faces/ChoixDonnee.xhtml"

        payload = {
            'form:j_idt193:0:j_idt209': 'form:j_idt193:0:j_idt209',
            "form:j_idt193:0:documents_input": idReport,
        }

        payload.update(self.payloadReport)

        req = self.session.post(urlChoixDonnee, data=payload)

        if req.status_code != 200:
            raise Exception(f"WebAuiron is not available at the moment: Error {req.status_code}")

        if not path.endswith(".pdf"):
            path += ".pdf"
        
        with open(path, "wb") as f:
            f.write(req.content)
            
    def getMyClass(self):
        
        urlPost = self.baseMainPageUrl

        information = "Scolarité"
        id_information = self.id_leftMenu[information]
        soup = self.__soupForPlanning(self.dataOtherPlanning, id_information)
        
        payload = {
            'form:sidebar': 'form:sidebar',
            'form:sidebar_menuid': '1_7',
            "form:j_idt780:j_idt782_dropdown": "1",
            "form:j_idt780:j_idt782_mobiledropdown": "1"
        }

        req = self.session.post(urlPost, data=payload)
        
        payload2 = self.__getPayloadOfThePage(req.text)
        
        payload2.update(payload)
        payload2.update(self.language)

        req = self.session.post(urlPost, data=payload2)
        
        soup = BeautifulSoup(req.text, "html.parser")
        
        row = soup.find_all("tr", {"class": "CursorInitial"})[0]
        
        classe = row.find_all("td")[0].text
            
        return classe
        

class Moodle:
    """Class to get the resources of the user's courses. (on Moodle)
    
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
    getCoursesLink() -> dict:
        Return a dictionary with the courses of the user
        
    getCourseResources(courseLink: str) -> dict:
        Return a dictionary with the resources of the course
        
    downloadResources(link: str, path: str) -> bool:
        Download the resource of the link in the path
    """
    def __init__(self, session):
        """Initialize Moodle class with a session.

        Args:
            session: User session.
        """
        self.session = session
        self.baseUrl = "https://web.isen-ouest.fr/moodle/my/index.php?mynumber=-2"

    def getCoursesLink(self):
        """Get the links of the user's courses.

        Returns:
            dict: Dictionary containing the course titles and their respective links.
        """
        req = self.session.get(self.baseUrl)
        soup = BeautifulSoup(req.text, "html.parser")
        allCourses = soup.find_all("div", {"class": "course_title"})
        courses = {}
        for title in allCourses:
            courses[title.find("h2").text] = title.find("a")["href"]
        return courses

    def getCourseResources(self, courseLink):
        """Get the resources of a specific course.

        Args:
            courseLink (str): Link of the course.

        Returns:
            dict: Dictionary containing the course topics and their respective resources.
        """
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
        """Download a resource from the given link.

        Args:
            link (str): Link of the resource.
            path (str): Path to save the downloaded resource.

        Returns:
            bool: True if the resource is downloaded successfully, False otherwise.
        """
        path = path.replace(" ", "_").replace(":", "_").replace("-", "_").replace("?", "_").replace("!", "_").replace(
            "(", "_").replace(")", "_").replace("'", "_").replace(",", "_").replace(".", "_")
        req = self.session.get(link)
        if ".pdf" in req.url:
            with open(path + ".pdf", "wb") as f:
                f.write(req.content)
            return True
        else:
            return False

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