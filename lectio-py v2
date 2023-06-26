import requests
from bs4 import BeautifulSoup
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel



def getLoginSession(username,password,schoolID):
    postUrl = "https://www.lectio.dk/lectio/{0}/login.aspx".format(schoolID)

    loginSession = requests.session()

    # anskaffer eventvali ved at lave en normal get til login siden og kigge html igennem for at finde værdien :)
    eventValidationValue = BeautifulSoup(loginSession.get(postUrl).content,"html.parser").find("input", id="__EVENTVALIDATION")["value"]

    # http request payload
    loginPayload = {
        "m$Content$username": username,
        "m$Content$password": password,
        "m$Content$passwordHidden": password,
        "__EVENTVALIDATION": eventValidationValue,
        "__EVENTTARGET": "m$Content$submitbtn2",
        "__EVENTARGUMENT": "",
        "masterfootervalue": "X1!ÆØÅ",
        "LectioPostbackId": ""
    }
    loginSession.post(postUrl,data=loginPayload)
    return loginSession

# retunere suppen til en URL med den active session(altså det aktive login :)
def getSoup(URL, session):
    return BeautifulSoup(session.get(URL).content,"html.parser")



def get_elev_ID(skoleID,session):
    # går ind på forsiden (den kræver ikke elevid i URL men kun cookie) elevID findes i en specifik a-tag da den linker
    # til en anden side hvor elevID er i URL, elevID bliver taget fra den URL
    url = "https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID)


    soup = getSoup(url, session)

    try:
        href = soup.find("a", attrs={"class":"ls-user-name"})["href"]
    except:
        raise ValueError("ikke logget ind, tjek brugernavn og adgangskode")

    index = href.find("elevid=")
    if index == -1:
        raise ValueError("elevid blev ikke fundet")

    # plusser med 7 for kun at få elevid og ikke elevid= med
    return str(href[index+7:])


def test(skoleID,session,printToggle=False):
    soup= getSoup("https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID),session)

    data = soup.find("div", id="s_m_HeaderContent_MainTitle").text

    if printToggle == True:
        print(data)
        return
    else:
        return data


# beskeder
# liste med alle overskrifter tid og start person og link til videre data
def get_all_messages(skoleID,elevID,session):
    besked_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=&elevid={1}&selectedfolderid".format(skoleID,elevID)

    soup = getSoup(besked_url,session)
    print(soup.findAll("tr"))



class Besked:
    def __init__(self, titel, sender, modtager, dato, link):
        self.titel = titel
        self.sender = sender
        self.modtager = modtager
        self.dato = dato
        self.link = link



#test
sesh = getLoginSession("","","523")
e_id= get_elev_ID("523",sesh)

get_all_messages("523",e_id,sesh)


"""
# grafiske interface
class app(MDApp):
    def build(self):
        label = MDLabel(text="Dit Lectio", halign='center',theme_text_color='Error')
        return label

#app().run()
"""
