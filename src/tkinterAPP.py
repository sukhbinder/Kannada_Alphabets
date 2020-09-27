import tkinter as Tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.kanada_tkinter import App
from src.say import _say

import argparse
import time


class View():
    def __init__(self, master):
        self.var = Tk.StringVar()
        self.frame = Tk.Frame(master)
        self.label = Tk.Label(self.frame, textvariable=self.var, fg="red")
        self.label.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.fig = Figure(figsize=(6, 4), dpi=80, facecolor=(0.1, 1, 1))
        self.ax0 = self.fig.add_axes(
            (0.05, .05, .90, .90), facecolor=("red"), frameon=False)
        self.frame.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.sidepanel = SidePanel(master)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.canvas.draw()

    def set_label(self, text):
        self.var = text
        self.canvas.draw()


class SidePanel():
    def __init__(self, root):
        self.frame2 = Tk.Frame(root)
        self.frame2.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)
        self.plotBut = Tk.Button(self.frame2, text="Yes")
        self.plotBut.pack(side="top", fill=Tk.BOTH)
        self.noButton = Tk.Button(self.frame2, text="No")
        self.noButton.pack(side="top", fill=Tk.BOTH)
        self.playButton = Tk.Button(self.frame2, text="Play")
        self.playButton.pack(side="bottom", fill=Tk.BOTH)
        self.checkButton = Tk.Button(self.frame2, text="Check")
        self.checkButton.pack(side="bottom", fill=Tk.BOTH)
        self.clearButton = Tk.Button(self.frame2, text="Clear")
        self.clearButton.pack(side="bottom", fill=Tk.BOTH)


class Controller():
    def __init__(self, user="barun"):
        self.root = Tk.Tk()
        self.app = App(user=user)
        self.view = View(self.root)
        self.view.sidepanel.plotBut.bind("<Button>", self.yes_word)
        self.view.sidepanel.clearButton.bind("<Button>", self.clear)
        self.view.sidepanel.playButton.bind("<Button>", self.say_word)
        self.view.sidepanel.noButton.bind("<Button>", self.no_word)
        self.view.sidepanel.checkButton.bind("<Button>", self.my_plot)

    def run(self):
        self.root.title("Kanada Learning")
        self.selected_word = self.app.get_selected_word()
        self.root.deiconify()
        self.view.set_label(self.app.print_next_review_day())
        self.selected_word = self.app.get_selected_word()
        self.word = self.get_word(event=None)
        self.say_word(event=None)
        self.updated_word = []
        self.root.mainloop()

    def get_word(self, event):
        word = None
        if self.selected_word:
            word = np.random.choice(self.selected_word)
        return word

    def no_word(self, event):
        if self.word:
            self.my_plot(event)
            self.word.decrement()
            self.word.update_due_date()
            self.word = self.get_word(event)
            self.say_word(event)
            self.clear(event)

    def yes_word(self, event):
        if self.word:
            self.my_plot(event)
            self.word.increment()
            self.word.update_due_date()
            self.updated_word.append(self.word)
            self.selected_word.remove(self.word)
            self.word = self.get_word(event)
            self.say_word(event)
            self.clear(event)
            self.view.set_label(
                "{} words to go".format(len(self.selected_word)))

    def clear(self, event):
        self.view.ax0.clear()
        self.view.fig.canvas.draw()
        self.view.ax0.set_xticks([])
        self.view.ax0.set_yticks([])

    def say_word(self, event):
        if self.word is not None:
            _say("Write this word")
            self.app.play(self.word.question)
            time.sleep(2)
            self.app.play(self.word.question)
        else:
            _say("All Done")
            msg_text = self.app.print_next_review_day()
            if "-" in msg_text:
                _say("Next review is now")
            else:
                _say(msg_text)
            if self.updated_word:
                self.app.save_words(self.updated_word)

    def my_plot(self, event):
        self.view.ax0.clear()
        self.app.show_image(
            self.word.answer, ax=self.view.ax0, fig=self.view.fig)
        self.view.fig.canvas.draw()


def main():
    parser = argparse.ArgumentParser(description="Kanada study and revision")
    parser.add_argument("-u", "--user", type=str, help="New Users starts new", default="barun")
    
    args = parser.parse_args()

    c = Controller(args.user)
    c.run()


if __name__ == '__main__':
    main()