# poll reservations.ontarioparks.com  for any recently cancelled sites
# sites can be bookd 5 months in advance
#   but the booking can span 5 months + 23 days
# then can be cancelled 4 months in advance (people forced to hold onto bookings for a month)
# so 4 months prior to a trip you want to go on there could be cancellations opening up
# given a booking can span to 5m+23d, it's prudent to check prior to a date you're
# interested in
#

# https://www.browserstack.com/guide/python-selenium-to-run-web-automation-test
# pip install selenium
# https://sites.google.com/a/chromium.org/chromedriver/downloads
# i'm using 88.0

# usage:
# pythong cancel_checker.py <mazinaw/fairway>

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime
import logging
import sendemail
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

url = "https://reservations.ontarioparks.com"
url = "https://reservations.ontarioparks.com/create-booking/results?resourceLocationId=-2147483634&mapId=-2147483588&searchTabGroupId=0&bookingCategoryId=0&startDate=2021-08-16&endDate=2021-08-24&nights=8&isReserving=true&equipmentId=-32768&subEquipmentId=-32767&partySize=4&searchTime=2021-03-04T12:21:32.429"

startDate = "2021-07-17"
endDate = "2021-07-24"
partySize = 4
consecMin = 1  # min consecutive days to look for
period = 60*5  # 5 min

parts = str(datetime.datetime.now()).split(" ")
searchTime = parts[0] + "T" + parts[1] # 2021-03-04T12:21:32.429

bonecho_locid = 2147483634
bonecho_mazinaw_mapid = 2147483588
bonecho_fairway_mapid = 2147483585

locId = bonecho_locid

if sys.argv[1] == "fairway":
    # sites of interest
    # mazinaw = 1-164
    # fairway = 281-400
    mapId = bonecho_fairway_mapid
    sites = []
    for s in range(281, 400+1):
        sites.append(str(s))
    log.debug(sites)
else:
    mapId = bonecho_mazinaw_mapid
    sites = []
    for s in range(1, 163+1):
        sites.append(str(s))
    log.debug(sites)

url = "https://reservations.ontarioparks.com/create-booking/results?resourceLocationId=-" + \
      str(locId) + "&mapId=-" + \
      str(mapId) + "&searchTabGroupId=0&bookingCategoryId=0&startDate=" + \
      startDate + \
      "&endDate=" + endDate + \
      "&nights=8&isReserving=true&equipmentId=-32768&subEquipmentId=-32767&partySize=" + \
      str(partySize) + \
      "&searchTime=" + searchTime

driver = webdriver.Chrome('./chromedriver.exe')
driver.get(url)
log.debug(driver.title)

lastOutputStr = ""
while True:
    outputStr = ""
    calendarButton = 0
    while(calendarButton == 0): # wait for page load
        # find the calendar putton and push it
        try:
          calendarButton = driver.find_element_by_id('grid-view-button')
        except:
          continue;

    # scroll to calendar button

    #calendarButton.click()
    driver.execute_script("arguments[0].click();", calendarButton) # perform JS click

    calendarTable = 0
    while(calendarTable == 0): # wait for page load
        try:
          calendarTable = driver.find_element_by_id('grid-table')
        except:
          continue;

    log.debug("found table")

    # bring table into view
    driver.execute_script("arguments[0].scrollIntoView();", calendarTable)

    log.debug("getting rows...")
    tbody = calendarTable.find_element_by_tag_name("tbody")
    rows = tbody.find_elements_by_tag_name("tr") # very slow
    r = 0
    log.debug("parsing rows...")
    for row in rows:
        #print("row " + str(r))
        #sitecol = row.find_elements_by_tag_name("td")[0]
        #site = row.find_element_by_id("resource-" + str(r) + "-name")
        #print("site: " + site.text)

        consec = 0

        # <td> tags are the available/unavailable and have date in each one as well.
        # under "aria-label". this also has the site number in it
        # this give us 2 weeks of dates (even if not queried)
        cols = row.find_elements_by_tag_name("td")
        for c in range(len(cols)):
            if c == 0: pass  # site column
            t = cols[c].get_attribute("aria-label")
            if t != None:
                #print("{}".format(t))
                parts = t.split("\n")
                site = parts[0].strip()[:-1]
                date = parts[1].strip()
                avail = parts[4].strip()
                #log.debug("{} {} -{}- {}".format(site, date, avail, consec))
                if "Available" == avail and site in sites:
                    consec += 1
                else:
                    if consec >= consecMin:
                        outputStr += "site {} is available for {} days ending on {}<BR>\n".format(site, consec, date)
                    consec = 0

        if consec >= consecMin:
            outputStr += "site {} is available for {} days ending on {}<BR>\n".format(site, consec, date)
        r += 1

    if outputStr == "":
        log.debug("something failed or no sites...trying again")
        time.sleep(period)
        driver.refresh()
        continue

    if lastOutputStr != outputStr:
        email_content = outputStr
        email_content += "<BR><BR>"
        email_content += url
        if lastOutputStr != "":
            email_content += "<BR>NEW CANCELLATION!<BR>"
            log.debug("NEW CANCELLATION!")
            sendemail.send(email_content)
        else:
            # send first one
            email_content += "<BR>INITIAL <BR>"
            sendemail.send(email_content)
        log.debug(outputStr)
    else:
        log.debug("no change")
    lastOutputStr = outputStr


    # keep checking
    time.sleep(period)
    driver.refresh()



# close window when done
driver.close()
