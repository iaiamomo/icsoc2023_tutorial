from tkinter import ttk
import tkinter as tk
from GUI.RunTime_lmdp import RunTimePage_lmdp
from GUI.RunTime_plan import RunTimePage_plan
from GUI.PreRunTime import PreRunTimePage
from GUI.DesignTime import DesignTime
from tkinter import filedialog
from tkinter import Text
from tkinter import END
import tkinter.messagebox as msgbox
import os
import tkinter.font as font
import json
import tkinter as tk
from constants import *


class tkinterApp(tk.Tk):
    
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
       
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
         
        # creating a container
        self.geometry("1920x1080")
        container = tk.Frame(self)
        self.title("AIDA")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        #container.grid(side = "top", fill = "both", expand = True)
        container.grid(row=0, column=0, sticky= "nsew")
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # initializing frames to an empty array
        self.frames = {} 
        # iterating through a tuple consisting of the different page layouts
        for F in (StartPage, DesignTime, PreRunTimePage, RunTimePage_lmdp, RunTimePage_plan):
            frame = F(container, self)
            
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")
        
        self.show_frame(StartPage) 
        
 
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


    def show_RunTimePage_lmdp(self):
        self.show_frame(RunTimePage_lmdp)    

    def get_RunTimePage_lmdp(self):
        return self.frames[RunTimePage_lmdp]
    
    def show_RunTimePage_plan(self):
        self.show_frame(RunTimePage_plan)    

    def get_RunTimePage_plan(self):
        return self.frames[RunTimePage_plan]
    

    def getFrame(self, cont):
        return self.frames[cont]

    def get_PreRunTimePage(self):
        return self.frames[PreRunTimePage]
    

    def show_mainPage(self):
        self.show_frame(StartPage)


    def design_time(self):
        self.show_frame(DesignTime)
        folder = filedialog.askdirectory(
            title='Select the folder', #name of the tab
            initialdir="./", #initial shown directory
        )
        while not folder:
            msgbox.showerror("Error", "Please select a folder")
            folder = filedialog.askdirectory(
                title='Select the folder', #name of the tab
                initialdir="./", #initial shown directory
            )
        try:
            os.mkdir(folder)
        except:
            print()
        frame = self.getFrame(DesignTime) #retrive the frame instance, otherwise it uses the generic class 
        frame.path = str(folder)
        frame.refreshListBox()

    
    def run_time(self):
        self.show_frame(PreRunTimePage) #tell show_frame to load runTimePage
        config_file = filedialog.askopenfilename(
            title="Select the config file",
            initialdir="./config_files"
        )
        while not config_file:
            msgbox.showerror("Error", "Please select a file")
            config_file = filedialog.askopenfilename(
                title="Select the config file",
                initialdir="./config_files"
            )
        config_json = json.load(open(config_file))
        folder = config_json['folder']
        mode = config_json['mode']
        if not os.path.isdir(folder):
            msgbox.showerror("Error", "The folder specified in the config file does not exist")
            self.show_mainPage()
            return
        
        temp : PreRunTimePage = self.getFrame(PreRunTimePage)
        temp.config_file = str(config_file)
        #temp.check_files_config()
        temp.set_files()

        if mode == 'lmdp_ltlf':
            temp : RunTimePage_lmdp = self.getFrame(RunTimePage_lmdp)
            temp.config_file = str(config_file)
            temp.set_image_services()
            temp.refreshComboBox()
        elif mode == 'plan':
            temp : RunTimePage_plan = self.getFrame(RunTimePage_plan)
            temp.config_file = str(config_file)
            temp.set_image_services()
            temp.refreshComboBox()


# first window frame startpage  --START PAGE--
class StartPage(tk.Frame):
    def __init__(self, parent, controller : tkinterApp):
        self.controller = controller
        
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.option_add("*Font","aerial") #change font size 
        style = ttk.Style()
        style.configure('CustomButton.TButton', font=MEDIUMFONT)
    
        # label of frame
        label = ttk.Label(self, text ="AIDA", font = LARGEFONT)
        label.grid(row = 0, column =0, padx = 10, pady = 10)
  
        # button planning
        button1 = ttk.Button(self, text ="Design time",
            command = self.desig_time,
            style='CustomButton.TButton',
            width= 30
        )
        button1.grid(row = 1, column = 0, padx = 10, pady = 10)
  
        # button stochastic constraint-based policy
        button2 = ttk.Button(self, text ="Run Time",
            command = self.run_time,
            style='CustomButton.TButton',
            width= 30
        )
        button2.grid(row = 2, column = 0, padx = 10, pady = 10)

    def desig_time(self):
        self.controller.design_time()

    def run_time(self):
        self.controller.run_time()


# Driver Code
app = tkinterApp() ##app corresponds to the object app, its attributes are: 
app.mainloop()