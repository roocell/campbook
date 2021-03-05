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

startDate = "2021-08-12"
endDate = "2021-08-24"
partySize = 4

if sys.argv[1]:
    site = sys.argv[1]
else:
    site = 162

log.debug("trying for site {}".format(site))

parts = str(datetime.datetime.now()).split(" ")
searchTime = parts[0] + "T" + parts[1] # 2021-03-04T12:21:32.429

bonecho_locid = 2147483634
bonecho_mazinaw_mapid = 2147483588
bonecho_fairway_mapid = 2147483585
locId = bonecho_locid
mapId = bonecho_mazinaw_mapid

url = "https://reservations.ontarioparks.com/create-booking/results?resourceLocationId=-" + \
      str(locId) + "147483634&mapId=-" + \
      str(mapId) + "&searchTabGroupId=0&bookingCategoryId=0&startDate=" + \
      startDate + \
      "&endDate=" + endDate + \
      "&nights=8&isReserving=true&equipmentId=-32768&subEquipmentId=-32767&partySize=" + \
      str(partySize) + \
      "&searchTime=" + searchTime

driver = webdriver.Chrome('./chromedriver.exe')
driver.get(url)
log.debug(driver.title)


# bring up mapview (it's the default)

# find the site to click
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
    #message = dialog.find_element_by_tag_name('li')
    message = dialog.find_element_by_id('message-0')
    dialogAction = driver.find_element_by_tag_name('mat-dialog-actions')
    log.debug(message.text)
    if not_allowed in message.text:
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
