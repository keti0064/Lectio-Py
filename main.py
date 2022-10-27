import requests
from datetime import datetime
from bs4 import  BeautifulSoup
from lxml import html

Username = "lectio brugernavn"
Password = "lectio adgangskode"
SchoolID = "din skoles lectio id"
StudentID = "din elev id"


postUrl = "https://www.lectio.dk/lectio/{0}/login.aspx".format(SchoolID)
forsideURL = "https://www.lectio.dk/lectio/{0}/forside.aspx?elevid={1}".format(SchoolID, StudentID)

session = requests.Session()
result = session.get(postUrl)
tree = html.fromstring(result.text)
authenticity_token = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]

loginPayload = {
    "m$Content$username": Username,
    "m$Content$password": Password,
    "m$Content$passwordHidden": Password,
    "__EVENTVALIDATION": authenticity_token,
    "__EVENTTARGET": "m$Content$submitbtn2",
    "__EVENTARGUMENT": "",
    "masterfootervalue": "X1!ÆØÅ",
    "LectioPostbackId": ""
}


def LogIn():
    Session = requests.session()
    Session.post(postUrl, data=loginPayload)

    return Session


def get_soup(url):
    active_session = LogIn()
    response = active_session.get(url)
    soup = BeautifulSoup(response.content,"html.parser")
    return soup


class Skema:
    skemaURL = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?type=elev&elevid={1}".format(SchoolID, StudentID)
    skemaSoup = get_soup(skemaURL)

    @staticmethod
    def test_skema():
        return Skema.skemaSoup.prettify()

    @staticmethod
    def get_eksame_for_all_days():
        eksame_list = []
        for obj in Skema.skemaSoup.select("a .s2skemabrik s2bgbox s2bgboxeksamen s2brik lec-context-menu-instance .s2skemabrikInnerContainer"):
            eksame_list.append(obj)
        return eksame_list

    @staticmethod
    def get_all_aflyst():
        aflyst_list = []
        for a in Skema.skemaSoup.find_all("a", class_="s2skemabrik s2bgbox s2cancelled s2brik lec-context-menu-instance"):
            aflyst_list.append(a.text)
        return aflyst_list

    # mandag er day_int = 2
    @staticmethod
    def get_one_day(day_int):
        td = Skema.skemaSoup.select("tr:nth-of-type(4) td:nth-of-type({})".format(day_int))
        try:
            div_td = td[0].select("a")
        except IndexError:
            return ""

        link_data = []

        for a in div_td:
            link_data.append(a.get("data-additionalinfo"))

        return link_data

    @staticmethod
    def get_one_day_short(day_int):
        td = Skema.skemaSoup.select("tr:nth-of-type(4) td:nth-of-type({})".format(day_int))
        link_data = []
        try:
            div_td = td[0].select("a")
        except IndexError:
            return ""

        for a in div_td:

            a_data = a.get("data-additionalinfo")

            if a_data == None:
                pass

            elif "Lektier:" in a_data:
                link_data.append(slice_string(a_data, "Lektier:"))

            elif "Øvrigt indhold:" in a_data:
                link_data.append(slice_string(a_data, "Øvrigt indhold:"))

            elif "Note:" in a_data:
                link_data.append(slice_string(a_data, "Note:"))

            else:
                link_data.append(a_data)

        return link_data


def slice_string(string_to_slice,word_at_slice):
    word_index = string_to_slice.index(word_at_slice)
    new_string = string_to_slice[0:word_index]
    return new_string


class Lektier:
    url = "https://www.lectio.dk/lectio/{0}/material_lektieoversigt.aspx?elevid={1}".format(SchoolID, StudentID)
    lektieSoup = get_soup(url)

    @staticmethod
    def get_all_lektier_objects():
        lektie_list = []
        for a in Lektier.lektieSoup.find_all("a", class_="s2skemabrik s2bgbox s2brik lec-context-menu-instance"):
            lektie_list.append(a.get('data-additionalinfo'))

        return lektie_list

    @staticmethod
    def get_nearest_lektie():
        data = Lektier.lektieSoup.find("a", class_="s2skemabrik s2bgbox s2brik lec-context-menu-instance")
        return data.get('data-additionalinfo')


class Opgaver:
    url = "https://www.lectio.dk/lectio/{0}/OpgaverElev.aspx?elevid={1}".format(SchoolID,StudentID)
    opg_soup = get_soup(url)

    ls_mangler = []
    for span in opg_soup.find_all("span",class_="exercisemissing"):
        ls_mangler.append(span)

    ls_venter = []
    for span in opg_soup.find_all("span", class_="exercisewait"):
        ls_venter.append(span)

    @staticmethod
    def get_data(list_used, num):
        data = list_used[num].parent.parent
        uge = data.find("td").find("span", class_="tooltip").get("title")
        fag = data.find("td", class_="nowrap").text
        note = data.find("a").text
        tid = data.find_all("td")[3].text
        elevtimer = data.find("td", class_="numCell").text
        layout = "{0:>10} | {1} | {2} | {3} elevtimer | {4}".format(fag,uge,tid,elevtimer,note)
        return layout

    @staticmethod
    def get_one_missing(num):
        return Opgaver.get_data(Opgaver.ls_mangler,num)

    @staticmethod
    def get_one_wait(num):
        return Opgaver.get_data(Opgaver.ls_venter, num)


skema = Skema()

lektie = Lektier()




# mere brugervenlige funktioner:
current_time = datetime.now()


# returnere skemaet for i dag i en liste, hvor ver object er et modul
def skema_i_dag():
    return skema.get_one_day_short(current_time.weekday()+2)

# returnere en liste med dage, hver dag er en liste for sig selv med moduler
def skema_uge():
    skema_ls = []
    for day in range (2,7):
        skema_ls.append(skema.get_one_day_short(day))
    return  skema_ls
# returnere den nærmeste lektie
def lektie_1():
    return lektie.get_nearest_lektie()


# returner de 3 nærmeste lektier
def lektie_3():
    lektie_ls = []
    for x in range(0,2):
        lektie_ls.append(lektie.get_all_lektier_objects()[x])
    return lektie_ls


# Returner de 3 tætteste opgaver i en liste
def opgave_3():
    opgave_ls = []
    for i in range(0,4):
        opgave_ls.append(Opgaver.get_one_wait(i))
    return opgave_ls

# split modul op efter hvor mange newlines der er. hvis der er 7 er der en note som er på plads 0, hvis der er 6 er der ikke nogen note.
def format_modul(modul):
    modul_ls = modul.split('\n')
    layout6 = "{0} | {1} | {2} | {3}"
    layout7 = "{0} | {1} | {2} | {3} | {4}"

    layout6_AE = "{0} | Ændret! | {1} | {2} | {3}"
    layout7_AE = "{0} | Ændret! | {1} | {2} | {3} | {4}"
    if modul_ls[0].startswith("Ændret!"):
        if len(modul_ls) == 7:
            return layout6_AE.format(modul_ls[1],modul_ls[3],modul_ls[4], modul_ls[2])
        elif len(modul_ls) == 8:
            return layout7_AE.format(modul_ls[2],modul_ls[4],modul_ls[5], modul_ls[1], modul_ls[3])
    elif modul_ls[0] == "Aflyst!":
        return "Aflyst modul!"
    elif len(modul_ls) == 6:
        return layout6.format(modul_ls[0],modul_ls[2],modul_ls[3], modul_ls[1])
    elif len(modul_ls) == 7:
        return layout7.format(modul_ls[1],modul_ls[3],modul_ls[4], modul_ls[0], modul_ls[2])

