# the intention of this script is to grab
# a campsite as soon as site opens @ 7am
# you set what site you're interested in and it continuously tries to reserve
# the site by pressing the reserve button
# this script could be run on multiple instances (for several sites) and/or
# from multiple machines for the same site to increase chances of getting it

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import logging
import time
import sys

# create logger
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d   %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# 143 .. 164
# 154, 152 are kind of crap

# aug9:  143, 150, 161, 163
# aug10: 142, 144, 149
# aug11: 151, 152
# aug12:
# aug13: 155
# aug14: 154
# aug15: 147, 162
# aug16: 145
# aug17:
# aug18:
# aug19:
# aug20:
# aug??:  146, 156, 157

# usage:
# python ont_grab_site.py <gat/ont> <map> <site#> <startDate> <endDate>
# python ont_grab_site.py gat taylor T13 2021-08-20 2021-08-25
# python grab_site.py ont 162 2021-08-08 2021-08-25

# python grab_site.py gat peche 12A 2021-07-30 2021-07-31
# python grab_site.py gat taylor T13 2021-07-18 2021-07-23
# python grab_site.py gat phillipe 330 2021-07-18 2021-07-23


fqdn = "reservations.ontarioparks.com"
bonecho_locid = 2147483634
bonecho_mazinaw_mapid = 2147483588
bonecho_fairway_mapid = 2147483585
locId = bonecho_locid
mapId = bonecho_mazinaw_mapid
bookingCategoryId = 0
searchTabGroupId = 0
dateAppend = ""
equip = "&equipmentId=-32768&subEquipmentId=-32767"
gat = False

if sys.argv[1] == "gat":
    gat = True
    fqdn = "reservations.ncc-ccn.gc.ca"
    gat_locid = 2147483648

    locId = gat_locid
    bookingCategoryId = 4  # summer
    searchTabGroupId = 0 # campsite
    #dateAppend = "T00:00:00.000Z"
    equip = "equipmentId=-32768&subEquipmentId=-32768"

    # https://reservations.ncc-ccn.gc.ca/create-booking/results?resourceLocationId=-2147483648&mapId=-2147483642&searchTabGroupId=0&bookingCategoryId=4&startDate=2021-07-18&endDate=2021-07-23&nights=5&isReserving=true&subEquipmentId=-32768&partySize=4&searchTime=2021-03-14T20:24:23.846&equipmentId=-32768

lac_taylor_mapid = 2147483639
lac_phillip_mapid = 2147483642
lac_peche_mapid = 2147483647


map = sys.argv[2]
if map == "taylor":
    mapId = lac_taylor_mapid
if map == "phillipe":
    mapId = lac_phillip_mapid
if map == "peche":
    mapId = lac_peche_mapid

if sys.argv[3]:
    site = sys.argv[3]

startDate = "2021-08-08" + dateAppend
endDate = "2021-08-25" + dateAppend
if sys.argv[4]:
    startDate = sys.argv[4]
if sys.argv[5]:
    endDate = sys.argv[5]

d0 = datetime.datetime.strptime(startDate, "%Y-%m-%d")
d1 = datetime.datetime.strptime(endDate, "%Y-%m-%d")
nights = (d1 - d0).days

startDate += dateAppend
endDate += dateAppend

partySize = 4

log.debug("trying {} for site {} for {} nights".format(fqdn, site, nights))

parts = str(datetime.datetime.now()).split(" ")
searchTime = parts[0] + "T" + parts[1] # 2021-03-04T12:21:32.429

url = "https://" + fqdn + "/create-booking/results?resourceLocationId=-" + \
      str(locId) + "&mapId=-" + \
      str(mapId) + "&searchTabGroupId=" + str(searchTabGroupId) + "&bookingCategoryId=" + str(bookingCategoryId) + \
      "&startDate=" + startDate + \
      "&endDate=" + endDate + \
      "&nights=" + str(nights) + "&isReserving=true" + equip + "&partySize=" + \
      str(partySize) + \
      "&searchTime=" + searchTime

print(url)

driver = webdriver.Chrome('./chromedriver.exe')
driver.get(url)
log.debug(driver.title)

# if gatineau - need to click the Campsites tab
if gat:
    log.debug("looking for campsite tab...")
    tabDiv = 0
    while(tabDiv == 0): # wait for page load
        try:
          tabDiv = driver.find_element_by_id('mat-tab-label-1-1')
        except:
          continue;
    log.debug("found tab ... now clicking it")
    driver.execute_script("arguments[0].click();", tabDiv) # perform JS click



# bring up mapview (it's the default)

# find the site to click
log.debug("looking for map...")
mapDiv = 0
while(mapDiv == 0): # wait for page load
    try:
      mapDiv = driver.find_element_by_id('map')
    except:
      continue;
log.debug("found map")
driver.execute_script("arguments[0].scrollIntoView();", mapDiv)
siteLabels = mapDiv.find_elements_by_class_name('site-label-text')

for s in siteLabels:
    log.debug(s.text)
    if s.text == str(site):
        log.debug("found site {}".format(site))
        siteDiv = s
        break

# click on site of interest
driver.execute_script("arguments[0].click();", siteDiv) # perform JS click

# find form on right with the 'reserve' button
reserveButton = 0
while(reserveButton == 0): # wait for page load
    try:
      reserveButton = driver.find_element_by_id('addToStay')
    except:
      continue;

# click reserve
log.debug('clicking reserve')
driver.execute_script("arguments[0].scrollIntoView();", reserveButton)
driver.execute_script("arguments[0].click();", reserveButton) # perform JS click

d = 0
while True:
    # check if popup happened
    dialog = 0
    give_up = 1000
    while dialog == 0 and give_up > 0: # wait for page load
        try:
          dialog = driver.find_element_by_id('mat-dialog-' + str(d)) # increases count everytime
          #dialog = driver.find_element_by_tag_name('mat-dialog-container')
          #dialog = driver.find_element_by_tag_name('mat-dialog-content')
        except:
          give_up -= 1
          continue;
    if give_up == 0:
        log.debug("giving up on dialog. exiting script")
        exit()
    log.debug('found dialog')
    d +=1

    not_allowed = "Reserving these dates is not yet allowed"
    if gat:
        not_allowed = "will become available for reservation on March 15"

    dialogAction = driver.find_element_by_tag_name('mat-dialog-actions')
    dialogContent = driver.find_element_by_tag_name('mat-dialog-content')
    messages = dialogContent.find_elements_by_tag_name('li')
    dialog_conf = False
    for m in messages:
        log.debug(m.text)
        if not_allowed in m.text:
            dialog_conf = True

    if dialog_conf:
        log.debug("closing dialog")
        dialogCloseButton = dialogAction.find_element_by_tag_name('button')
        driver.execute_script("arguments[0].click();", dialogCloseButton) # perform JS click

        #driver.implicitly_wait(1)
        time.sleep(1) # have to wait in order for the reserve button to work again. not sure why.

        # purposely only doing this again in here - so we click reserve again ONLY if that
        # particular dialog message appears - anything else we kind of want to do nothing
        # so letting it spin in the "while True" should be fine.
        log.debug('clicking reserve')
        driver.execute_script("arguments[0].click();", reserveButton) # perform JS click


# !!! never close window - because we want to keep it open so user
# can book the site !!!
