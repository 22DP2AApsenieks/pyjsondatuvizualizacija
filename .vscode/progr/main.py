import tkinter as tk
from galvenais import JSONTimeStampSaglabatajs
from vizualization import JSONTimeStampVizualizetjas

if __name__ == "__main__": #this will hapen if in those other programm it find name = main
    root = tk.Tk()
    app = JSONTimeStampSaglabatajs(root) #šis 
    """ app = JSONTimeStampVizualizetjas(root)"""
    root.mainloop()
