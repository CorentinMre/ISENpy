# client.py

"""
This file defines the Client class, which is the main class of the package.
"""

import requests
from bs4 import BeautifulSoup
import base64
import json

# IMPORT
# from . import dataClasses
from . import classification


class LoginStudent:
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
    __login()
        Login to the session
        
    getSession()
        Get the session
        
    getPage()
        Get the page
    """

    def __init__(self, username: str, password: str) -> None:


        # Create the session
        self.session = requests.Session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
        }
        
        self.page = None
        self.logged_in = self.__login(username, password)
        self.annee = "2023-2024"
        
        
        


    def __login(self, username, password) -> bool:
        """
        Login to the session
        """
        
        payload = {
            "username": username,
            "password": password,
            "credentialId": "",
        }

        req = self.session.get(
            "https://web.isen-ouest.fr/webAurion/?portail=false")
        soup = BeautifulSoup(req.text, "html.parser")
        # get form action url
        form = soup.find("form")
        url = form["action"]
        
        req = self.session.post(
            url, data=payload)
        
        if req.status_code != 200:
            return False
        
        self.page = req
        
        # print(self.page.text)

        # Check if the login is successful
        return req.status_code == 200

    
    def getSession(self):
        return self.session
    
    def getPage(self):
        if self.page:
            return self.page
        
    