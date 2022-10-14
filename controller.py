import main as lectio
from datetime import datetime

current_time = datetime.now()

# returnere skemaet for i dag i en liste, hvor ver object er et modul
def skema_i_dag():
    return lectio.skema.get_one_day_short(current_time.weekday()+2)

# returnere den nærmeste lektie
def lektie_1():
    return lectio.lektie.get_nearest_lektie()

# returner de 3 nærmeste lektier
def lektie_3():
    lektie_ls = []
    for x in range(0,2):
        lektie_ls.append(lectio.lektie.get_all_lektier_objects()[x])
    return lektie_ls

# Returner de 3 tætteste opgaver i en liste
def opgave_3():
    opgave_ls = []
    for i in range(0,4):
        opgave_ls.append(lectio.opgaver.get_one_wait(i))
    return opgave_ls
