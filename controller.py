import main as lectio
from datetime import datetime

current_time = datetime.now()

def skema_i_dag():
    return lectio.skema.get_one_day_short(current_time.weekday()+2)

def lektie_1():
    return lectio.lektie.get_nearest_lektie()

def lektie_3():
    lektie_ls = []
    for x in range(0,2):
        lektie_ls.append(lectio.lektie.get_all_lektier_objects()[x])
    return lektie_ls

def opgave_3():
    opgave_ls = []
    for i in range(0,4):
        opgave_ls.append(lectio.opgaver.get_one_wait(i))
    return opgave_ls