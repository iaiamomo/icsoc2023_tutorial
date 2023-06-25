import tkinter as tk
from tkinter import ttk
import os
from tkinter import END
from tkinter import messagebox as msgbox
from constants import *


class DesignTime(tk.Frame):

    def __init__(self, parent, controller):
        self.path = ''
        self.listBox : tk.Listbox = None
        self.controller = controller

        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        style.configure('CustomButton.TButton', font=MEDIUMFONT) 

        self.sdl_template = [file for file in os.listdir("./templates") if file.endswith(".sdl")][0]
        self.tdl_template = [file for file in os.listdir("./templates") if file.endswith(".tdl")][0]

        topFrame = tk.Frame(self, width = 200 , height= 30)
        topFrame.grid(row = 0, column= 0 )

        centerFrame = tk.Frame(self,  highlightbackground= 'black', width = 200 , height= 200)
        centerFrame.grid(row = 1, column= 0 )

        rightFrame = tk.Frame(self, width = 100 , height= 100, padx= 50, pady= 50)
        rightFrame.grid(row = 1, column= 1)
 
        bottomFrame = tk.Frame(self, width = 200 , height= 200)
        bottomFrame.grid(row = 8, column= 0 )

        buttonsFrame = tk.Frame(rightFrame)
        buttonsFrame.grid(row=2, column=0)
  
        resetButton = ttk.Button(bottomFrame, text="Reset", command= self.wipeText, style= 'CustomButton.TButton') #function to redet the whole design window, has not be implemented yet // TODO
        resetButton.grid(column=0, row=0, padx = 3, pady = 3)

        modelButton = ttk.Button(bottomFrame, text="SAVE", command= self.preSave, style= 'CustomButton.TButton') #function to load a file from local storage, for now just a single one
        modelButton.grid(column=1, row=0, padx = 3, pady = 3)

        deleteButton= ttk.Button(buttonsFrame, text="Delete file", command= self.delete_item , style= 'CustomButton.TButton') #not sure if this is essential, for now I'll just leave it here
        deleteButton.grid(column=0, row=0, padx = 8, pady = 3)               #it does the same action as Service/Target Template, for now.

        loadButton = ttk.Button(buttonsFrame, text="Load file", command= self.showFile ,style= 'CustomButton.TButton')
        loadButton.grid(column=1, row=0, padx = 8, pady = 3)
        
        label = ttk.Label(centerFrame, text ="Design Time", font = LARGEFONT)
        label.grid(row = 0, column = 0)

        self.listBox = tk.Listbox(rightFrame, width= 30, height= 25, font= SMALLFONT)
        self.listBox.grid(row= 0, column= 0)

        startPageButton = ttk.Button(bottomFrame, text ="Home", command = self.goHome , style= 'CustomButton.TButton')   
        startPageButton.grid(row = 0, column = 2, padx = 3, pady = 3)

        modelServiceButton = ttk.Button(topFrame, text = " Service Template ", command= self.loadSDLFile, style= 'CustomButton.TButton')
        modelServiceButton.grid(row = 1, column = 0, pady= 5)

        modelTargetButton =  ttk.Button(topFrame, text = " Target Template ", command= self.loadTDLFile, style= 'CustomButton.TButton')    
        modelTargetButton.grid(row = 1, column = 1, pady= 5)
        
        self.inputtxt = tk.Text(centerFrame,
            height = 38,
            width = 115,
        )
        self.inputtxt.grid(row= 1, column= 0)


    def reset(self):
        self.inputtxt.delete(1.0, END)
        self.listBox.delete(0, END)
        #loadedFileLabel.config(text = "here is the list of all loaded files: \n")
    
    
    def delete_item(self): #function called by button DELETE
        selected_index = self.listBox.curselection()
        selected_value = self.listBox.get(selected_index)
        file_path = os.path.join(self.path, selected_value)
        if selected_index:
            flag = msgbox.askyesno("Are you sure?", "do you want to permanently delete "+selected_value+" ?")
            print(flag)
            if os.path.isfile(file_path) and flag:
                os.remove(str(file_path))
                msgbox.showinfo("all gone"," File "+selected_value+ " has been deleted")
                self.listBox.delete(selected_index)
                self.reset()
                self.refreshListBox()
            

    def showFile(self): #action of button LOAD
        self.inputtxt.delete(1.0, END) #first we clean the textbox
        selected_index = self.listBox.curselection()
        selected_value = self.listBox.get(selected_index)
        file_path = os.path.join(self.path, selected_value)
        with open(str(file_path), "r") as file:
            self.inputtxt.insert(1.0,str(file.read()))


    def loadSDLFile(self):
        self.inputtxt.delete(1.0, END)
        file_path = os.path.join("templates", self.sdl_template)
        with open(str(file_path), "r") as file:
            self.inputtxt.insert(END,str(file.read()+ '\n')) #A NEWLINE IS INSERTED FOR EVERY NEW LOADED FILE


    def loadTDLFile(self):
        self.inputtxt.delete(1.0, END)
        file_path = os.path.join("templates", self.tdl_template)
        with open(str(file_path), "r") as file:
            self.inputtxt.insert(END,str(file.read()+ '\n')) #A NEWLINE IS INSERTED FOR EVERY NEW LOADED FILE   


    def preSave(self):
        info_window = tk.Toplevel()
        info_window.grab_set()
        info_window.title("Save the model")
        info_window.geometry("800x120")
        info_label = tk.Label(info_window, text="Please, select a name for the file", font= SMALLFONT )
        info_label.grid(row=0, column=0)
        boolean = tk.IntVar()
        radioButtonSDL = ttk.Radiobutton(
            info_window,
            text='.sdl',
            value=1, #TODO right now I can select both radiobuttons, while only one just have to do so
            variable= boolean
        )  

        radioButtonTDL = ttk.Radiobutton(
            info_window,
            text='.tdl',
            value=2,
            variable= boolean
        )

        radioButtonSDL.grid(row=1, column= 1)                
        radioButtonTDL.grid(row=1, column=2)
        radioButtonSDL.invoke()

        saveTextBox= tk.Text(info_window, height= 1, width= 18)
        saveTextBox.grid(row=1, column=0)

        close_button = tk.Button(info_window, text="Save", command= lambda : self.saveFile(info_window, saveTextBox.get(0.0,END).strip(), boolean) )
        close_button.grid(row=1, column=3)


    def saveFile(self, info_window, filename, boolean):
        info_window.destroy()
        info_window.update()
        if (boolean.get() == 1):
            filename = filename + ".sdl".strip()
        else:
            filename = filename + ".tdl".strip()

        try:
            file_path = os.path.join(self.path, filename)
            text_file = open(file_path, "w") 
            text_file.write(self.inputtxt.get("1.0", "end-1c").strip()) #the file is saved in the current folder
            text_file.close()
            self.inputtxt.delete(1.0, END) #textbox is now blank
            msgbox.showinfo("Information", "file " +filename+" has been saved!")
            self.refreshListBox()
        except Exception as e:
            msgbox.showerror("error", "an error occurred!"+str(e))    
        

    def goHome(self):
        self.reset()
        self.path = ''
        self.controller.show_mainPage()
        

    def wipeText(self):
        self.inputtxt.delete(1.0, END)


    def refreshListBox(self): #very ugly way to update items in the listbox
        file_list = [file for file in os.listdir(self.path) if file.endswith(".sdl") or file.endswith(".tdl")]
        self.listBox.delete(0, END)
        
        for file in file_list:
            self.listBox.insert(END,str(file))
    
    
    def emptyListBox(self):
        self.listBox.delete(0, END) #this ensures that the listbox will be empty every time the frame is loaded, before choosing the new directory
