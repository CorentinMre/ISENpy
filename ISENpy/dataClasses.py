

from bs4 import BeautifulSoup
import requests
import datetime
import json

from . import classification


class DataClasses:

    def __init__(self) -> None:
        pass

    def webAurion(self, url: str, data: dict) -> requests.Response:
        mainPageUrl = self.baseMainPageUrl
        data.update(self.payload)
        self.session.post(mainPageUrl, data=data)
        return self.session.get(url)

    def getPayloadOfThePage(self, text):
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

    def soupForPlanning(self, data: dict, id: str) -> BeautifulSoup:
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

    def getWorkingTime(self, req: requests.get, start_date: str = None, end_date: str = None,
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
        payload = self.getPayloadOfThePage(req.text)
        # Set timestamp of the beginning of the week
        timestamp = int(datetime.datetime.strptime(
            payload["form:date_input"], '%d/%m/%Y').timestamp())
        # Set the first day for the planning
        start_date = (timestamp * 1000) if not start_date else (
            int(datetime.datetime.strptime(start_date, '%d-%m-%Y').timestamp()) * 1000)
        # Set the last day for the planning
        end_date = ((timestamp + 518400) * 1000) if not end_date else (
            int(datetime.datetime.strptime(end_date, '%d-%m-%Y').timestamp()) * 1000)

        # Set the "form:??"
        idform = list(payload.keys())[
            list(payload.values()).index("agendaWeek")][:-5]
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

            # ** is for splited dict to args of the class 'Event'
            event_obj = classification.Event(**event_data)
            workingTime.append(event_obj)

        # get the planning report
        planning_report = classification.PlanningReport(events=workingTime)
        return planning_report

    # def getClassPlanning(self):
    #     """Get the planning of the webAurion class.

    #     Returns:
    #         list: List of classes.
    #     """
    #     information = "Plannings des groupes"
    #     id_information = self.id_leftMenu[information]
    #     soup = self.soupForPlanning(self.dataOtherPlanning, id_information)
    #     listOfClasses = soup.find(
    #         "li", {"class": "enfants-entierement-charges"}).find_all("li")
    #     for child in listOfClasses:
    #         self.classPlanning[child.find(
    #             "span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
    #     return list(self.classPlanning.keys())

    # def getClassCity(self, classPlanning: str = "Plannings CIR"):
    #     """Get the city of the class.

    #     Args:
    #         classPlanning (str, optional): Class of the planning. Defaults to "CIR".

    #     Returns:
    #         list: List of cities.
    #     """
    #     classPlanning = classPlanning
    #     id_classPlanning = self.classPlanning[classPlanning]
    #     soup = self.soupForPlanning(self.dataOtherPlanning, id_classPlanning)
    #     listOfCities = soup.find(
    #         "li", {"class": f"submenu_{id_classPlanning}"}).find_all("li")
    #     for child in listOfCities:
    #         self.classCity[child.find(
    #             "span", {"class": "ui-menuitem-text"}).text] = child["class"][-2].split("_")[-1]
    #     self.classPlanning[classPlanning] = {"city": self.classCity}
    #     return list(self.classCity.keys())

    # def getClassYear(self, classCity: str = "Plannings CIR Caen"):
    #     """Get the year of the class.

    #     Args:
    #         classPlanning (str, optional): Class of the planning. Defaults to "CIR".
    #         classCity (str, optional): City of the planning. Defaults to "Caen".

    #     Returns:
    #         list: List of years.
    #     """

    #     classPlanning = " ".join(classCity.split(" ")[:-1])

    #     id_classCity = self.classPlanning[classPlanning]["city"][classCity]
    #     soup = self.soupForPlanning(self.dataOtherPlanning, id_classCity)
    #     listOfYears = soup.find(
    #         "li", {"class": f"submenu_{id_classCity}"}).find_all("li")
    #     for child in listOfYears:
    #         dictionary = child.find("a")["onclick"].split("'form',")[
    #             1].split(").submit")[0].replace("'", '"')
    #         try:
    #             dictionary = json.loads(dictionary)
    #         except:
    #             dictionary = {}
    #         self.classYear[child.find(
    #             "span", {"class": "ui-menuitem-text"}).text] = dictionary
    #     self.classPlanning[classPlanning]["city"][classCity] = {
    #         "year": self.classYear}
    #     return list(self.classYear.keys())

    # def getClassGroup(self, classYear: str = "Plannings CIR Caen 1"):
    #     """Get the group of the class.

    #     Args:
    #         classPlanning (str, optional): Class of the planning. Defaults to "CIR".
    #         classCity (str, optional): City of the planning. Defaults to "Caen".
    #         classYear (str, optional): Year of the planning. Defaults to "1".

    #     Returns:
    #         list: List of groups.
    #     """

    #     classPlanning = " ".join(classYear.split(" ")[:-2])
    #     classCity = classPlanning + " " + classYear.split(" ")[-2]
    #     classYear = classPlanning + " " + classYear.split(" ")[-1]

    #     payloadOfLastClass = self.classYear[classYear]
    #     payloadOfLastClass.update(self.payload)
    #     req = self.session.post(self.baseMainPageUrl, data=payloadOfLastClass)
    #     soup = BeautifulSoup(req.text, "html.parser")
    #     allLastClass = soup.find(
    #         "tbody", {"class": "ui-datatable-data"}).find_all("tr")
    #     for child in allLastClass:
    #         self.classGroup[child.find(
    #             "span", {"class": "preformatted"}).text] = child["data-rk"]
    #     self.classPlanning[classPlanning]["city"][classCity]["year"][classYear] = {
    #         "group": self.classGroup}
    #     self.classPlanning[classPlanning]["city"][classCity]["year"][classYear]["extraInfo"] = req
    #     return list(self.classGroup.keys())
