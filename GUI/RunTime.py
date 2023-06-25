import tkinter as tk
from tkinter import ttk
import os
from tkinter import END
from tkinter import messagebox as msgbox
from PIL import ImageTk, Image #EXTRA LIBRARY --> pip install pillow
import json
from local.aida_utils import AIDAUtils
import time
import subprocess
import asyncio
from constants import *
import signal
import numpy as np
import threading
import queue


class RunTimePage(tk.Frame):
    def __init__(self, parent, controller):
        self.config_file = ''
        self.service_map = {}
        self.service_map_rectangle = {}
        self.service_map_action = {}
        self.background_canvas = None
        self.controller = controller
        self.initialRun = True
        self.n_runs = 1
        self.n_prob_mod = 1
        self.step_x = 0
        self.step_y = 0
        self.star_images = []

        self.aida = None
        self.queueInfo = None

        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=0)
        style = ttk.Style()
        style.configure('CustomButton.TButton', font=MEDIUMFONT)

        self.rightFrame = tk.Frame(self, width= 400, height= 100)
        
        buttonsFrame = tk.Frame(self.rightFrame)
        buttonsFrame.grid(column=0, row = 5, pady=40)

        self.rightFrame.pack(side = "right", padx= 20)

        self.topFrame = tk.Frame(self, width=1400)
        
        servicesLabel = ttk.Label(self.topFrame , text= "Services" , font= LARGEFONT)
        servicesLabel.pack(side= "top")
        
        self.topFrame.pack()

        self.backgroundFrame = tk.Frame(self, width= 1400)
        
        self.whiteImage = np.zeros((1200, 900))
        self.background_image = ImageTk.PhotoImage(Image.fromarray(self.whiteImage))
        
        self.background_canvas = tk.Canvas(self.backgroundFrame, width=1200, height=900)
        self.image_on_canvas = self.background_canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
        self.background_canvas.pack()

        self.backgroundFrame.pack(side= "left", padx= 20)

        self.servicesLabel = ttk.Label(self.rightFrame, text= "Execution plan", font= LARGEFONT)
        self.servicesLabel.grid(column= 0, row = 0)

        servicesScrollbar = tk.Scrollbar(self.rightFrame, width=20)
        servicesScrollbar.grid(column=1, row=1)

        self.planListBox = tk.Text(self.rightFrame, width= 40, height= 20, font= SMALLFONT, yscrollcommand=servicesScrollbar, state="disabled")
        self.planListBox.grid(column= 0, row= 1, pady=20)

        servicesScrollbar.config(command = self.planListBox.yview)

        self.comboBox = ttk.Combobox(self.rightFrame,width= 25, height= 15, font= XMEDIUMFONT, state= "readonly") #readonly avoid the user from entering values arbitarily
        self.comboBox.grid(column= 0, row= 2, pady=5)

        self.disruptionButton = ttk.Button(self.rightFrame, text="Break", command=self.breakHandler, style= 'CustomButton.TButton', state= "disabled")
        self.disruptionButton.grid(row=3, column=0)

        homeButton = ttk.Button(buttonsFrame, text="Home", command=lambda: self.goHome(), style= 'CustomButton.TButton')
        homeButton.grid(row=1, column=0, padx=10, pady=10)

        self.startButton = ttk.Button(buttonsFrame, text="Start", command= self.start, style= 'CustomButton.TButton') #no action
        self.startButton.grid(row=1, column=1, padx=10, pady=10)

        self.nextButton = ttk.Button(buttonsFrame, text="Next", command=self.next , style= 'CustomButton.TButton', state="disabled") #debug button to reset background to green
        self.nextButton.grid(row=2, column=0, padx=10, pady=10)

        self.killButton = ttk.Button(buttonsFrame, text="Kill", command=self.kill, style= 'CustomButton.TButton', state="disabled") #debug button to reset background to green
        self.killButton.grid(row=2, column=1, padx=10, pady=10)

        self.immediateRunButton = ttk.Button(buttonsFrame, text="Immediate Run", command=self.immediateRun, style= 'CustomButton.TButton', state="disabled")
        self.immediateRunButton.grid(row=3, column=0)

        self.runButton = ttk.Button(buttonsFrame, text="Run", command=self.run, style='CustomButton.TButton', state="disabled")
        self.runButton.grid(row=3, column=1)


    def start(self):
        self.reset_on_start()

        config_json = json.load(open(self.config_file))
        folder = config_json['folder']
        mode = config_json['mode']
        target_file = config_json['target_file']

        app_path = "../local/IndustrialAPI/app.py"
        self.p1 = subprocess.Popen([f"xterm -e python {app_path}"], shell=True, preexec_fn=os.setsid)

        time.sleep(3)

        launch_devices_path = "../local/IndustrialAPI/launch_devices.py"
        self.p2 = subprocess.Popen([f"xterm -e python {launch_devices_path} {folder} {mode}"], shell=True)

        time.sleep(3)

        self.queue = queue.Queue()
        target = os.path.abspath(f"{folder}/{target_file}")
        self.aida = AIDAUtils(target, self.queue)

        asyncio.get_event_loop().run_until_complete(self.aida.compute_policy())

        self.startButton.config(state= "disabled")
        self.nextButton.config(state= "normal")
        self.killButton.config(state= "normal")
        self.immediateRunButton.config(state= "normal")
        self.runButton.config(state= "normal")
        self.disruptionButton.config(state= "normal")


    def insert_text(self, message):
        self.planListBox.config(state="normal")
        self.planListBox.insert(END, message)
        self.planListBox.config(state="disabled")


    async def _next(self):
        if self.initialRun:
            self.insert_text(f"RUN {self.n_runs}\n")
            self.initialRun = False
        service, previous_state, new_state, executed_action, finished = await self.aida.next_step()
        if (previous_state == "executing" or previous_state == "ready") and (new_state == "ready" or new_state == "broken"):
            self.service_map_action[service][0]+=1
            self.update_star(service)
        self.change_rect_color(service, new_state)
        self.insert_text(f"{service} : {executed_action}\n\t{previous_state} -> {new_state}\n")
        self.planListBox.see(END)
        if finished:
            self.n_runs+=1
            msgbox.showinfo(f"Run {self.n_runs-1}", f"Run {self.n_runs-1} finished!\nContinue to re-compute LMDP...")
            self.initialRun = True
            await self.aida.recompute_lmdp()
    def next(self):
        asyncio.get_event_loop().run_until_complete(self._next())


    # method used in the immediate run and run methods
    async def _next_finished(self):
        if self.initialRun:
            self.insert_text(f"RUN {self.n_runs}\n")
            self.initialRun = False
        service, previous_state, new_state, executed_action, finished = await self.aida.next_step()
        if (previous_state == "executing" or previous_state == "ready") and (new_state == "ready" or new_state == "broken"):
            self.service_map_action[service][0]+=1
            self.update_star(service)
        self.change_rect_color(service, new_state)
        self.insert_text(f"{service} : {executed_action}\n\t{previous_state} -> {new_state}\n")
        self.planListBox.see(END)
        if finished:
            self.initialRun = True
            self.n_runs+=1
            self.n_prob_mod+=1
        return service, previous_state, new_state, executed_action, finished


    def _immediateRun_while(self):
        finished = False
        while not finished:
            _,_,_,_,finished = asyncio.get_event_loop().run_until_complete(self._next_finished())
    def _immediateRun(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._immediateRun_while())
    def immediateRun(self):
        thread = threading.Thread(target=self._immediateRun)
        thread.start()
        self.monitor(thread)

    def _run_while(self):
        finished = False
        while not finished:
            _,_,_,_,finished = asyncio.get_event_loop().run_until_complete(self._next_finished())
            time.sleep(1)
    def _run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._run_while())
    def run(self):
        thread = threading.Thread(target=self._run)
        thread.start()
        self.monitor(thread)
        
    
    def monitor(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.monitor(thread))
        else:
            msgbox.showinfo(f"Run {self.n_runs-1}", f"Run {self.n_runs-1} finished!\nContinute to re-compute LMDP...")
            self.recomputelmdp()


    async def _recomputelmdp(self):
        await self.aida.recompute_lmdp()
    def recomputelmdp(self):
        asyncio.get_event_loop().run_until_complete(self._recomputelmdp())


    def kill(self):
        print("Stopping...")
        os.killpg(os.getpgid(self.p1.pid), signal.SIGTERM)
        self.startButton.config(state= "normal")
        self.nextButton.config(state= "disabled")
        self.killButton.config(state= "disabled")
        self.immediateRunButton.config(state= "disabled")
        self.runButton.config(state= "disabled")
        self.disruptionButton.config(state= "disabled")


    def refreshComboBox(self): #very ugly way to update items in the listbox
        data = list(self.service_map.keys())
        self.comboBox['values'] = data
        self.comboBox.current(0)
        
        
    async def _breakHandler(self, service_label):
        await self.aida.break_service(service_label)       
    def breakHandler(self):
        with open(self.config_file) as json_file:
            data = json.load(json_file)
        break_type = data["breaking_type"]
        service_label = self.comboBox.get() #return the selected value
        print(service_label)
        asyncio.get_event_loop().run_until_complete(self._breakHandler(service_label))


    def set_image_services(self):
        with open(self.config_file) as json_file:
            data = json.load(json_file)
    
        services = data['services']
        self.image_path = f"utils/{data['image_path']}"
        self.folder = data['folder']
        
        self.matrix = [data['matrix'][key] for key in ['rows', 'columns']]

        service_map = {}
        
        for service in services:
            nome_file = service['name_file']
            x = service['x']
            y = service['y']
            label = service['label']

            service_map[label] = (x,y,nome_file)

        self.service_map = service_map
        
        data = self.service_map.keys()

        self.background_image = ImageTk.PhotoImage(Image.open(self.image_path).resize((1200,900)))
        self.background_canvas.itemconfig(self.image_on_canvas, image = self.background_image)
        
        self.step_x = 1200 // self.matrix[1]
        self.step_y = 900 // self.matrix[0]
        
        for service_label in data:
            x = self.service_map[service_label][0]
            y = self.service_map[service_label][1]
            x1 = x * self.step_x
            if x1 == 0: x1 +=1
            y1 = y * self.step_y
            if y1 == 0: y1 +=1
            rectangle = self.background_canvas.create_rectangle(x1, y1, x1+self.step_x, y1+self.step_y, fill="green", stipple="gray50", outline="black")
            text_service_label = service_label
            if "_" in text_service_label:
                tokens = text_service_label.split("_")
                text_service_label = ""
                for elem in tokens:
                    text_service_label+=f"\n{elem}"
            self.background_canvas.create_text(x1+self.step_x/2, y1+self.step_y/2, text=text_service_label, font=SERVICE_FONT)
            self.service_map_rectangle[service_label] = rectangle
            self.service_map_action[service_label] = [0, []]


    def reset_on_start(self):
        for service_label in self.service_map_rectangle.keys():
            self.background_canvas.itemconfig(self.service_map_rectangle[service_label], fill="green", stipple="gray50", outline="black")
            self.service_map_action[service_label] = [0, []]
        self.star_images = []
        self.n_runs = 1
        self.n_prob_mod = 1
        self.initialRun = True
        self.planListBox.config(state="normal")
        self.planListBox.delete(1.0, END)
        self.planListBox.config(state="disabled")


    def change_rect_color(self, service, state):
        match state:
            case "configured":
                self.background_canvas.itemconfig(self.service_map_rectangle[service], fill="gray", stipple="gray50", outline="black")
            case "broken":
                self.background_canvas.itemconfig(self.service_map_rectangle[service], fill="red", stipple="gray50", outline="black")
            case "executing":
                self.background_canvas.itemconfig(self.service_map_rectangle[service], fill="blue", stipple="gray50", outline="black")
            case "repairing":
                self.background_canvas.itemconfig(self.service_map_rectangle[service], fill="yellow", stipple="gray50", outline="black")
            case "ready":
                self.background_canvas.itemconfig(self.service_map_rectangle[service], fill="green", stipple="gray50", outline="black")


    def update_star(self, service_label):
        x_width = 30
        n_action = self.service_map_action[service_label][0]
        star_elem = self.service_map_action[service_label][1]
        x = self.service_map[service_label][0] * self.step_x
        y = self.service_map[service_label][1] * self.step_y
        if n_action > len(star_elem):
            posX = x+(x_width*(n_action-1))
            posY = y+2
            if posX + x_width > x + self.step_x:
                posX = x+((x_width*(n_action))%(self.step_x//x_width))
                posY = y+x_width
            print(posX, posY)
            self.star_images.append(ImageTk.PhotoImage(Image.open("utils/star.png").resize((x_width, x_width))))
            star_elem = self.background_canvas.create_image(posX, posY, anchor=tk.NW, image=self.star_images[len(self.star_images)-1])
            self.service_map_action[service_label][1].append(star_elem)
      

    def resetPage(self):
        self.config_file = ''
        self.service_map = {}
        self.service_map_rectangle = {}
        self.initialRun = True
        self.n_runs = 1
        self.n_prob_mod = 1
        
        try:
            self.kill()
        except:
            print("services not killed or already killed")

        self.planListBox.config(state="normal")
        self.planListBox.delete(1.0, END)
        self.planListBox.config(state="disabled")


    def goHome(self):
        self.controller.get_PreRunTimePage().resetPage()
        self.resetPage()
        self.controller.show_mainPage()