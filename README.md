# CloneHero Scoreboard

## The problem

You're rocking out on Sweet Child o' Mine, and you're bringing the house down! You nail the solos, and reach the end. That's when you see it -

> NEW HIGH SCORE!

So what are your options at this point? Well you can't export your high scores, but you *can* take a screenshot.

While lots of tools help you understand your performance while you're playing, there isn't a good way to view your data outside of the game aside from those screenshots. If only you could export them to a CSV and open them in a spreadsheet. Or even better, wouldn't it be great if you could just see your high scores appear in a Google Sheet?

## The solution

CloneHero Scoreboard uses OCR to lift the text off of your screenshots, organizes them for you, and can export them to a CSV and/or a Google Sheet! 

## Installation

### Requirements
* [Python 3.9.1](https://www.python.org/downloads/) (The latest release as of this writing)
* [Tesseract](https://github.com/tesseract-ocr/tesseract)
* [Optional] Google Cloud Service Account (for exporting directly to a Google Sheet) ([Instructions here](https://gspread.readthedocs.io/en/latest/oauth2.html))

### Instructions

1. Clone this repo
2. Run `python3 setup.py install`
3. Back up your screenshot directory
4. Run the script

For example:
```
python3 scoreboard.py --img_dir=/path/to/clonehero/screenshots --google_sheet="My CloneHero High Scores" --remove_captured
```

## Advanced usage

As shown in the example above, the script supports multiple flags. To see all available flags, run -
```
python3 scoreboard.py --help
```

The script can also be added to a crontab or scheduled task to run every so often. How does one do this?

* [Linux Crontab](https://opensource.com/article/17/11/how-use-cron-linux)
* [Windows Scheduler](https://datatofish.com/python-script-windows-scheduler/)

## FAQ

* Q: Why didn't CHS export my score(s)?
* A: It probably couldn't find your score in the screenshot. The script attempts 3 different ways of lifting the score off the image. If it fails to get the score all 3 times, it will skip the song entirely.
---
* Q: Will you fix *foo* issue? 
* A: Maybe if you ask nicely? ;)
---
* Q: Will you implement *foo* feature?
* A: Maybe if you ask nicely and send cookies?

