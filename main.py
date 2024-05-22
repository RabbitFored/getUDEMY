import os
import logging
import telegram
import datetime
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from bs4 import BeautifulSoup as bs
from telegram import Update
import json
import emoji
from alive import keep_alive

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!\nI can give you free udemy coupons')


def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('''
Useful commands:

/start  - Check if I'm alive
/help   - Get this text
/about - about me
/donate - Donate us

/coupon - Get udemy coupons
/info - Get a course info
    ''')


def aboutTheBot(update, context):
    """Log Errors caused by Updates."""

    keyboard = [
        [
            telegram.InlineKeyboardButton(
                (emoji.emojize(":loop:", use_aliases=True)) + "Channel",
                url="t.me/theostrich"),
            telegram.InlineKeyboardButton("👥Support Group",
                                          url="t.me/ostrichdiscussion"),
        ],
        [
            telegram.InlineKeyboardButton(
                (emoji.emojize(":bookmark:", use_aliases=True)) +
                "Add Me In Group",
                url="https://t.me/getUDEMYbot?startgroup=new")
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "<b>Hey!</b>"
        "\nI can provide you free udemy coupons."
        "\n\n<b>About Me :</b>"
        "\n\n  - <b>Name</b>        : GetUdemyBot"
        "\n\n  - <b>Creator</b>      : @theostrich"
        "\n\n  - <b>Language</b>  : Python 3"
        "\n\n  - <b>Library</b>       : <a href=\"https://github.com/python-telegram-bot/python-telegram-bot/\">python-telegram-bot</a>"
        "\n\nIf you enjoy using me and want to help me survive, do donate with the /donate command - my creator will be very grateful! Doesn't have to be much - every little helps! Thanks for reading :)",
        parse_mode='html',
        reply_markup=reply_markup,
        disable_web_page_preview=True)


def donate(update, context):
    keyboard = [
        [
            telegram.InlineKeyboardButton(
                "Contribute", url="https://github.com/RabbitFored"),
            telegram.InlineKeyboardButton(
                "Paypal Us", url="https://paypal.me/donateostrich"),
        ],
    ]

    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Thank you for your wish to contribute. I hope you enjoyed using our services. Make a small donation/contribute to let this project alive.",
        reply_markup=reply_markup)


def coupon(update: Update, context: CallbackContext):

    edit = update.message.reply_text("Gathering coupons...")
    coupons = getcoupons()

    for i in range(len(coupons)):
        title, description, rating, lang, price, paid, instructor = demyscr(
            coupons[i])

        update.message.reply_text(
            f'🌀{title}🌀\n\n<b>━━━━━━━━━━━━━━━━</b>\n<b>Rating:</b> {rating} \n<b>Language :</b> {lang} \n<b>Original Price : </b>{price}\n<b>Instructor : </b>{instructor}\n<b>📜Description : </b>{description}\n<b>━━━━━━━━━━━━━━━━━</b>\n<b>Enrollment link:</b>\n{coupons[i]}',
            parse_mode="html",
            disable_web_page_preview=True)
    edit.delete()


def demyscr(url):
    get = requests.get(url)
    api = 'https://www.udemy.com/api-2.0/courses/' + url[29:]
    apireq = requests.get(api).content
    jsonise = json.loads(apireq)
    

    soup = bs(get.content, "html5lib")

    title = soup.title.get_text()

    description = soup.find(
        'div', class_='ud-text-md clp-lead__headline').get_text()

    rating = soup.find(
        'span',
        class_='ud-heading-sm star-rating-module--rating-number--2-qA2').get_text(
        )

    lang = soup.find(
        'div', class_='clp-lead__element-item clp-lead__locale').get_text()

    price = jsonise['price']

    paid = jsonise['is_paid']

    instructor = jsonise['visible_instructors'][0]['display_name']

    return title, description, rating, lang.strip(), price, paid, instructor


def autocoups(context: telegram.ext.CallbackContext):
    coupons = getcoupons()
    join = []
    for i in range(len(coupons)):
        split = coupons[i].split("?")
        try:
            joins = split[0] + "?join:@Udemy_Blaster&" + split[1]
            join.append(joins)
        except:
            joins = split[0] + "?join:@Udemy_Blaster"
            join.append(joins)

    for i in range(len(coupons)):
        title, description, rating, lang, price, paid, instructor = demyscr(
            coupons[i])
        if lang == "English":

            context.bot.sendMessage(
                chat_id="@Udemy_Blaster",
                text=
                f'🌀{title}🌀\n\n<b>━━━━━━━━━━━━━━━━</b>\n<b>Rating:</b> {rating} \n<b>Language :</b> {lang} \n<b>Original Price : </b>{price}\n<b>Instructor : </b>{instructor}\n<b>📜Description : </b>{description}\n<b>━━━━━━━━━━━━━━━━━</b>\n<b>Enrollment link:</b>\n{join[i]}',
                parse_mode="html")


def getcoupons():
    discudemy = "https://www.discudemy.com/all/"
    index = requests.get(discudemy)

    soup = bs(index.content, "html5lib")

    gosearch = soup.find_all(class_="card-header")

    gopages = []

    for i in range(len(gosearch)):
        try:
            getgo = gosearch[i]["href"]
            gopages.append(getgo)
        except:
            print("Some Error encountered")

    golinks = []

    for i in range(len(gopages)):
        gosource = requests.get(gopages[i])
        gosoup = bs(gosource.content, "html5lib")
        final = gosoup.find_all(class_="ui big inverted green button discBtn")
        for i in range(len(final)):
            golinks.append(final[i]["href"])

    coupons = []

    for i in range(len(golinks)):
        req = requests.get(golinks[i])
        coupsoup = bs(req.content, "html5lib")
        coupdiv = coupsoup.find_all(class_="ui segment")
        for i in range(len(coupdiv)):
            coup = (coupdiv[i].a)["href"]
            coupons.append(coup)

    return coupons


def format(update, context):
    url = context.args[0]
    try:
        title, description, rating, lang, price, paid, instructor = demyscr(
            url)
        update.message.reply_text(
            f'🌀{title}🌀\n\n<b>━━━━━━━━━━━━━━━━</b>\n<b>Rating:</b> {rating} \n<b>Language :</b> {lang} \n<b>Original Price : </b>{price}\n<b>Instructor : </b>{instructor}\n<b>📜Description : </b>{description}\n<b>━━━━━━━━━━━━━━━━━</b>\n<b>Enrollment link:</b>\n{url}',
            parse_mode="html",
            disable_web_page_preview=True)
    except:
        update.message.reply_text("Cannot extract course info.")


def main():

    updater = Updater(os.environ['token'])
    j = updater.job_queue
    time = datetime.time(hour=4, minute=00, second=00)
    j.run_daily(autocoups, time)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start, run_async=True))
    dispatcher.add_handler(CommandHandler("help", help, run_async=True))
    dispatcher.add_handler(CommandHandler("about", aboutTheBot,
                                          run_async=True))
    dispatcher.add_handler(CommandHandler("donate", donate, run_async=True))
    dispatcher.add_handler(CommandHandler("coupon", coupon, run_async=True))
    dispatcher.add_handler(CommandHandler("info", format, run_async=True))

    keep_alive()
    updater.start_polling()



if __name__ == '__main__':
    main()
