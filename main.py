from playwright.async_api import async_playwright
from GoogleBotrepository import GoogleBotRepository
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        repository = GoogleBotRepository(page)
        await repository.init_page()
        
        await repository.setAirport(isArrival=False, airport="sdq")
        await repository.setAirport(isArrival=True, airport="jfk")
        await repository.search()
        await repository.setNonstop()
        await repository.loadMonthsNumbers()
        
        result = await repository.findLowestFromMonth(month=9, exclude=["Saturday", 28])
        replyTxt = 'Not found' if result is None else result
        await update.message.reply_text(replyTxt)
        
        # Cerrar el navegador
        await browser.close()


if __name__ == '__main__':
    print(TELEGRAM_BOT_TOKEN)
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_command))
    app.run_polling(poll_interval=3)
# test = [
#     {
#         "from":"sdq",
#         "to":"jfk",
#         "months": [10, 1]
#     }
# ]
# def main():
#     for flight in test:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=False)
#             page = browser.new_page()
#             repository = Repository(page)
#             repository.setAirport(isArrival=False, airport="sdq")
#             repository.setAirport(isArrival=True, airport="jfk")
#             repository.search()
#             repository.setNonstop()
#             repository.loadMonthsNumbers()
#             print(repository.findLowestFromMonth(month=9, exclude=["Saturday", 28]))
#             browser.close()
#     pass
# main()