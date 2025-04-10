import tkinter as tk
from galvenais import JSONTimeStampSaglabatajs
from vizualization import JSONTimeStampVizualizetjas

if __name__ == "__main__":
    root = tk.Tk()

    # Choose ONE of the two lines below depending on what you want to launch
    app = JSONTimeStampSaglabatajs(root)         # main data saving app
    #app = JSONTimeStampVizualizetjas(root)     # visualization UI

    root.mainloop()
