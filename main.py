import requests
from bs4 import  BeautifulSoup
from lxml import html

Username = "21Epsilon16"
Password = "fwr43bgk"
SchoolID = "523"
StudentID = "48261254615"


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

    def __init__(self):
        print("skema init")

    skemaURL = "https://www.lectio.dk/lectio/{0}/SkemaNy.aspx?type=elev&elevid={1}".format(SchoolID, StudentID)
    skemaSoup = get_soup(skemaURL)


    def test_skema(self):
        return Skema.skemaSoup.prettify()


    def get_eksame_for_all_days(self):
        eksame_list = []
        for obj in Skema.skemaSoup.select("a .s2skemabrik s2bgbox s2bgboxeksamen s2brik lec-context-menu-instance .s2skemabrikInnerContainer"):
            eksame_list.append(obj)
        return eksame_list

    def get_all_aflyst(self):
        aflyst_list = []
        for a in Skema.skemaSoup.find_all("a", class_="s2skemabrik s2bgbox s2cancelled s2brik lec-context-menu-instance"):
            aflyst_list.append(a.text)
        return aflyst_list

    # mandag er day_int = 2
    def get_one_day(self, day_int):
        td = Skema.skemaSoup.select("tr:nth-of-type(4) td:nth-of-type({})".format(day_int))
        try:
            div_td = td[0].select("a")
        except IndexError:
            return ""

        link_data = []

        for a in div_td:
            link_data.append(a.get("data-additionalinfo"))

        return link_data

    def get_one_day_short(self, day_int):
        td = Skema.skemaSoup.select("tr:nth-of-type(4) td:nth-of-type({})".format(day_int))
        link_data = []
        try:
            div_td = td[0].select("a")
        except IndexError:
            return ""

        for a in div_td:

            a_data = a.get("data-additionalinfo")

            if a_data == None:
                link_data.append("---")

            elif "Øvrigt indhold:" in a_data:
                link_data.append(slice_string(a_data, "Øvrigt indhold:"))

            elif "Lektier:" in a_data:
                link_data.append(slice_string(a_data, "Lektier:"))

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
    def __init__(self):
        print("lektier init")

    url = "https://www.lectio.dk/lectio/{0}/material_lektieoversigt.aspx?elevid={1}".format(SchoolID, StudentID)
    lektieSoup = get_soup(url)

    def get_all_lektier_objects(self):
        lektie_list = []
        for a in Lektier.lektieSoup.find_all("a", class_="s2skemabrik s2bgbox s2brik lec-context-menu-instance"):
            lektie_list.append(a.get('data-additionalinfo'))

        return lektie_list

    def get_nearest_lektie(self):
        data = Lektier.lektieSoup.find("a", class_="s2skemabrik s2bgbox s2brik lec-context-menu-instance")
        return data.get('data-additionalinfo')


class Opgaver:

    def __init__(self):
        print("opgaver init")

    url = "https://www.lectio.dk/lectio/{0}/OpgaverElev.aspx?elevid={1}".format(SchoolID,StudentID)
    opg_soup = get_soup(url)

    ls_mangler = []
    for span in opg_soup.find_all("span",class_="exercisemissing"):
        ls_mangler.append(span)

    ls_venter = []
    for span in opg_soup.find_all("span", class_="exercisewait"):
        ls_venter.append(span)

    def get_data(self, list_used, num):
        data = list_used[num]
        uge = data.parent.parent.find("td").find("span", class_="tooltip").get("title")
        fag = data.parent.parent.find("td", class_="nowrap").text
        note = data.parent.parent.find("a").text
        tid = data.parent.parent.find_all("td")[3].text
        elevtimer = data.parent.parent.find("td", class_="numCell").text
        layout = fag + " | " + uge + " | " + tid + " | " + elevtimer + " elevtimer | " + note
        return layout

    def get_one_missing(self, num):
        return opgaver.get_data(opgaver.ls_mangler,num)


    def get_one_wait(self, num):
        return opgaver.get_data(opgaver.ls_venter, num)

skema = Skema()
lektie = Lektier()
opgaver = Opgaver()
