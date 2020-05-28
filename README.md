# ricardify

 Little sister of [tuttify](https.//github.com/kferrari/tuttify). Still a work-in-progress.

 ### Install

 * Clone this repo or download ricardify.py.
 * Edit headers{} in ricardify.py to include your name and email address, if you want. This is good practice in case someone over at tutti.ch wants to contact you.
 * Install [telegram-send](https://pypi.org/project/telegram-send/) and run `telegram-send --configure` to set up your personal Bot.
 * Install [beautifulsoup](https://pypi.org/project/beautifulsoup4/).

 ### Usage

 Simple run

 ```bash
 python3 ricardify.py sofa

 python3 ricardify.py "raspberry pi 4"
 ```

 To run in background

 ```bash
 nohup python3 -u ricardify.py sofa &
 ```

 The first run for each unique query will build a dictionary of existing listings and save it to a JSON file. It also sends a message for each listing. To avoid cluttering of your Telegram conversation, use the `--silent` flag first. Later, re-run without the flag to only be notified about new listings.

 ```bash
 python3 ricardify.py sofa --silent
 ```

 To only search a specific ZIP code, use `--zipcode`. Use `--range` to also include a range in km.

 ```bash
 python3 ricardify.py sofa --zipcode 8000 --range 25
 ```

 To define a price range, use `--maxprice` and/or `--minprice`

 ```bash
 python3 ricardify.py sofa --minprice 10 --maxprice 150
 ```
