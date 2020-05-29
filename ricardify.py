import telegram_send, time
import json
import argparse, os, sys
from datetime import date, timedelta

from urllib.request import urlopen
from bs4 import BeautifulSoup

def ad_known(id):
    for i, d in enumerate(dic["inserate"]):
        if d["id"] == id:
            return 1
    return 0

# Parse arguments
parser = argparse.ArgumentParser(
description="This script will watch ricardo.ch for new ads and notify you via telegram. Also, it keeps a record of listings with prices in a JSON file."
)
parser.add_argument('query', metavar="Query", type=str, help='tutti.ch search string')
parser.add_argument('-z', '--zipcode', metavar="ZIPcode", type=int, default=0,
    help="ZIP code")
parser.add_argument('-r', '--range', metavar="Range", type=int, default=20,
    help="The range in km around ZIP code.")
parser.add_argument('-ma', '--maxprice', metavar="maxPrice", type=int, default=0,
    help="Highest price to still look for.")
parser.add_argument('-mi', '--minprice', metavar="minPrice", type=int, default=0,
    help="Lowest price to still look for.")
parser.add_argument('-s', '--silent', action='store_true', default=False,
    help="Don't send notifications.")

args = parser.parse_args()

# Header for requests
headers = {
    'User-Agent': 'Anon',
    'From': 'your.email@here.com'
}

while True:
    try:
        # Build up url with queries
        search_url = 'https://www.ricardo.ch/de/s/'

        search_url += args.query.lower().replace(" ", "%20") + '?'

        if args.maxprice:
            search_url += "&range_filters.price.max=" + str(args.maxprice)

        if args.minprice:
            search_url += "&range_filters.price.min=" + str(args.minprice)

        if args.zipcode:
            search_url += "&zip_code=" + str(args.zipcode)

            if args.range:
                search_url += "&range=" + str(args.range)

        # Download page
        html = urlopen(search_url)
        soup = BeautifulSoup(html, features="lxml")

        list_all = soup.body.find_all('a', attrs={"class":"link--2OHFZ"})

        n_new = 0
        sys.stdout.write("\r {} new listings".format(n_new))

        for item in list_all:

            url = item.get("href")
            url = "https://www.ricardo.ch" + url
            unique_id = url[-11:-1]

            all_text = item.find_all(text=True)

            if "turned_in_not" in all_text: all_text.remove("turned_in_not")

            emoji = ""
            if "rocket" in all_text:
                all_text.remove("rocket")
                emoji += "🚀"

            title = all_text[0]

            if "Neu eingestellt" in all_text:
                all_text.remove("Neu eingestellt")
                emoji += "🆕"

            bids = all_text[2]
            price = all_text[3]

            if not "Sofort kaufen" in all_text:
                # auction only
                buy_now = "nur Auktion"

            elif len(all_text) == 4:
                # buy now only
                buy_now = "nur Sofortkauf"

            elif len(all_text) == 6:
                # both
                buy_now = all_text[4] + ": " + all_text[5]

            # Create dict for first advertisement
            new_dict = {"id": unique_id, "name" : title, "url" : url, "bids": bids, "price": price, "buy_now": buy_now}

            # Check if file exists already and create if not
            fname = args.query.lower() + "_dictionary.json"
            if not os.path.isfile(fname):
                mydict = {}
                mydict["inserate"] = []
                listings = mydict["inserate"]
                listings.append(new_dict)

                with open(fname, 'w') as f:
                    json.dump(mydict, f)

                # notify
                n_new += 1
                sys.stdout.write("\r {} new listings".format(n_new))

                if not args.silent:
                    message = 'Neues Inserat: ' + emoji + '{} - {}: {} - {}.'.format(title, bids, price, buy_now)
                    message += '\n{}'.format(url)
                    telegram_send.send(messages=[message])

            else:
                with open(fname,'r+') as f:
                    dic = json.load(f)

                    if ad_known(unique_id):
                        # do nothing
                        pass

                    else:
                        dic["inserate"].append(new_dict)
                        f.seek(0)
                        json.dump(dic, f)

                        # notify
                        n_new += 1
                        sys.stdout.write("\r {} new listings".format(n_new))

                        if not args.silent:
                            message = 'Neues Inserat: ' + emoji + '{} - {}: {} - {}.'.format(title, bids, price, buy_now)
                            message += '\n{}'.format(url)
                            telegram_send.send(messages=[message])

            # Close file
            f.close()

        # Wait a minute
        time.sleep(60)

    except:
        # Wait half a minute, in case the server isn't reachable
        sys.stdout.write("\nServer not reachable or other error")
        time.sleep(30)
