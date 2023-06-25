import tkinter as tk
from tkinter import ttk
import os
from tkinter import messagebox as msgbox
import json
import glob

LARGEFONT = ("Verdana", 24)

class PreRunTimePage(tk.Frame):
    def __init__(self, parent, controller):    
        self.config_file = ''
        self.controller = controller
        
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        style.configure('CustomButton.TButton', font=('Arial', 19)) 
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(column=0, row= 5, pady= 50)

        homeButton = ttk.Button(buttonFrame, text ="Home", command = lambda : self.goHome(), style='CustomButton.TButton')
        homeButton.grid(row = 0, column = 0, padx=10)
        
        exectueButton = ttk.Button(buttonFrame, text= "EXECUTE", command= self.execute, style='CustomButton.TButton')
        exectueButton.grid(row= 0, column= 1, padx=10)

        self.backgroundFrame = tk.Frame(self)
        self.backgroundFrame.grid(column= 0, row= 1)

        servicesLabel = ttk.Label (self.backgroundFrame, text = "SERVICES:", font= LARGEFONT)
        servicesLabel.grid(row =1, column=0)

        targetsLabel = ttk.Label (self.backgroundFrame, text= "TARGETS:", font= LARGEFONT)
        targetsLabel.grid(row = 3, column= 0)

        servicesScrollbar = tk.Scrollbar(self.backgroundFrame, width=17)
        servicesScrollbar.grid(row=2, column=1)

        self.servicesListBox = ttk.Treeview(self.backgroundFrame, height=17, columns=("Name", "Validity"), show='headings', yscrollcommand=servicesScrollbar)
        self.servicesListBox.grid(row = 2, column= 0, pady=10)

        servicesScrollbar.config(command = self.servicesListBox.yview)
        
        self.targetsListBox = ttk.Treeview(self.backgroundFrame, height=2, columns=("Name", "Validity") , show='headings')
        self.targetsListBox.grid(row = 4, column= 0)


    def execute(self):
        with open(self.config_file) as json_file:
            data = json.load(json_file)

        mode = data["mode"]

        if (len(self.targetsListBox.get_children())):
            if mode == "lmdp_ltlf":
                self.controller.show_RunTimePage_lmdp()
            elif mode == "plan":
                self.controller.show_RunTimePage_plan()
        else:
            msgbox.showerror("check your files", "Please, check the .tdl file and try again.")
            self.controller.show_mainPage()


    def set_files(self):
        if self.config_file == "":
            msgbox.showerror("File config", "You need to select a config file.")
            self.controller.show_mainPage()
            return

        with open(self.config_file) as json_file:
            data = json.load(json_file)

        folder_name = data["folder"]
        
        self.setColumnsNames(self.servicesListBox)
        self.setColumnsNames(self.targetsListBox)

        self.loadListBoxs(folder_name)


    def loadListBoxs(self, folder_name):
        service_list = [file for file in os.listdir(folder_name) if file.endswith(".sdl")] 
        target_list = [file for file in os.listdir(folder_name) if file.endswith(".tdl")]
        
        for file in service_list:
            self.servicesListBox.insert('', 'end', text="0", values=(str(file), 'ok!')) #for now, the validity is not implemented, it just shows ok for everyone
        for file in target_list:
            self.targetsListBox.insert('', 'end', text="0", values=( str(file), 'ok!'))# validity is not implemented yet


    def setColumnsNames(self, listBox): #This method create headings names, and change text size to be bigger
        style1 = ttk.Style()
        style1.configure("Treeview.Heading", font=(None, 22), ) #changing heading text size
        style1.configure("Treeview", font=(None, 16), rowheight = 20) #changing elements text size

        listBox.column( "#1", anchor= "center" , width = 400)
        listBox.heading("#1", text="Name")
        listBox.column( "#2", anchor= "center", width = 200)
        listBox.heading("#2", text="Validity")

    
    def check_files_config(self):
        if self.config_file == "":
            msgbox.showerror("File config", "You need to select a config file.")
            print("1")
            self.controller.show_mainPage()
            return

        with open(self.config_file) as json_file:
            data = json.load(json_file)

        folder_name = data["folder"]
        services = [service["name_file"] for service in data["services"]]

        files = glob.glob(f"{folder_name}/*.sdl") + glob.glob(f'{folder_name}/*.tdl')
        print(files)

        for f in files:
            service_name = f.split("/")[-1]
            if service_name not in services:
                # ERROR
                msgbox.showerror("check your files", "Please, check the files in folder and try again. They are not coherent with the config file.")
                print("1")
                self.controller.show_mainPage()
                break

    
    def resetPage(self):
        self.config_file = ''
        self.servicesListBox.delete(*self.servicesListBox.get_children())
        self.targetsListBox.delete(*self.targetsListBox.get_children())


    def goHome(self):
        self.resetPage()
        self.controller.get_RunTimePage_lmdp().resetPage()
        self.controller.get_RunTimePage_plan().resetPage()
        self.controller.show_mainPage()