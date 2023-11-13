import requests
from bs4 import BeautifulSoup


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
        "LectioPostbackId": "",
    }

    headers = {
        "Content-Length": "571",
        "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Linux\"",
        "Upgrade-Insecure-Requests": "1",
        "Content-Length": "0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.lectio.dk/lectio/{0}/forside.aspx".format(schoolID),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }

    cookies = {
        'isloggedin3': 'Y'
    }

    response = loginSession.post(postUrl,data=loginPayload, headers=headers,cookies=cookies)
    print("Login response:",response)
    return loginSession

# retunere suppen til en URL med den active session(altså det aktive login :)


def getSoup(URL, session,school_id):
    headers = {
        "Content-Length": "571",
        "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Linux\"",
        "Upgrade-Insecure-Requests": "1",
        "Content-Length": "0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.lectio.dk/lectio/{0}/forside.aspx".format(school_id),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }

    cookies = {
        'isloggedin3': 'Y'
    }
    return BeautifulSoup(session.get(URL, headers=headers,cookies=cookies).content,"html.parser")


def postSoup(URL,session,payload,school_id):
    headers = {
        "Content-Length": "571",
        "Sec-Ch-Ua": "\"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Linux\"",
        "Upgrade-Insecure-Requests": "1",
        "Content-Length": "0",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.lectio.dk/lectio/{0}/forside.aspx".format(school_id),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=0, i"
    }

    cookies = {
        'isloggedin3': 'Y'
    }

    return BeautifulSoup(session.post(URL,data=payload,headers=headers,cookies=cookies).content,"html.parser")


def get_elev_ID(skoleID,session):
    # går ind på forsiden (den kræver ikke elevid i URL men kun cookie) elevID findes i en specifik a-tag da den linker
    # til en anden side hvor elevID er i URL, elevID bliver taget fra den URL
    url = "https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID)

    soup = getSoup(url, session,skoleID)


    try:
        href = soup.find("a", attrs={"id":"s_m_HeaderContent_subnavigator_ctl03"})["href"]
    except:
        raise ValueError("ikke logget ind, tjek brugernavn og adgangskode")

    index = href.find("elevid=")
    if index == -1:
        raise ValueError("elevid blev ikke fundet")

    # plusser med 7 for kun at få elevid og ikke elevid= med
    return str(href[index+7:])


def test(skoleID,session,printToggle=False):
    soup= getSoup("https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID),session,skoleID)
    try:
        data = soup.find("div", id="s_m_HeaderContent_MainTitle").text
    except:
        data= "Ikke logget ind"

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
    soup = getSoup(besked_url,session,skoleID)
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

    def getMessageDialog(self,skoleID,elevID,session,school_id):
        besked_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=showthread&elevid={1}&selectedfolderid=-70&id={2}".format(skoleID,elevID,self.ID)
        besked_forside_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=&elevid={1}&selectedfolderid".format(skoleID, elevID)

        viewstatex_value = getSoup(besked_forside_url,session,skoleID).find("input", id="__VIEWSTATEX")["value"]

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

        pageSoup = postSoup(besked_url,session,postPayload,school_id=school_id)
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


# anskaf alle moduler i en uge
def get_all_moduler(schoolID,elevID,session,week_year="X",):
    if week_year == "X":

        siteUrl = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?".format(schoolID)
    else:
        siteUrl = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?week={2}".format(schoolID, elevID,week_year)
    siteSoup = getSoup(siteUrl, session,schoolID)
    # find alle moduler, de kan blive placeret ud fra dato som står på modulet.
    alleDageDivs = siteSoup.findAll("div", {"class":"s2skemabrikcontainer lec-context-menu-instance"})
    #liste med alle modul html elementerne på en uge
    ugeModuler = []

    # iterererr igennem alle dage divs, finder alle a_tags, som er hvert enkelt modul og ligger det i en liste
    # den liste bliver smidt ind i moduler, så hver dag er en liste af moduler i moduler
    for dagDiv in alleDageDivs:
        # generer modul objekter
        ugeModuler.append(dagDiv.findAll("a"))
    # liste af dage med moduler omskrevet til modul objekter
    denneUge = []
    for dagNum,dag in enumerate(ugeModuler):
        # liste af denne dags moduler, som modul objektet
        denneDag=[]
        for a_num, a_tag in enumerate(dag):
            data = a_tag.find("div",{"class":"s2skemabrikInnerContainer"})

            if data != None:

                # nyt modul
                modul_titel = ""

                # Der tages højde for om modulet ikke har et ID
                try:
                    # modulets ID ligger i modulets link i absid attributten
                    a_tag_href= a_tag["href"]
                    modul_ID = a_tag_href[a_tag_href.index("absid=") + 6:a_tag_href.index("&")]

                except:
                    modul_ID = ""

                a_tag_style = a_tag["style"]

                # hvert modul har et tool tip hvor lokale, note og tidspunkt står i.
                a_tag_additional_info = a_tag["data-additionalinfo"]


                Lokale_Index = a_tag_additional_info.find("Lokale:")
                if Lokale_Index != -1:
                    modul_lokale = a_tag_additional_info[Lokale_Index:a_tag_additional_info.find("\n",Lokale_Index+8)]
                else:
                    modul_lokale = ""
                # Modul tid og dato, findes også i additional info, den ligger altid over "hold" og alle moduler
                # har hold og dato/tid så det vil altid virke, ellers skriver den FEJL og så ved jeg ikke lige
                # hvad der skal gøres.
                additional_info_splitt = a_tag_additional_info.split("\n")

                # hedder fejl til hvis der ikke findes nogen valid værdi
                modul_dato_tid = "FEJL"
                for index, newLine in enumerate( additional_info_splitt):
                    if "Hold:" in newLine:
                        modul_dato_tid = additional_info_splitt[index-1].replace("\n","")

                # den fysiske position på dagens skema ligger i modulets stil, samt størrelsen af modulet
                modul_pos = a_tag_style
                # modul data
                modul_lære = []
                modul_hold = []
                modul_titel = ""

                modul_status = a_tag.attrs["class"][2]
                all_span = data.findAll("span")
                for span in all_span:
                    try:
                        # her findes hold og lærer, de sepereres ved at kigge på de første karaktere i contextcard
                        # hold starter med HE, og lærer starter med T, derefter er holdet/lærerens ID
                        contextCardData = span.text
                        contextCardID = span.attrs['data-lectiocontextcard']

                        if contextCardID[1]=="E":
                            modul_hold.append(contextCardData)
                        elif contextCardID[0] == "T":
                            modul_lære.append(contextCardData)
                    except:
                        # her findes titlen til modulet, da span tagget med titlen ikke har en contextcard attr
                        # som den eneste.
                        modul_titel = span.text
                #print("\n"+str(dagNum)+"\n"+modul_titel+"\n"+modul_dato_tid+"\n"+modul_lokale+"\n"+modul_status+"\n"+" ".join(modul_hold)+"\n"+" ".join(modul_lære)+"\n"+modul_ID+"\n"+modul_pos+"\n")

                # lav modul objekt og tilføj til liste
                denneDag.append(Modul(modul_lære,modul_hold,modul_pos,modul_lokale,modul_dato_tid,modul_status,modul_ID,modul_titel))
                #slut modul
            else:
                continue

        denneUge.append(denneDag)
    return denneUge


class Modul:
    #anskaffer modulerne ude fra, men de bliver lavet til objekter her. som tillader nem refferat og nemt tilgængeligt
    #data fra hvert modul og data fra modulets side

    def __init__(self, lærer,hold, position,lokale,tid,status,id,titel):
        self.lærer = lærer
        self. hold = hold
        self.position = position
        self.lokale = lokale
        self.tid = tid
        self.status = status
        self.id = id
        self.titel = titel

    def get_site_data(self, skoleID, elevID, session):
        # Her behøves der ikke at anskaffes viewstatex, get requesten kan bare køres direkte
        siteURL = "https://www.lectio.dk/lectio/{0}/aktivitet/aktivitetforside2.aspx?absid={1}&prevurl=SkemaNy.aspx%3ftype%3delev%26elevid%3d{2}&elevid={2}".format(skoleID,self.id,elevID)
        pageSoup = getSoup(siteURL,session,skoleID)

        # find note hvis der er nogen
        try:
            note = pageSoup.find("textarea",attrs={"class":"activity-note"}).text
        except:
            note = None

        # find lektier og eller øvrigt hvis der er nogen
        try:
            lektier_øvrigt = pageSoup.find("div",id="s_m_Content_Content_tocAndToolbar_inlineHomeworkDiv").text
        except:
            lektier_øvrigt = None

        return note, lektier_øvrigt
