# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 20:23:14 2021

@author: charl
"""

import tkinter as tk
import tkinter.ttk as ttk
import sys, csv, pyperclip
import numpy as np
import pylab as pl
from os import listdir, stat, startfile
from os.path import isfile, join


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import optimize as sc

root = tk.Tk() 


# compile  a list of all .txt and .csv files in the Data folder
def read_data_file():
    global Data_files
    Data_files = []
    for file in listdir('Data'):
        if isfile(join('Data', file)) and file[-4:]=='.csv' or isfile(join('Data', file)) and file[-4:]=='.txt':
            Data_files.append(file)
        
read_data_file()



def write_factory():# resets the save file to default settings
    config_file = open(join('Config','config.txt'),'w')
    config_file.write("40\n32\n100\nNone\nFalse")
    config_file.close()

class default:#when done add saving ability
    # stores the adc unit as a si conversion and the symbol
    ADC_unit = [10e-15, 'FC']
    ADC_calibration = 40
    ELEC_gain = 32
    max_peaks = 15
    Stdev = 100
    auto_zoom = False
    
class factory:#when done add saving ability
    # stores the adc unit as a si conversion and the symbol
    ADC_unit = [10e-15, 'FC']
    ADC_calibration = 40
    ELEC_gain = 32
    max_peaks = 15
    Stdev = 100
    auto_zoom = False
    

class file_info:# the info about the laoded file is stored here
    size = 0
    name = ''
    rows = 0
    previous_load = None

class widgets: # differnt lists of widgets to be anbled/dsiabled
    enable_on_load = []
    disable_on_load = []
    disable_on_mafs = []

class Data:#stores useful chunks of data
    peak_coords = []
    current_coords = []
    disable = False
    created_imgs = []
    already_loaded = False
    fit_paras = []
    fit_errors = [] # centers is second




def load_defaults():
    try: #trys to open save file, if it cant creates a new one and writes the default data to it
        config_file = open(join('Config','config.txt'),'r')
    
    
    except:
        tk.messagebox.showerror("Error", "No save file, creating one")
        write_factory()
        
        config_file = open(join('Config','config.txt'),'r')
    
    
    reader = config_file.readlines()#loads data from the save file
    default.ADC_calibration = int(reader[0])
    default.ELEC_gain = int(reader[1])
    default.Stdev = int(reader[2])
    file_info.previous_load = str(reader[3])
    default.auto_zoom = bool(reader[4])
    
    
    config_file.close()

        
    
    
def Load_File(load_last = False): # this function loads the selected file
    Remove_Coords(clear= True)



    
    global array, canvas, info

   


    if load_last == True:#if load last is selcted this repalces the apth and name with the saved ones
        
        

        config_file = open(join('Config','config.txt'),'r')
        reader = config_file.readlines()#loads data from the save file
        name = str(reader[3])
        config_file.close()
        if name == 'None':
            tk.messagebox.showerror("Error", "No last file saved")
            return



    else:
        name = option_menu_title.get()
    file_type = (name)[-4:]#get file type 
        
        

    
    
    
    
    
    
    if file_type == '.csv':
        
        path = join('Data',name)
        root.title(('PPP: {0}').format(name))
        file = open(path)
        csv_reader = csv.reader(file)
                    #determine the number of rows in the csv
        row_count = sum(1 for row in csv_reader)  # fileObject is your csv.reader


        array = np.zeros((row_count,2))

        #make empty array    
        file = open(path)#for some reason i need to repeate this bit otherwise it wont work WHO KNOWS
        reader = csv.reader(file)
        
        for index,row in enumerate(reader): #populate array
            array[index,0] = float(row[0])
            array[index,1] = float(row[1])
     

    elif file_type == '.txt':#method for reading atxt file
        
        path = join('Data',name)
        text_file = open(path,'r')
        reader = text_file.readlines()
        
        
        row_count = (len(reader))
        array = np.zeros((row_count,2))
    
    
        for index,line in enumerate(reader):

            x,y = float(line[:(line.find('\t'))]),float(line[(line.find('\t')):])
            array[index,0] = float(x)
            array[index,1] = float(y)
            
            
            
    if load_last == False:#if load last is file saves it to the file
        config_file = open(join('Config','config.txt'),'r')
        reader = config_file.readlines()#loads data from the save file
        adc_entry = int(reader[0])#reads the first 3 lines
        elec_entry = int(reader[1])
        stdev_entry = int(reader[2])
        file_info.previous_load = str(reader[3])
        auto_zoom = bool(reader[4])
        config_file.close()
        config_file = open(join('Config','config.txt'),'w')
        
        last=str(name)#
        
        config_file.write(("{0}\n{1}\n{2}\n{3}\n{4}").format(adc_entry,elec_entry,stdev_entry,last,auto_zoom))# writes to the file with the enw last load
        config_file.close()
    
    
    
    for widget in widgets.disable_on_load:#enable and disable required widgets
        widget.config(state="disabled")        
    for widget in widgets.enable_on_load:
        widget.config(state="normal")     
        
    size = stat(path).st_size

    file_info.size = size
    file_info.rows = row_count
 
    file_info.name = name
    if len(name) > 20:
        name = name[:20] + '...'
    info.set(('File:\nName: {0}\nSize (bytes): {1}\n# Data points: {2}').format(name,size,row_count))
 

    #sets the file info box to correct stuff




    
    fig = pl.Figure(figsize = (16, 9))
    plot1 = fig.add_subplot(111)
    
    x_min,x_max = True, True
    if default.auto_zoom == True:
        for index in range(1, file_info.rows):
            x = int(array[index,0])
            y = int(array[index,1])
            if y != 0.0 and x_min == True:
                x_min = x - 50
                

            index = file_info.rows - index
            x = int(array[index,0])
            y = int(array[index,1])
            
            if y != 0.0 and x_max == True:
                x_max = x + 50
                

        plot1.set_xlim(x_min,x_max)
    plot1.plot(array[:,0],array[:,1])
    global toolbar
    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw()
    
    if Data.already_loaded == True:

        toolbar.destroy()
        toolbar = NavigationToolbar2Tk(canvas,root) 
        toolbar.update() 
    elif Data.already_loaded == False:
        toolbar = NavigationToolbar2Tk(canvas,root) 
        toolbar.update() 
    
    canvas.get_tk_widget().place(x=0,y=7) 



    over_view = pl.figure()
    pl.xlabel('ADC')
    pl.ylabel('Entries')
    pl.title('SiPM Output')
    pl.plot(array[:,0],array[:,1])

    pl.xlim(min(array[:,0]),max(array[:,0])/2)
    pl.rcParams['figure.figsize']  = 16,9
    pl.savefig('Saved/fig0.png')

    pl.close(over_view)


    

    def callback(event):
        x = int(event.xdata)
        y = int(event.ydata)
        most_recent_coords.set(('\nCurrent Coords:\n'+str(x)+', '+ str(y))+((default.max_peaks)*'\n'))
        Data.current_coords=(x,y)
    canvas.mpl_connect('button_press_event',callback)
    Data.already_loaded = True
 
def Update():
    global analysis_button
    string = ''
        
    for index,peak in enumerate(Data.peak_coords,start = 1):
        string = string + ('{0}: {1}, {2}\n').format(str(index),str(peak[0]),str(peak[1]))
        
    string = '\nSaved Coords:\n' + string
    saved_recent_coords.set(string)
    
    if len(Data.peak_coords) >= 3: #min length needed to do maths
        analysis_button.config(state="normal")
    else:
        analysis_button.config(state="disabled")       
        
def Add_Coords():
    global remove_button, add_button, clear_button
    if Data.current_coords  == []:
        tk.messagebox.showerror('Error','No coordinates selected')
        return
    if Data.disable == True:
        return
    if Data.current_coords != None and len(Data.peak_coords) < default.max_peaks:
        Data.peak_coords.append(Data.current_coords)
        if len(Data.peak_coords) >= 1:
            remove_button.config(state="normal")
            clear_button.config(state="normal")
        if len(Data.peak_coords) >= default.max_peaks:
            add_button.config(state="disabled")
    Update()
    
def Add_Coords2(event):
        Add_Coords()
        
def Remove_Coords(clear= False):
    global remove_button, add_button, clear_button, canvas
    if Data.disable == True:
        return
    if clear == True:
        Data.peak_coords = []
        remove_button.config(state="disabled")
        clear_button.config(state="disabled")
        add_button.config(state="normal")
    
    elif len(Data.peak_coords) > 0:
        Data.peak_coords = Data.peak_coords[:-1]    
        if len(Data.peak_coords) == 0:
            remove_button.config(state="disabled")
            clear_button.config(state="disabled")
        if len(Data.peak_coords) < default.max_peaks:
            add_button.config(state="normal")
    else:
        print('Remove button should\nhave been disabled')
    Update()
    
def Remove_Coords2(event):
    if len(Data.peak_coords) != 0:
        Remove_Coords()

def Mode_Switch():
    global Single_Peak_Mode_Only
    if Single_Peak_Mode_Only.get() == True:
        default.max_peaks = 3
    else:
        default.max_peaks = 15
        
    if not(len(Data.peak_coords) <= 3 and Single_Peak_Mode_Only.get() == True):
    
        Data.peak_coords = []
    Update()


def Big_Maths():# add a bit to read the settings
    global Progress_Bar, ADC, Electronic_Gain
    for widget in widgets.disable_on_mafs:#enable and disable required widgets
        widget.config(state="disabled")
    def Gaussian(x,height,center,stdev):
        return height*np.exp(-((x-center)**2)/(2*(stdev**2)))

    def Single_Fit(data, height, center, stdev):

        return(sc.curve_fit(Gaussian,data[:,0],data[:,1],p0=(height,center,stdev)))

    if Single_Peak_Mode_Only.get() == True:
            lower_bound = Data.peak_coords[0][0] 
            upper_bound = Data.peak_coords[2][0]
            difference = upper_bound - lower_bound
            data = np.zeros((0,2))
            if upper_bound <= lower_bound:
                print('lower bound is larger than the upper bound')
            for index in range(0,Data.lines):
                if array[index,0] >= lower_bound and array[index,0] <= upper_bound:
                    x = array[index,0]
                    y = array[index,1]
                    data = np.r_[data,[[x,y]]]
            
            fit_para = Single_Fit(data,Data.peak_coords[1][1],Data.peak_coords[1][0],default.Stdev)
            print(('height: {0} \ncenter: {1} \nstdev: {2}').format(*fit_para))
                                                                
            
            
            x_data = []
            y_data = []    
            for peak in Data.peak_coords:
                x_data.append(peak[0])
                y_data.append(peak[1])
               
            over_view = pl.figure()
            pl.title('Selected points')
            pl.plot(array[:,0],array[:,1])
            pl.plot(x_data,y_data,'+')
            pl.xlim(lower_bound-difference,upper_bound+difference)
            pl.ylim(0,(Data.peak_coords[1][1]*1.5))
            pl.rcParams['figure.figsize']  = 16,9
            pl.savefig('Saved/fig1.png')
            pl.xlabel('ADC')
            pl.ylabel('Entries')
            pl.show()
            pl.close(over_view)
            Data.created_imgs.append('Saved/fig1.png')
       
            x_data = np.linspace(lower_bound-difference,upper_bound+difference,1000)
        
            single_fit = pl.figure()
            pl.title('Single Fit')
            pl.plot(x_data,Gaussian(x_data,*fit_para))
            pl.plot(data[:,0],data[:,1],'+')
            pl.xlim(lower_bound-difference,upper_bound+difference)
            pl.ylim(0,(Data.peak_coords[1][1]*1.5))
            pl.rcParams['figure.figsize']  = 16,9
            pl.savefig('Saved/fig2.png')
            pl.xlabel('ADC')
            pl.ylabel('Entries')
            pl.show()
            pl.close(single_fit)    
            Data.created_imgs.append('Saved/fig2.png')
    if Single_Peak_Mode_Only.get() == False:
        def update_progress(peak,flat_amount = None):
            if flat_amount == None:
                amount = (peak+1)*(100/len(Data.peak_coords))
            else:
                amount = flat_amount
                
            Progress_Bar['value'] = amount
            root.update_idletasks() 
        
        
        centers = []
        heights = []
        for i in range(0,len(Data.peak_coords)):
            heights.append(Data.peak_coords[i][1])
            centers.append(Data.peak_coords[i][0])

        
        #findign average differnce
        differnces = []
        for i in range(0,len(centers)-1):
            differnces.append(abs(centers[i+1]-centers[i]))
        differnce = np.average(differnces)/2
        
        # now we cycle though each peak and make a single gaussian fit for each
        temp_error = []
        for peak in range(0,len(Data.peak_coords)):
            center = centers[peak]
            height = heights[peak]

            data = np.zeros((0,2))
            for index in range(0,file_info.rows):# can make more efficent later maybe
                x = array[index,0]
                y = array[index,1]

                if (x > center-differnce) and (x< center+differnce):
                    data = np.r_[data,[[x,y]]]
                else:
                    data = np.r_[data,[[x,0]]]
            fit_para,covp = Single_Fit(data,height,center,default.Stdev)
          #  print(covp)
            (Data.fit_paras).append(fit_para)
            temp_error.append(covp[1,1])
        
            update_progress(peak)
        Data.fit_errors.append(temp_error) #add sqrt if needecd
        multi_fit = pl.figure()
        pl.plot(array[:,0],array[:,1],'+')
        
        
        error = 0
        update_progress(None,flat_amount = 0)
        for i,para in enumerate(Data.fit_paras):
            update_progress(i)
            pl.plot(array[:,0],Gaussian(array[:,0],*para),color = 'red')
            error += int(para[2])
        
     #   print(file_info.rows, error)
        error = (error/np.sqrt(int(file_info.rows)))
    
        # this cant be right they're tiny
            
        pl.title('Multi Fit')

       # pl.xlim(min(array[:,0]),5000)#remove this line after you've got a good iamge

        pl.rcParams['figure.figsize']  = 16,9
        pl.savefig('Saved/fig3.png')
        pl.xlabel('ADC')
        pl.ylabel('Entries')
        pl.show()
        pl.close(multi_fit) 


        


        y_total = []
        update_progress(None,flat_amount = 0)
        for index,x in enumerate(array[:,0]):
            # add counter here
            temp = 0
            for para in Data.fit_paras:
                temp = temp + Gaussian(x,*para)
            y_total.append(temp)
        total_multi_fit = pl.figure()    
        pl.plot(array[:,0],array[:,1],'+')
        pl.plot(array[:,0],y_total,color='red')
        pl.rcParams['figure.figsize']  = 16,9
        pl.savefig('Saved/fig4.png')
        #pl.xlim(min(array[:,0]),5000)
        pl.xlabel('ADC')
        pl.ylabel('Entries')
        pl.show()
        pl.close(total_multi_fit) 

        x = []
        y = []
        for i in range(0,len(centers)):
            x.append(i)
            y.append(centers[i])
        peak_to_peak = pl.figure()
        pl.title('Peak to Peak seperation')
        pl.plot(x,y,'.')

        def stright_line(x,m,c):
            y = (m*x) + c
            return y  


        #coeff = np.polynomial.polynomial.polyfit(x,y,1)# 
        
        
        
        popt_sl, covp_sl = sc.curve_fit(stright_line,x,y,sigma =Data.fit_errors[0])#,p0=(height,center,stdev)))
        
        intercept, grad = popt_sl[1], popt_sl[0]
        print(covp_sl)
        
        sigma_grad = np.sqrt(covp_sl[0,0])
        
        print('sigma_m',sigma_grad)#still too small converting to sigma gain
        
        

    

        y2 = []
        for x_ in x:
            y = (grad*x_) + intercept
            y2.append(y)
            
        pl.plot(x,y2,label = 'Fit')
        pl.legend()
        pl.rcParams['figure.figsize']  = 16,9
        pl.savefig('Saved/fig5.png')
        pl.xlabel('# of photons')
        pl.ylabel('ADC')
        pl.show()
        pl.close(peak_to_peak) 
        
        # residual plot
        
        #error Syy
        x = []
        y = []
        for i in range(0,len(centers)):
            x.append(i)
            y.append(centers[i])


        
        
        #then  make a pop up
        def idiot_proof(text,string):
            try:
                number = int(text)
            except:
                print(text = 'Number not entered in {0}'.format(string), title = 'You Idiot')
            else:
                return number
            
            

        Adc_Calibration_Unit = 1e-15
        Adc_Calibration_Value = idiot_proof(ADC.get(),'adc calibration')
        gain_elec = idiot_proof(Electronic_Gain.get(),'electronic gain')
        
        charge = Adc_Calibration_Value*grad*Adc_Calibration_Unit

        gain_elec_factor = 10**(gain_elec/20)
        
        gain_intr = charge/(1.60217662e-19*gain_elec_factor)
        gain_intr = str(round(gain_intr,0))[:-2]
        
        

        sigma_gain = ((Adc_Calibration_Value*Adc_Calibration_Unit*sigma_grad)/(1.60217662e-19*gain_elec_factor))
        print(f"{sigma_gain} sigma gain")
        sigma_gain = round(sigma_gain,0)

        alert_message = 'Gain: {0} ± {1}'.format(gain_intr, sigma_gain) 
        
        tk.messagebox.showinfo("Results", alert_message)
        pyperclip.copy(('{0}\t{1}'.format(gain_intr, error)))
        
        



    
        Progress_Bar['value'] = 0
        for widget in widgets.disable_on_mafs:#enable and disable required widgets
            widget.config(state="normal")

        Data.fit_errors = []
        Data.fit_paras = []

text_size = 10
text_font ="Helvetica"

root.title('PPP')
root.state('zoomed')
def credit():
    tk.messagebox.showinfo("Credit", "Program written by Charles V Yelland as part of a final year project for the University of Sussex")
    
def setup_fit_frame():#setting up the fit frame
    text_size = 10
    text_font ="Helvetica"
    global most_recent_coords, saved_recent_coords, remove_button, clear_button, add_button
    button_height = 2
    button_width = 10
    
    fit_frame = ttk.LabelFrame(root, text="Fitting")
    fit_frame.place(rely = .05, relx = .7)
     
    clear_button = tk.Button(fit_frame,text = 'Clear',state = tk.DISABLED, command = lambda: Remove_Coords(clear=(True)))
    clear_button.config( height = button_height, width = button_width)
    clear_button.grid(column = 0,row = 0)
    #widgets.enable_on_load.append(clear_button)
    
    remove_button = tk.Button(fit_frame,text = 'Remove',command = Remove_Coords)
    remove_button.config( height = button_height, width = button_width,state = tk.DISABLED)
    remove_button.grid(column = 1,row = 0)
   # widgets.enable_on_load.append(remove_button)
    
    add_button = tk.Button(fit_frame,text = 'Add', command = Add_Coords)
    add_button.config( height = button_height, width = button_width,state = tk.DISABLED)
    add_button.grid(column = 2,row = 0)
    widgets.enable_on_load.append(add_button)
    
    most_recent_coords = tk.StringVar()
    most_recent_coords.set('\nCurrent Coords:'+16*'\n')
    
    
    most_recent_coords_l=tk.Label(fit_frame, textvariable = most_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
    most_recent_coords_l.grid(column = 0, row = 2,columnspan =2,sticky = 'nw')
    widgets.enable_on_load.append(most_recent_coords_l)
    
    saved_recent_coords = tk.StringVar()
    saved_recent_coords.set('\nSaved Coords:\n')
    
    
    saved_recent_coords_l=tk.Label(fit_frame, textvariable = saved_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
    saved_recent_coords_l.grid(column = 1, row = 2,columnspan =2,sticky = 'n')
    widgets.enable_on_load.append(saved_recent_coords_l)

def refresh():
    global option_menu_title, Data_files
    read_data_file()
    file_frame.destroy()
    setup_file_frame()
    
    
def setup_file_frame():#add settings frame
    text_size = 10
    text_font ="Helvetica"
    global option_menu_title, Data_files, file_frame 
    button_height = 2
    button_width = 10
    file_frame = ttk.LabelFrame(root, text="File")
    
    file_frame.place(rely = .7, relx = .1)
    
    

    
    
    option_menu_title = tk.StringVar()
    option_menu_title.set(Data_files[0])
    option_menu = tk.OptionMenu(file_frame,option_menu_title,*Data_files)
    option_menu.config( height = button_height, width = 60)
    option_menu.grid(column = 1, row = 0)
    
    #widgets.disable_on_load.append(option_menu)
    
    
    Load_Button = tk.Button(file_frame ,text='Load',font=(text_font, text_size))
    Load_Button.config( height = button_height, width = button_width,command = Load_File)
    Load_Button.grid(column = 2, row = 0)
    #widgets.disable_on_load.append(Load_Button)
    
    Refresh_Button = tk.Button(file_frame ,text='↺',font=(text_font, 16))
    Refresh_Button.config( height = 0, width = 3,command = refresh)
    Refresh_Button.grid(column = 0, row = 0)
    
    #add settings tab
def setup_maths_frame():
    global analysis_button, Single_Peak_Mode_Only, Progress_Bar, ADC, Electronic_Gain
    text_size = 10
    text_font ="Helvetica"
    button_height = 2
    button_width = 10
    
    analysis_frame = ttk.LabelFrame(root, text="Analysis")
    analysis_frame.place(rely = .05, relx = .85)
     
    analysis_button = tk.Button(analysis_frame,text = 'Analyse',command = Big_Maths,state = tk.DISABLED)
    analysis_button.config( height = button_height, width = button_width)
    analysis_button.grid(column = 0,row = 0,columnspan = 1)
    

    Electronic_Gain = tk.Entry(analysis_frame,width = 10)
    Electronic_Gain.grid(column = 1,row = 3)
    Electronic_Gain.insert(1,string = str(default.ELEC_gain))
    Electronic_Gain_l=tk.Label(analysis_frame, text = 'Electronic Gain:',font=(text_font, text_size))
    Electronic_Gain_l.grid(column = 0,row = 3)
    widgets.disable_on_mafs.append(Electronic_Gain)
    
    ADC = tk.Entry(analysis_frame,width = 10)
    ADC.grid(column = 1,row = 2)
    ADC.insert(1,string = str(default.ADC_calibration))
    ADC_l=tk.Label(analysis_frame, text = ('ADC [{0}]:').format(default.ADC_unit[1]),font=(text_font, text_size))
    ADC_l.grid(column = 0,row = 2)
    widgets.disable_on_mafs.append(ADC)

    Single_Peak_Mode_Only = tk.BooleanVar()
    Single_Peak_Mode_Only.set(False)
    Single_Peak_Mode_Only_CB = tk.Checkbutton(analysis_frame, text="Single Peak Only",command = Mode_Switch, variable = Single_Peak_Mode_Only,state = tk.DISABLED)
    Single_Peak_Mode_Only_CB.grid(column=1, row = 0,columnspan = 1)
    widgets.enable_on_load.append(Single_Peak_Mode_Only_CB)
    widgets.disable_on_mafs.append(Single_Peak_Mode_Only_CB)
    
    Progress_Bar = ttk.Progressbar(analysis_frame,length = 200, orient = tk.HORIZONTAL, mode = 'determinate')
    Progress_Bar.grid(row=1, column = 0, columnspan = 2,pady = 10)

def setup_info_frame():
    global info
    text_size = 10
    text_font ="Helvetica"
    info_frame = ttk.LabelFrame(root, text="Info")
    info_frame.place(rely = .2, relx = .85)
    
    
    
    info = tk.StringVar()
    info.set(('File:\nName: {0}\nSize (bytes): {1}\n# Data points: {2}').format('','',''))
    
    
    info_l=tk.Label(info_frame, textvariable = info,font=(text_font, text_size),state = tk.DISABLED)
    widgets.enable_on_load.append(info_l)
    info_l.grid(column = 0, row = 0)
    
    info_frame.grid_columnconfigure(0, minsize=215)

# call all the set up fucntions just to keep it neat tbh

def settings():

    def reset():
        write_factory()
        tk.messagebox.showinfo("Settings", "Settings reset")
        trunk.destroy()
        load_defaults()
    def save_settings(adc_entry,stdev_entry,elec_entry,auto_zoom_entry):
        def idiot_proof(entry):
            try:
                int(entry.get())
            except:
                return False
            else:
                return True
        
        for entry in (adc_entry,stdev_entry,elec_entry):
            if idiot_proof(entry) == False:
                tk.messagebox.showerror("Error", "Please only enter interger values")
        
        
        
        
        config_file = open(join('Config','config.txt'),'w')
        
        last=str(file_info.previous_load)
        
        
        
        config_file.write(("{0}\n{1}\n{2}\n{3}{4}").format(adc_entry.get(),elec_entry.get(),stdev_entry.get(),last,auto_zoom_entry))
        config_file.close()
        trunk.destroy()
        load_defaults()
        tk.messagebox.showinfo("Settings", "Settings saved")
        
        

    class text_label:
        def __init__(self,text,x,y,span = 2,sticky = '',padx = 0,pady= 0):
            text_size = 12
            text_font ="Helvetica"
            label = tk.Label(trunk,text = text,font=(text_font, text_size))
            label.grid(column = x, row = y, columnspan = span,sticky = sticky,padx = padx, pady = pady)

    text_size = 12
    text_font ="Helvetica"  
            
    button_height = 2
    button_width = 13
    
    trunk = tk.Toplevel()
    trunk.focus_force()
    text_label('Default Sigma',0,1)
    text_label('ADC',0,2,sticky = 'e')
    text_label('Electronic Gain',0,3)
    text_label('dB',3,3)
    text_label('n/a',3,1)
    text_label('fC',3,2)
    text_label('Value',2,0,pady = 3)
    text_label('Unit',3,0,padx = 10)
    
    trunk.title('Settings')
    trunk.resizable(False, False)
    
    
    Auto_Zoom = tk.BooleanVar()
    Auto_Zoom.set(default.auto_zoom)
    Auto_Zoom_CB = tk.Checkbutton(trunk, variable = Auto_Zoom,font=(text_font, text_size))
    Auto_Zoom_CB.grid(column=2, row = 4,columnspan = 1,pady = 5)
    text_label('Auto Zoom',0,4)
    
    
    Electronic_Gain = tk.Entry(trunk,width = 10,font=(text_font, text_size))
    Electronic_Gain.grid(column = 2,row = 3)
    Electronic_Gain.insert(1,string = str(default.ELEC_gain))

    ADC_Calibration = tk.Entry(trunk,width = 10,font=(text_font, text_size))
    ADC_Calibration.grid(column = 2,row = 2)
    ADC_Calibration.insert(1,string = str(default.ADC_calibration))
    


    Default_sigma = tk.Entry(trunk,width = 10,font=(text_font, text_size))
    Default_sigma.grid(column = 2,row = 1)
    Default_sigma.insert(1,string = str(default.Stdev))
    
    
    Save_B = tk.Button(trunk, text = 'Save',command = lambda: save_settings(ADC_Calibration,Default_sigma,Electronic_Gain,Auto_Zoom.get()),font=(text_font, text_size))
    
    Save_B.config( height = button_height, width = button_width)
    Save_B.grid(column = 0, row = 5, columnspan = 2)
    
    Reset_B = tk.Button(trunk, text = 'Reset',command = reset,font=(text_font, text_size))
    Reset_B.config( height = button_height, width = button_width)
    Reset_B.grid(column = 2, row = 5, columnspan = 2,pady = 15)


    prefixes_dict = {'n':10e-9,'p':10e-12,'f':10e-15,'a':10e-18}

    temp = []
    for prefix in ('n','p','f','a'):
        temp.append(('{0} [{1}]').format(prefix,prefixes_dict[prefix]))


    

    trunk.iconphoto(False, tk.PhotoImage(file='Config\settings_icon.png'))
    trunk.mainloop()
    
    
    
def show_help():# make this work
    print('fds')
 
    try:
        trunk.destory()
    except:
        print('ggg')
    else:
        trunk.destory()
    
    
def Exit():
    root.destroy()
    
    
    
    
    
    
setup_maths_frame()
setup_fit_frame()
setup_file_frame()
setup_info_frame()

root.bind('<space>', Add_Coords2) #binds useful keys to fucntions
root.bind('<BackSpace>', Remove_Coords2)



#add menu bar, to open settings and credit

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open Folder",command = lambda: startfile("Data"))



filemenu.add_command(label="Load Last",command = lambda: Load_File(load_last=True))

filemenu.add_separator()

filemenu.add_command(label="Settings",command = settings)
filemenu.add_command(label="Exit",command = Exit)
filemenu.add_separator()
filemenu.add_command(label="Credit",command = credit)
#filemenu.add_separator()




#filemenu.add_command(label="Help",command = show_help) #do later
menubar.add_cascade(label="File", menu=filemenu)



root.iconphoto(False, tk.PhotoImage(file='Config\icon.png'))


root.config(menu=menubar)
root.mainloop()