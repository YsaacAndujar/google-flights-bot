import datetime
from playwright.async_api import Page, Request, Response

class GoogleBotRepository():
    url = "https://www.google.com/travel/flights?hl=en&curr=USD"
    page: Page
    maxCalendarMonthReached = 2
    monthsNumbers = []
    _monthsNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    _callingCalendarApi = 0

    def __init__(self, page: Page):
        self.page = page
        page.on('request', self._onRequest)
        page.on('response', self._onResponse)

    async def init_page(self):
        await self.page.goto(self.url)
        await self.page.get_by_label('Round trip').nth(0).click()
        await self.page.wait_for_timeout(1000)
        await self.page.keyboard.press("ArrowDown")
        await self.page.keyboard.press("Enter")
        await (await self.getCalendarInput()).click()
        await self.page.wait_for_timeout(500)
        await self.page.keyboard.press("ArrowRight")
        await self.page.keyboard.press("Enter")

    async def _onRequest(self, request: Request):
        if request.method == "POST" and "getcalendarpicker" in request.url.lower():
            self._callingCalendarApi += 1

    async def _onResponse(self, response: Response):
        if response.request.method == "POST" and "getcalendarpicker" in response.request.url.lower():
            self._callingCalendarApi -= 1

    def getInputAirport(self, isArrival=True):
        labelText = 'Where to' if isArrival else 'Where from'
        return self.page.locator(f"input[aria-label^='{labelText}']")

    async def setNonstop(self):
        await self.page.get_by_text('Stops').click()
        await self.page.get_by_text('Nonstop only').click()

    async def search(self):
        await self.getInputAirport().focus()
        await self.page.keyboard.press("Tab")
        await self.page.keyboard.press("Tab")
        await self.page.keyboard.press("Enter")

    async def reachMonth(self, month):
        index = self.monthsNumbers.index(month)
        while index + 1 > self.maxCalendarMonthReached:
            await self.nextCalendarMonth()
            self.maxCalendarMonthReached += 1
            await self.page.wait_for_timeout(200)

    async def findLowestFromMonth(self, *, month, include=[], exclude=[]):
        await self.reachMonth(month)
        await self.page.wait_for_timeout(1000)
        trys = 1
        while self._callingCalendarApi > 0:
            await self.page.wait_for_timeout(1000)
            if trys > 20:
                raise TimeoutError("Calendar API timeout")
            trys += 1

        rowgroups = self.page.get_by_role("rowgroup")
        rows = rowgroups.nth(self.monthsNumbers.index(month)).get_by_role('row')
        prices = []
        for i in range(await rows.count()):
            row = rows.nth(i)
            gridcells = row.get_by_role("gridcell")
            for x in range(await gridcells.count()):
                gridcell = gridcells.nth(x)
                dateDiv = gridcell.locator(f"[aria-label*='{self._monthsNames[month-1]}']")
                dateArray = [item.strip() for item in (await dateDiv.get_attribute('aria-label')).replace(',', '').split()]
                if len(exclude) > 0 and (dateArray[0] in exclude or int(dateArray[2]) in exclude):
                    continue
                if len(include) > 0 and not (dateArray[0] in include or int(dateArray[2]) in include):
                    continue
                pricesDiv = gridcell.locator("[aria-label$='US dollars']")
                for y in range(await pricesDiv.count()):
                    priceDiv = pricesDiv.nth(y)
                    price = int((await priceDiv.inner_text()).replace('$', ''))
                    prices.append(price)
        return min(prices) if prices else None

    async def loadMonthsNumbers(self):
        await (await self.getCalendarInput()).click()
        firstRowgroup = self.page.get_by_role("rowgroup").nth(0)
        firstDiv = firstRowgroup.locator("div").nth(0)
        monthNumber = datetime.datetime.strptime(await firstDiv.inner_text(), "%B").month
        for i in range(12):
            self.monthsNumbers.append(monthNumber)
            monthNumber += 1
            if monthNumber > 12:
                monthNumber = 1

    async def nextCalendarMonth(self):
        await self.page.get_by_label('Next').nth(0).click()

    async def getCalendarInput(self):
        calendar = self.page.get_by_placeholder('Departure')
        return calendar if (await calendar.count()) == 1 else calendar.nth(0)

    async def setAirport(self, *, isArrival, airport):
        await self.getInputAirport(isArrival).fill(airport)
        await self.page.wait_for_timeout(500)
        await self.page.keyboard.press("ArrowDown")
        await self.page.keyboard.press("Enter")