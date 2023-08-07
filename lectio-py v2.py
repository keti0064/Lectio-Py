import requests
from bs4 import BeautifulSoup
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel



def getLoginSession(username,password,schoolID):
    postUrl = "https://www.lectio.dk/lectio/{0}/login.aspx".format(schoolID)

    loginSession = requests.session()

    # anskaffer eventvali ved at lave en normal http get til login siden og kigge html igennem for at finde værdien :)
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

def postSoup(URL,session,payload):
    return BeautifulSoup(session.post(URL,data=payload).content,"html.parser")

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
    beskeder = []
    soup = getSoup(besked_url,session)
    tr_list = soup.findAll("tr")
    for tr in tr_list[1:]:
        td_list = tr.findAll("td")


        td_list_text = [x.text for x in td_list]


        ID_tag = (tr.findNext("a",tabindex="0")["onclick"])
        # skal minus med 1 for at ikke få et ' med
        ID = ID_tag[ID_tag.index("MC_$_")+5:ID_tag.index(")")-1]


        besked = Besked(td_list_text[3].replace("\n",""),td_list_text[4],td_list_text[6],td_list_text[5],td_list_text[8],ID)

        beskeder.append(besked)

    return beskeder

class Besked:
    def __init__(self, titel, sender, modtager,seneste_besked, dato, ID):
        self.titel = titel
        self.sender = sender
        self.modtager = modtager
        self.seneste_besked = seneste_besked
        self.dato = dato
        self.ID = ID

    def consolePrintMessageInfo(self):
        print(self.titel,self.sender,self.modtager,self.seneste_besked,self.dato,self.ID)

    # det her er besværligt da det kræver viewstatex i en post request for at få den her side som bliver lavet om hver gang man går ind på besked forsiden selv i samme session :(
    def getMessageDialog(self,skoleID,elevID,session):
        besked_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=showthread&elevid={1}&selectedfolderid=-70&id={2}".format(skoleID,elevID,self.ID)
        besked_forside_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=&elevid={1}&selectedfolderid".format(skoleID, elevID)

        viewstatex_value = getSoup(besked_forside_url,session).find("input", id="__VIEWSTATEX")["value"]

        postPayload = {
            "__EVENTTARGET": "__PAGE",
            "__EVENTARGUMENT": "$LB2$_MC_$_{}".format(self.ID),
            "__VIEWSTATEX": viewstatex_value,
            "__VIEWSTATEY_KEY":"",
            "__VIEWSTATE":"",
            "__VIEWSTATEENCRYPTED":"",
            "masterfootervalue":    "X1!ÆØÅ",
            "LectioPostbackId": ""
        }


        pageSoup = postSoup(besked_url,session,postPayload)
        # sorter efter svar
        svar = pageSoup.find("ul",id="s_m_Content_Content_ThreadList").findAll("li")
        for s in svar:
            style = s["style"][13]

            # sender:
            sender = s.find("span").text
            # text

            tab = "\t"*int(style)
            text = s.find("div").text
            text = text.replace("\r","").replace("\n","\n"+tab)
            print(tab,"[x]",sender,"\n",tab,text,"\n")



#test
sesh = getLoginSession("","","523")
e_id= get_elev_ID("523",sesh)

a = get_all_messages("523",e_id,sesh)
a[1].getMessageDialog("523",e_id,sesh)


"""
# grafiske interface
class app(MDApp):
    def build(self):
        label = MDLabel(text="Dit Lectio", halign='center',theme_text_color='Error')
        return label

#app().run()
"""
