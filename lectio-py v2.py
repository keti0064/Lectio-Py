import requests
import re
from bs4 import BeautifulSoup


class Client:

    def __init__(self, username:str, password:str, schoolID:str):
        self.username = username
        self.password = password
        self.schoolID = schoolID
        self.session = getLoginSession(self.username,self.password, self.schoolID)
        self.elevID = get_elev_ID(self.schoolID,self.session)
        print(
    """Lavet klient:
    Username:   {0}
    ElevID:     {1}
    Session:    {2}
        """.format(self.username,self.elevID,self.session.cookies))


# logger ind som elev, returnere http session
def getLoginSession(username: str, password: str, schoolID: str):
    postUrl = "https://www.lectio.dk/lectio/{0}/login.aspx".format(schoolID)

    loginSession = requests.session()

    # anskaffer eventvali ved at lave en normal http get til login siden og kigge html igennem for at finde værdien :)
    eventValidationValue = BeautifulSoup(loginSession.get(postUrl).content, "html.parser").find("input", id="__EVENTVALIDATION")["value"]

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
    loginSession.post(postUrl, data=loginPayload)
    return loginSession


# Laver en GET request med den givne session, returnere suppen af svaret
def getSoup(URL, session):
    return BeautifulSoup(session.get(URL).content, "html.parser")


# Laver en POST request med den givne session, returnere suppen af svaret
def postSoup(URL, session, payload):
    return BeautifulSoup(session.post(URL, data=payload).content, "html.parser")


# henter elev id fra en kendt position på forsiden af lectio, som er tilgængelig uden allerede at kende elevID
def get_elev_ID(skoleID, session):
    # går ind på forsiden (den kræver ikke elevid i URL men kun cookie) elevID findes i en specifik a-tag da den linker
    # til en anden side hvor elevID er i URL, elevID bliver taget fra den URL
    url = "https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID)

    soup = getSoup(url, session)

    try:
        href = soup.find("a", attrs={"id": "s_m_HeaderContent_subnavigator_ctl03"})["href"]
    except:
        raise ValueError("ikke logget ind, tjek brugernavn og adgangskode")

    index = href.find("elevid=")
    if index == -1:
        raise ValueError("elevid blev ikke fundet")

    # plusser med 7 for kun at få elevid og ikke elevid= med
    return str(href[index + 7:])

# metode til at teste om login er gået som det skal >:), du burde få html for lectio forside hvis du er logget ind korrekt.
def test(Client:Client, printToggle=False):
    skoleID = Client.schoolID
    session = Client.session
    soup = getSoup("https://www.lectio.dk/lectio/{0}/forside.aspx".format(skoleID), session)

    data = soup.find("div", id="s_m_HeaderContent_MainTitle").text

    if printToggle:
        print(data)
        return
    else:
        return data


# beskeder
#  anskaffer alle beskeder og laver dem til besked objekter.
def get_all_messages(Client:Client):
    session = Client.session
    skoleID = Client.schoolID
    elevID = Client.elevID

    besked_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=&elevid={1}&selectedfolderid".format(skoleID,
                                                                                                            elevID)
    beskeder = []
    soup = getSoup(besked_url, session)
    tr_list = soup.findAll("tr")
    for tr in tr_list[1:]:
        td_list = tr.findAll("td")

        td_list_text = [x.text for x in td_list]

        ID_tag = (tr.findNext("a", tabindex="0")["onclick"])
        # skal minus med 1 for at ikke få et "'" med
        ID = ID_tag[ID_tag.index("MC_$_") + 5:ID_tag.index(")") - 1]

        # laver besked objekter
        besked = Besked(td_list_text[3].replace("\n", ""), td_list_text[4], td_list_text[6], td_list_text[5],
                        td_list_text[8], ID)

        beskeder.append(besked)

    return beskeder


class Besked:
    def __init__(self, titel, sender, modtager, seneste_besked, dato, ID):
        self.titel = titel
        self.sender = sender
        self.modtager = modtager
        self.seneste_besked = seneste_besked
        self.dato = dato
        self.ID = ID

    def consolePrintMessageInfo(self):
        print(self.titel, self.sender, self.modtager, self.seneste_besked, self.dato, self.ID)

    def postMessageViewStatexSoup(self, Client):
        skoleID = Client.schoolID
        session = Client.session

        besked_forside_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?type=&selectedfolderid".format(
            skoleID)

        viewstatex_value = getSoup(besked_forside_url, session).find("input", id="__VIEWSTATEX")["value"]
        besked_url = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?mappeid=-70".format(skoleID)

        postPayload = {
            "__EVENTTARGET": "__PAGE",
            "__EVENTARGUMENT": "$LB2$_MC_$_{}".format(self.ID),
            "__VIEWSTATEX": viewstatex_value,
            "__VIEWSTATEY_KEY": "",
            "__VIEWSTATE": "",
            "__VIEWSTATEENCRYPTED": "",
            "masterfootervalue": "X1!ÆØÅ",
            "LectioPostbackId": ""
        }

        soup = postSoup(besked_url, session, postPayload)
        return soup

    def getMessageViewStatexKey(self, Client:Client):
        soup = self.postMessageViewStatexSoup(Client)
        return soup.find("input", id="__VIEWSTATEY_KEY")["value"]


    def getMessageDialog(self, Client:Client):
        pageSoup = self.postMessageViewStatexSoup(Client)

        # kigger soup igennem efter table tagget som indeholder hele samtalen.
        table = pageSoup.find("table", id="s_m_Content_Content_MessageThreadCtrl_MessagesGV")
        messages = [messageDiv.find("div",id="GridRowMessage") for messageDiv in table.findAll("tr")]


        allFormatedMessages = []
        for message in messages:
            # tjekker om der er noget tekst i beskeden, hvis ikke skip beskeden.
            try:
                sender = message.find("div", attrs={"class":"message-thread-message-sender"}).text
                sender = sender.replace("\n","").replace("\t","").replace("\r","")
            except:
                continue

            # finder det "div" tag som indeholder resten af beskedens data
            messageContentDiv = message.find("div",attrs={"class": "message"})
            titel = messageContentDiv.find("div",attrs={"class": "message-replysum-header-menu"}).findAll("div")[0].text.strip("\n\n")
            titel = re.sub("[\t\r\n]","",titel)
            content = messageContentDiv.find("div",attrs={"class": "message-thread-message-content"}).text.replace("\t","")

            allFormatedMessages.append([titel,sender,content])

        # returnere hele samtalen i en liste hvor hvert objekt i listen er en besked fra samtalen.
        # hver besked i samtalen er sat ind i en liste med format [titel, sender, content]
        return allFormatedMessages

    def replyToMessage(self, Client:Client,titel,besked):
        # der skal plusses med to for at lave en ny besked i samtalen.
        send_message(Client,[],titel,besked,(self.getMessageViewStatexKey(Client),len(self.getMessageDialog(Client))+2))


    # metode bruges både til at sende nye beskeder og til replies
def send_message(Client:Client,modtager,titel,besked,viewstatexkey=""):
    session = Client.session
    schoolID = Client.schoolID
    postUrl = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?mappeid=-70".format(schoolID)


    # data til ny besked
    if viewstatexkey == "":
        postUrl = "https://www.lectio.dk/lectio/{0}/beskeder2.aspx?mappeid=-70".format(schoolID)
        # først skal viewstatex value findes:
        viewstatex = getSoup(postUrl, session).find("input", id="__VIEWSTATEX")["value"]
        # derefter skal viewstatex key findes
        viewstatexPostData = {
            'time': '0',
            '__EVENTTARGET': 's$m$Content$Content$NewMessageLnk',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__SCROLLPOSITION': '{"tableId":"","rowIndex":-1,"rowScreenOffsetTop":-1,"rowScreenOffsetLeft":-1,"pixelScrollTop":0,"pixelScrollLeft":0}',
            '__VIEWSTATEX': viewstatex,
            '__VIEWSTATEY_KEY': '',
            '__VIEWSTATE': '',
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__VIEWSTATEENCRYPTED': '',
            's$m$searchinputfield': '',
            's$m$Content$Content$ListGridSelectionTree$folders': '-70',
            's$m$Content$Content$MarkChkDD': '-1',
            's$m$Content$Content$SPSearchText$tb': '',
            'masterfootervalue': 'X1!ÆØÅ',
            'LectioPostbackId': '',
        }
        viewstatexkey = postSoup(postUrl, session, viewstatexPostData).find("input", id="__VIEWSTATEY_KEY")["value"]
        # ny besked
        data = {
            '__LASTFOCUS': '',
            'time': '0',
            '__EVENTTARGET': 's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$SendMessageBtn',
            '__EVENTARGUMENT': '',
            '__SCROLLPOSITION': '{"tableId":"","rowIndex":-1,"rowScreenOffsetTop":-1,"rowScreenOffsetLeft":-1,"pixelScrollTop":0,"pixelScrollLeft":0}',
            '__VIEWSTATEY_KEY': viewstatexkey,
            '__VIEWSTATEX': '',
            '__VIEWSTATE': '',
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__VIEWSTATEENCRYPTED': '',
            's$m$searchinputfield': '',
            's$m$Content$Content$ListGridSelectionTree$folders': '-70',
            's$m$Content$Content$MessageThreadCtrl$addRecipientDD$inp': '',
            's$m$Content$Content$MessageThreadCtrl$addRecipientDD$inpid': '',
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$EditModeHeaderTitleTB$tb': titel,
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$EditModeContentBBTB$TbxNAME$tb': besked,
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$AttachmentDocChooser$selectedDocumentId': '',
            'masterfootervalue': 'X1!ÆØÅ',
            'LectioPostbackId': '',
        }
    # data til reply
    else:
        messageNum = viewstatexkey[1]
        if len(str(messageNum)) == 1:
            messageNum = "0{0}".format(messageNum)


        data = {
            'time': '0',
            '__EVENTTARGET': 's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl{0}$SendMessageBtn'.format(messageNum),
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__SCROLLPOSITION': '{"tableId":"","rowIndex":-1,"rowScreenOffsetTop":-1,"rowScreenOffsetLeft":-1,"pixelScrollTop":0,"pixelScrollLeft":0}',
            '__VIEWSTATEY_KEY': viewstatexkey[0],
            '__VIEWSTATEX': '',
            '__VIEWSTATE': '',
            '__VIEWSTATEENCRYPTED': '',
            's$m$searchinputfield': '',
            's$m$Content$Content$ListGridSelectionTree$folders': '-70',
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl{0}$EditModeHeaderTitleTB$tb'.format(messageNum): titel,
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl{0}$EditModeContentBBTB$TbxNAME$tb'.format(messageNum): besked,
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl{0}$AttachmentDocChooser$selectedDocumentId'.format(messageNum): '',
            'masterfootervalue': 'X1!ÆØÅ',
            'LectioPostbackId': '',
        }




    # tilføj modtagere til beskeden
    for m in modtager:
        payload = {
            '__LASTFOCUS': '',
            'time': '0',
            '__EVENTTARGET': 's$m$Content$Content$MessageThreadCtrl$AddRecipientBtn',
            '__EVENTARGUMENT': '',
            '__SCROLLPOSITION': '{"tableId":"","rowIndex":-1,"rowScreenOffsetTop":-1,"rowScreenOffsetLeft":-1,"pixelScrollTop":0,"pixelScrollLeft":0}',
            '__VIEWSTATEY_KEY': viewstatexkey,
            '__VIEWSTATEX': '',
            '__VIEWSTATE': '',
            '__SCROLLPOSITIONX': '0',
            '__SCROLLPOSITIONY': '0',
            '__VIEWSTATEENCRYPTED': '',
            's$m$searchinputfield': '',
            's$m$Content$Content$ListGridSelectionTree$folders': '-70',
            's$m$Content$Content$MessageThreadCtrl$addRecipientDD$inpid': m,
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$EditModeHeaderTitleTB$tb': '',
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$EditModeContentBBTB$TbxNAME$tb': '',
            's$m$Content$Content$MessageThreadCtrl$MessagesGV$ctl02$AttachmentDocChooser$selectedDocumentId': '',
            'masterfootervalue': 'X1!ÆØÅ',
            'LectioPostbackId': '',
        }
        # viewstatexkey bliver opdateret hver gang man putter ny modtager på så den skal opdateres her
        response = postSoup(postUrl,session,payload)
        viewstatexkey = response.find("input",id="__VIEWSTATEY_KEY")["value"]

    # send message content
    so = postSoup(postUrl,session,data)
    print("sender besked:")


# anskaf alle moduler i en uge og laver dem til modul objekter
def get_all_moduler(Client:Client,week_year="X",):
    schoolID = Client.schoolID
    elevID = Client.elevID
    session = Client.session

    if week_year == "X":
        siteUrl = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?".format(schoolID)
    else:
        siteUrl = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?week={2}".format(schoolID, elevID,week_year)
    siteSoup = getSoup(siteUrl, session)
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
    denneUge = [[],[],[],[],[],[],[]]
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
                a_tag_additional_info = a_tag["data-tooltip"]
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
                        # her findes hold og lærer, de separeres ved at kigge på de første karakter i context card
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
                # lav modul objekt og tilføj til liste
                denneDag.append(Modul(modul_lære,modul_hold,modul_pos,modul_lokale,modul_dato_tid,modul_status,modul_ID,modul_titel))
                #slut modul
            else:
                continue
        denneUge[dagNum]=(denneDag)
    return denneUge


class Modul:
    # Anskaffer modulerne ude fra, men de bliver lavet til objekter her. Som tillader nem referat og nemt tilgængeligt
    # data fra hvert modul og data fra modulets side

    def __init__(self, lærer, hold, position, lokale, tid, status, id, titel):
        self.lærer = lærer
        self.hold = hold
        self.position = position
        self.lokale = lokale
        self.tid = tid
        self.status = status
        self.id = id
        self.titel = titel

    def get_site_data(self, Client:Client):
        skoleID = Client.schoolID
        elevID = Client.elevID
        # Her behøves der ikke at anskaffes viewstatex, get requesten kan bare køres direkte
        siteURL = "/lectio/{0}/aktivitet/aktivitetforside2.aspx?absid={1}&prevurl=SkemaNy.aspx%3ftype%3delev%26elevid%3d{2}&elevid={2}".format(
            skoleID, self.id, elevID)

        print("Denne funktion er ikke færdig endnu")

# opgaver, hente opgave data
def get_all_opgaver(Client:Client):
    schoolID = Client.schoolID
    session = Client.session

    baseURL = "https://www.lectio.dk/lectio/{0}/OpgaverElev.aspx".format(schoolID)
    soup = getSoup(baseURL, session)

    tableElement = soup.find("table", id="s_m_Content_Content_ExerciseGV")
    # Alle opgaver står i et enkelt table og er fordelt i tr elementer, data står i samme rækkefølge altid i td
    # rækken og der kan derfor tildeles værdier som under:
    allRows = tableElement.findAll("tr")


    allOpgaver = []
    # genere opgave objekter
    for row in allRows[1::]:
        allTD = row.findAll("td")

        uge = allTD[0].text
        hold = allTD[1].text
        opgavetitel = allTD[2].text
        link = allTD[2].find("a")["href"]
        frist = allTD[3].text
        elevtid = allTD[4].text
        status = allTD[5].text
        fravær = allTD[6].text
        afventer = allTD[7].text
        opgavenote = allTD [8].text
        karakter = allTD[9].text
        elevnote = allTD[10].text

        allOpgaver.append(Opgave(uge,hold,opgavetitel,link,frist,elevtid,status,fravær,afventer,opgavenote,karakter,elevnote))

    return allOpgaver


class Opgave():

    def __init__(self, uge,hold,opgavetitel,link,frist,elevtid,status,fravær,afventer,opgavenote,karakter,elevnote):
        self.uge = uge,
        self. hold = hold
        self.opgavetitel = opgavetitel
        self.link = link
        self.frist = frist
        self. elevtid = elevtid
        self.status = status
        self.fravær = fravær
        self.afventer = afventer
        self.opgavenote = opgavenote
        self.karakter = karakter
        self.elevnote = elevnote

    def cliPrintOpgave(self):
        print(self.uge, self.hold,self.opgavetitel,self.link,self.frist,self.elevtid,self.status,
              self.fravær,self.afventer,self.opgavenote,self.karakter,self.elevnote)


# hente fraværs data
def get_fraværs_data(Client:Client):
    schoolID = Client.schoolID
    session = Client.session

    baseURL = "https://www.lectio.dk/lectio/{0}/subnav/fravaerelev_fravaersaarsager.aspx".format(schoolID)

    soup = getSoup(baseURL,session)
    table = soup.find("div",id="s_m_Content_Content_Samletfravaer_pa").find("table")

    fremmøde = table.find("span", id="s_m_Content_Content_FremmoedeFravaer").text
    skriftelig = table.find("span", id="s_m_Content_Content_SkriftligFravaer").text
    # returnere fravær i format [fremmødem skriftelig]
    return fremmøde,skriftelig








# TEST

client = Client("","","")

m = get_all_moduler(client)

for day in m:
    print(day)
