import time
from playwright.sync_api import Page, Request, Response
import datetime

class Repository():
    url="https://www.google.com/travel/flights?hl=en&curr=USD"
    page:Page
    maxCalendarMonthReached = 2
    monthsNumbers=[]
    _monthsNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    _callingCalendarApi = 0
    def __init__(self, page:Page):
        self.page = page
        page.on('request', self._onRequest)
        page.on('response', self._onResponse)
        page.goto(self.url)
        page.get_by_label('Round trip').nth(0).click()
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        self.getCalendarInput().click()
        time.sleep(0.5)
        page.keyboard.press("ArrowRight")
        page.keyboard.press("Enter")

    def _onRequest(self, request:Request):
        if(request.method == "POST" and "getcalendarpicker" in request.url.lower()):
            self._callingCalendarApi += 1

    def _onResponse(self, response:Response):
        if(response.request.method == "POST" and "getcalendarpicker" in response.request.url.lower()):
            self._callingCalendarApi -= 1

    def getInputAirport(self, isArrival=True):
        labelText = 'Where to' if isArrival == True else 'Where from'
        return self.page.locator(f"input[aria-label^='{labelText}']")

    def setNonstop(self):
        self.page.get_by_text('Stops').click()
        self.page.get_by_text('Nonstop only').click()

    def search(self):
        self.getInputAirport().focus()
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Tab")
        self.page.keyboard.press("Enter")

    def reachMonth(self, month):
        index = self.monthsNumbers.index(month)
        while index +1 > self.maxCalendarMonthReached:
            self.nextCalendarMonth()
            self.maxCalendarMonthReached +=1
            time.sleep(0.2)

    
    def findLowestFromMonth(self, *, month, include=[], exclude=[]):
        self.reachMonth(month)
        time.sleep(1)
        trys=1
        while self._callingCalendarApi > 0:
            time.sleep(1)
            if trys> 20:
                raise TimeoutError("Calendar api timeout")
            
        rowgroups = self.page.get_by_role("rowgroup")
        rows = rowgroups.nth(self.monthsNumbers.index(month)).get_by_role('row')
        prices=[]
        for i in range(0, rows.count()):
            row = rows.nth(i)
            gridcells = row.get_by_role("gridcell")
            for x in range(0, gridcells.count()):
                gridcell = gridcells.nth(x)
                dateDiv = gridcell.locator(f"[aria-label*='{self._monthsNames[month-1]}']")
                dateArray = [item.strip() for item in dateDiv.get_attribute('aria-label').replace(',', '').split()]
                if len(exclude) > 0:
                    if(dateArray[0] in exclude or int(dateArray[2]) in exclude):
                        continue
                if len(include) > 0:
                    if(not (dateArray[0] in include or int(dateArray[2]) in include)):
                        continue
                pricesDiv = gridcell.locator("[aria-label$='US dollars']")
                for y in range(0, pricesDiv.count()):
                    priceDiv = pricesDiv.nth(y)
                    price=int(priceDiv.inner_text().replace('$', ''))
                    prices.append(price)
        return min(prices) if len(prices) > 0 else None

    
    def loadMonthsNumbers(self):
        self.getCalendarInput().click()
        self.page.get_by_role("rowgroup")
        firstRowgroup = self.page.get_by_role("rowgroup").nth(0)
        firstDiv = firstRowgroup.locator("div").nth(0)
        monthNumber = datetime.datetime.strptime(firstDiv.inner_text(), "%B").month
        for i in range(0, 12):
            self.monthsNumbers.append(monthNumber)
            monthNumber += 1
            if(monthNumber > 12):
                monthNumber = 1


    def nextCalendarMonth(self):
        self.page.get_by_label('Next').nth(0).click()
        
    def getCalendarInput(self):
        calendar = self.page.get_by_placeholder('Departure')
        return calendar if calendar.count() == 1 else calendar.nth(0)
    
    def setAirport(self,*, isArrival, airport):
        self.getInputAirport(isArrival).fill(airport)
        time.sleep(0.5)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")

