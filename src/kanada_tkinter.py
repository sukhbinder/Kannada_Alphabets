from src.say import _say
import os
import pandas as pd
from datetime import datetime, timedelta
import argparse
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process


ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 

THESHOLDS = [timedelta(seconds=120), timedelta(hours=3), timedelta(hours=7), timedelta(hours=24), timedelta(days=2), timedelta(
    days=4), timedelta(days=8), timedelta(days=16), timedelta(days=28), timedelta(days=90), timedelta(days=180)]


def _play_audio(file):
    os.system("afplay {} -v 15".format(file))

def play_audio(file):
    process = Process(target=_play_audio,
                      args=(file,), daemon=True)
    process.start()

def format_timedelta(delta):
    seconds = abs(int(delta.total_seconds()))
    periods = [
        (60 * 60 * 24 * 365, 'year'),
        (60 * 60 * 24 * 30, 'month'),
        (60 * 60 * 24, 'day'),
        (60 * 60, 'hour'),
        (60, 'minute'),
        (1, 'second')
    ]

    parts = []
    for period_seconds, period_name in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            part = '%s %s' % (period_value, period_name)
            if period_value > 1:
                part += 's'
            parts.append(part)
    ret = ', '.join(parts)
    if delta.total_seconds() < 0:
        ret = '-' + ret
    return ret


class Card:
    def __init__(self, question, answer, num=0, due_date=datetime.now(), active=False):
        self.question = question
        self.answer = answer
        self.num = num
        self.due_date = due_date
        self.active = active

    def increment(self):
        if self.num < len(THESHOLDS):
            self.num = self.num + 1
        else:
            self.num = len(THESHOLDS)

    def decrement(self):
        if self.num > 8:
            self.num -= 4
        elif self.num >= 0:
            self.num = self.num - 1
        else:
            self.num = 0

    def update_due_date(self):
        try:
            self.due_date = datetime.now() + THESHOLDS[self.num]
        except Exception as ex:
            self.due_date = datetime.now() + THESHOLDS[self.num-1]

    def toggle_acive(self):
        self.active = not self.active

    def __repr__(self):
        return "{0} {1} {2} {3}".format(self.question, self.num, self.active, self.due_date)



class App():
    def __init__(self, user="sonu", nwords=10):
        self.user = user
        self.nwords =nwords
        
        self.soundpath = os.path.join(ROOT_DIR, "assets","sound")
        self.imagepath = os.path.join(ROOT_DIR, "assets","img")
        self.word_file = os.path.join(os.path.expanduser("~"), "{}.kwords".format(self.user))
        self.wordlist = None

        self.init()
        self.get_wordlist()

    def init(self):
        self.data = pd.read_csv(os.path.join(ROOT_DIR, "assets", "data.csv"))
    
    def play(self, mp3):
        play_audio(os.path.join(self.soundpath, mp3))

    def show_image(self, image_file, ax=None, fig=None):
        imfile = os.path.join(self.imagepath, image_file)
        if ax is None:
            fig, ax = plt.subplots()
        img = plt.imread(imfile)
        ax.imshow(img)
        # ax.set_facecolor('salmon')
        ax.set_xticks([])
        ax.set_yticks([])
        

    def get_words(self):
        fname= self.word_file
        if os.path.exists(fname):
            df = pd.read_csv(fname, infer_datetime_format=True,
                            parse_dates=["due_date"])
            df = df.sort_values(by="due_date", ascending=False)
            self.wordlist = [Card(row.question, row.answer, num=row.num,
                            due_date=row.due_date, active=row.active) for _, row in df.iterrows()]
        else:
            self.wordlist = []
        

    def save_words(self,selected_word):
        for word in selected_word:
            for w in self.wordlist:
                if word.question == w.question:
                    w.num = word.num
                    w.due_date = word.due_date
    
        pd.DataFrame(data=[(word.question, word.answer, word.due_date, word.num, word.active)
                        for word in self.wordlist], columns=["question", "answer", "due_date", "num", "active"]).to_csv(self.word_file)


    def _get_next_review_day(self):
        fname = self.word_file
        df = pd.read_csv(fname, infer_datetime_format=True,
                        parse_dates=["due_date"])
        try:
            next_due_date = df[df.num != 0].sort_values(by="due_date").iloc[0, 3]
        except Exception as ex:
            next_due_date = df[df.active].sort_values(by="due_date").iloc[0, 3]
        
        # print(df.head(), next_due_date)
        return next_due_date


    def print_next_review_day(self):
        self.get_wordlist()
        next_due_date = self._get_next_review_day()
        text_msg = "Next review in {}".format(
            format_timedelta(next_due_date-datetime.now()))
        print(text_msg)
        if "-" not in text_msg:
            _say(text_msg)
        else:
            _say("Next Revies is Now.")
        return text_msg

    def is_time_to_add_words(self):
        next_due_date = self._get_next_review_day()
        seconds_to_next_review = next_due_date-datetime.now()
        # check if the time has past 5 hours
        return seconds_to_next_review.seconds >= 60*60*5

    def get_selected_word(self):
        now = datetime.now()
        selected_word = [
            word for word in self.wordlist if word.due_date < now and word.active]
        return selected_word

    def check_next_active(self, num=5):
        if not self.is_time_to_add_words():
            return
        self.get_words()
        selected_word = [word for word in self.wordlist if word.active is False]
        if len(selected_word) > num:
            selected_word = selected_word[:num]

        for word in selected_word:
            word.active = True
            word.due_data = datetime.now()+timedelta(seconds=600)
        self.save_words(selected_word)


    def get_wordlist(self):
        if os.path.exists(self.word_file):
            self.get_words()
        else:
            self.wordlist = [Card(row["Sound"].strip(),row["Image"].strip() ) for _, row in self.data.iterrows()]
            # print(wordlist)
            for i in range(self.nwords):
                self.wordlist[i].active=True
        self.save_words(self.wordlist)

    def practice_com(self):
        # app = App()
        # user = self.user
        selected_word = self.get_selected_word()
        if selected_word:
            
            # for word in selected_word[:args.nworsds]:
            while True:
                if not selected_word:
                    break
                print("\n{} words to go \n".format(len(selected_word)))
                # print(selected_word)
                word = np.random.choice(selected_word)
                _say("Write this word")
                self.play(word.question)
                self.play(word.question)
                _say("Write this word")
                self.play(word.question)
                is_correct = confirm("Did you get it correct? yes or no: ")
                if is_correct:
                    word.increment()
                    word.update_due_date()
                    _say("Correct ")
                    selected_word.remove(word)
                else:
                    word.decrement()
                    word.update_due_date()
                    self.show_image(word.answer)
                    _say("Incorrect ")


            self.save_words(selected_word)
            _ = self.print_next_review_day()
        else:
            self.check_next_active()
    

def help_com(args):
    print("Use command lkanada practice user -n 10")

def main():
    parser = argparse.ArgumentParser(description="Kanada study and revision")
    parser.set_defaults(func=help_com)
    subparser = parser.add_subparsers()

    add_p = subparser.add_parser("practice")
    add_p.add_argument("user", type=str, help="New Users starts new")
    add_p.add_argument("-n", "--nwords", type=int, default=10)
    add_p.set_defaults(func=practice_com)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    app = App()
    app.practice_com()
