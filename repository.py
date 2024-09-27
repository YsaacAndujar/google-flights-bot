import time
from playwright.sync_api import Page
import datetime

class Repository():
    url="https://www.google.com/travel/flights?hl=en&curr=USD"
    page:Page
    maxCalendarMonthReached = 2
    monthsNumbers=[]
    def __init__(self, page:Page):
        self.page = page
        page.goto(self.url)
        page.get_by_label('Round trip').nth(0).click()
        time.sleep(1)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        self.getCalendarInput().click()
        time.sleep(0.5)
        page.keyboard.press("ArrowRight")
        page.keyboard.press("Enter")

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

    
    def findLowestFromMonth(self, month):
        self.reachMonth(month)
        time.sleep(0.5)
        rowgroups = self.page.get_by_role("rowgroup")
        rows = rowgroups.nth(self.monthsNumbers.index(month)).get_by_role('row')
        gridcells = rows.get_by_role("gridcell")
        pricesDiv = gridcells.locator("[aria-label$='US dollars']")
        time.sleep(10)
        print(pricesDiv.count())
        for i in range(0, pricesDiv.count()-1):
            priceDiv = pricesDiv.nth(i)
            print(priceDiv.inner_text())
        # # Itera sobre cada elemento y encuentra el primer <div> dentro
        # for i in range(rowgroups.count()):
        #     # Selecciona el elemento actual
        #     rowgroup = rowgroups.nth(i)
        #     firstDiv = rowgroup.locator("div").nth(0)
        #     print(firstDiv.inner_text())
    
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

