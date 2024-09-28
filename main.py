from playwright.sync_api import sync_playwright
from repository import Repository
test = [
    {
        "from":"sdq",
        "to":"jfk",
        "months": [10, 1]
    }
]
def main():
    for flight in test:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            repository = Repository(page)
            repository.setAirport(isArrival=False, airport="sdq")
            repository.setAirport(isArrival=True, airport="jfk")
            repository.search()
            repository.setNonstop()
            repository.loadMonthsNumbers()
            print(repository.findLowestFromMonth(month=9, exclude=["Saturday", 28]))
            browser.close()
    pass
main()