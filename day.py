#-*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from ast import literal_eval
import time
import re

from calverter import Calverter
from shamsievent import gregorian_event, persian_event, persians_famous, hijri_event

JALALI_WEEKDAYS = [u"یک شنبه", u"دوشنبه", u"سه‌شنبه", u"چهار‌شنبه", u"پنج‌شنبه", u"جمعه", u"شنبه"]
JALALI_MONTH = [
    u"فروردین",
    u"اردیبهشت",
    u"خرداد",
    u"تیر",
    u"مرداد",
    u"شهریور",
    u"مهر",
    u"آبان",
    u"آذر",
    u"دی",
    u"بهمن",
    u"اسفند",
]


def jalali_to_gregorian(date_str):
    if date_str == "":
        return ""
    cal =  Calverter()
    year, month, day = date_str.split("/")
    jd = cal.jalali_to_jd(int(year), int(month), int(day))
    gre = cal.jd_to_gregorian(jd)
    return date(gre[0], gre[1], gre[2])


def gregorian_to_jalali(date):
    if isinstance(date, str):
        date = parser(date)
    if isinstance(date, unicode):
        date = parser(date)
    cal = Calverter()
    jd = cal.gregorian_to_jd(date.year, date.month, date.day)
    jalali = cal.jd_to_jalali(jd)
    return "%s/%s/%s" % (jalali[0], jalali[1], jalali[2])


def parser(date_str):
    year, month, day = date_str.split("-")
    return date(int(year), int(month), int(day))


def normalize_date(date_obj):
    """
    """
    if isinstance(date_obj, date):
        return date_obj.strftime('%Y-%m-%d')
    else:
        return date_obj

def showday(day):
    return JALALI_WEEKDAYS[(day+1)%7]

def show_month(month):
    return JALALI_MONTH[month-1]

def today_event(jalali_date):
    if jalali_date == "":
        return ""
    cal =  Calverter()
    year, month, day = jalali_date.split("/")
    jd = cal.jalali_to_jd(int(year), int(month), int(day))

    is_holiday = False
    events = []

    gr = cal.jd_to_gregorian(jd)
    if (gr[1], gr[2]) in gregorian_event:
        event = gregorian_event[(gr[1], gr[2])]
        events.append(event[0])
        if event[1]:
            is_holiday = True

    hj = cal.jd_to_islamic(jd)
    if (hj[1], hj[2]) in hijri_event:
        event = hijri_event[(hj[1], hj[2])]
        events.append(event[0])
        if event[1]:
            is_holiday = True

    pr = cal.jd_to_jalali(jd)
    if (pr[1], pr[2]) in persians_famous:
        event = persians_famous[(pr[1], pr[2])]
        events.append(event[0])
        if event[1]:
            is_holiday = True

    if (pr[1], pr[2]) in persian_event:
        event = persian_event[(pr[1], pr[2])]
        events.append(event[0])
        if event[1]:
            is_holiday = True           

    return events, is_holiday    

def this_month_event(jalali):
    year, month, day = jalali.split("/")
    dt = jalali_to_gregorian(year+'/'+month+'/'+'1')
    month_long = 32 - int(gregorian_to_jalali(dt+timedelta(32)).split('/')[2])
    last_day_of_month = int(gregorian_to_jalali(dt+timedelta(int(month_long))).split('/')[2])
    cal = {}
    for item in range(1,last_day_of_month+1):
        cal[item] = [today_event(year+'/'+month+'/'+str(item))]

    first_day = dt.weekday()
    return cal, first_day

class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

l2p = [u'۰', u'۱', u'۲', u'۳', u'۴', u'۵', u'۶', u'۷', u'۸', u'۹']
p2l = [u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']

def english_num_to_persian(english_num):
    english_num = str(english_num)
    place = 0
    for integer in p2l:
        english_num = english_num.replace(integer, l2p[place])
        place += 1
    return english_num

def print_cal(pr, cal, first_day):
    today = int(pr.split('/')[2])
    header = '\t\t\t' + show_month(int(pr.split('/')[1])) 
    header += ' ' + english_num_to_persian(pr.split('/')[0]) + '\n' 

    header += bcolors.HEADER + JALALI_WEEKDAYS[6][:2] + '\t'
    for weekday in JALALI_WEEKDAYS[:6]:
        header += weekday[:2] + '\t'
    header += bcolors.ENDC
    print header
    days = ''
    count = 0
    while count < (first+2)%7:
        days += '\t'
        count += 1
    for item in cal:
        is_event = False
        is_holiday = False       

        for event in cal[item]:
            if event[1]:
                is_holiday = True
            if len(event[0]) > 0:
                is_event = True

        if is_event :
            days += bcolors.YELLOW
        if count == 6 or is_holiday:
            days += bcolors.RED
        if item == today:
            days += bcolors.BLUE   

        days += u'‍‎‭'+english_num_to_persian(str(item)) + '\t'

        if count == 6:
            days += bcolors.ENDC + '\n'
            count = 0
        else:
            count += 1

        if is_event:
            days += bcolors.ENDC
        if is_holiday:
            days += bcolors.ENDC
        if item == today:
            days += bcolors.ENDC       
    print days

    print u'--------------------- مناسبت ها -----------------------'
    print_events = ''
    for item in cal:
        # print cal[item][0][0]
        if len(cal[item][0][0]) > 0:
            # for event in cal[item]:
            if cal[item][0][1]:
                print_events += bcolors.RED
            print_events += english_num_to_persian(str(item)) + ': \n'
            if cal[item][0][1]:
                print_events += bcolors.ENDC
            for event in cal[item][0][0]:
                print_events += bcolors.GREEN + event + bcolors.ENDC + '\n'


    print print_events

# dt = datetime.now()#-timedelta(150)
dt = datetime(2014, 11, 10)
pr = gregorian_to_jalali(dt)
# print show_month(int(month))
# print today_event(pr)
cal, first = this_month_event(pr)
# print showday(first)
print_cal(pr, cal, first)
