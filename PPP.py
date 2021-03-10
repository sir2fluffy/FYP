# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 20:23:14 2021

@author: charl
"""

import tkinter as tk
import tkinter.ttk as ttk
import sys, csv, clipboard
import numpy as np
import pylab as pl
from os import listdir, stat
from os.path import isfile, join


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import optimize as sc

root = tk.Tk() 


# compile  a list of all .txt and .csv files in the Data folder

Data_files = []
for file in listdir('Data'):
    if isfile(join('Data', file)) and file[-4:]=='.csv' or isfile(join('Data', file)) and file[-4:]=='.txt':
        Data_files.append(file)
        
        
class default:#when done add saving ability
    # stores the adc unit as a si conversion and the symbol
    ADC_unit = [10e-15, 'FC']
    ADC_calibration = 40
    ELEC_gain = 32
    max_peaks = 15
    Stdev = 100

class file_info:
    size = 0
    name = ''
    rows = 0

class widgets:
    enable_on_load = []
    disable_on_load = []

class Data:
    peak_coords = []
    current_coords = []
    disable = False
    created_imgs = []
    


def Load_File(): # this function loads the selected file

    
    global array, canvas, info

    for widget in widgets.disable_on_load:
        widget.config(state="disabled")        
    for widget in widgets.enable_on_load:
        widget.config(state="normal")        
        
    file_type = (option_menu_title.get())[-4:]
    
    if file_type == '.csv':
        name = option_menu_title.get()
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
     

    elif file_type == '.txt':
        name = option_menu_title.get()
        path = join('Data',name)
        text_file = open(path,'r')
        reader = text_file.readlines()
        
        
        row_count = (len(reader))
        array = np.zeros((row_count,2))
    
    
        for index,line in enumerate(reader):

            x,y = float(line[:(line.find('\t'))]),float(line[(line.find('\t')):])
            array[index,0] = float(x)
            array[index,1] = float(y)
        
    size = stat(path).st_size

    file_info.size = size
    file_info.rows = row_count
    file_info.name = name
    if len(name) > 20:
        name = name[:20] + '...'
    info.set(('File:\nName: {0}\nSize (bytes): {1}\n# Data points: {2}').format(name,size,row_count))
 




        
        
    fig = pl.Figure(figsize = (16, 9))
    plot1 = fig.add_subplot(111) 
    plot1.plot(array[:,0],array[:,1])

    canvas = FigureCanvasTkAgg(fig, master = root)   
    canvas.draw() 
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
        most_recent_coords.set(('\nCurrent Coords:\n'+str(x)+', '+ str(y)))
        Data.current_coords=(x,y)
    canvas.mpl_connect('button_press_event',callback)
 
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
    global Progress_Bar
    def Gaussian(x,height,center,stdev):
        return height*np.exp(-((x-center)**2)/(2*(stdev**2)))

    def Single_Fit(data, height, center, stdev):

        return(sc.curve_fit(Gaussian,data[:,0],data[:,1],p0=(height,center,stdev))[0])

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
        fit_paras = []
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
            fit_para = Single_Fit(data,height,center,default.Stdev)
            fit_paras.append(fit_para)
            update_progress(peak)
        multi_fit = pl.figure()
        pl.plot(array[:,0],array[:,1],'+')
        
        update_progress(None,flat_amount = 0)
        for i,para in enumerate(fit_paras):
            update_progress(i)
            pl.plot(array[:,0],Gaussian(array[:,0],*para),color = 'red')
            
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
            for para in fit_paras:
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
        
        coeff = np.polynomial.polynomial.polyfit(x,y,1)# 

        intercept, grad = int(coeff[0]), int(coeff[1])

        
        def stright_line(x,m,c):
            y = (m*x) + c
            return y
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
            
            
            
        # Adc_Calibration_Unit = 1e-15
        # Adc_Calibration_Value = idiot_proof(Adc_Calibration.get(),'adc calibration')
        # gain_elec = idiot_proof(Electronic_Gain.get(),'electronic gain')
        
        # charge = Adc_Calibration_Value*grad*Adc_Calibration_Unit
        # print(grad,': grad')
        # gain_elec_factor = 10**(gain_elec/20)
        
        # gain_intr = charge/(1.60217662e-19*gain_elec_factor)
        # gain_intr = str(round(gain_intr,0))[:-2]
        
        
        
        
        
        # alert_message = 'Gain: {0} ± {1}'.format(gain_intr, '3') 
        
        
        # User_Alert(text = alert_message,title='Results',clip_board=True)


    
        Progress_Bar['value'] = 0

       

text_size = 10
text_font ="Helvetica"

root.title('PPP')
root.state('zoomed')

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
    widgets.enable_on_load.append(clear_button)
    
    remove_button = tk.Button(fit_frame,text = 'Remove',command = Remove_Coords)
    remove_button.config( height = button_height, width = button_width,state = tk.DISABLED)
    remove_button.grid(column = 1,row = 0)
    widgets.enable_on_load.append(remove_button)
    
    add_button = tk.Button(fit_frame,text = 'Add', command = Add_Coords)
    add_button.config( height = button_height, width = button_width,state = tk.DISABLED)
    add_button.grid(column = 2,row = 0)
    widgets.enable_on_load.append(add_button)
    
    most_recent_coords = tk.StringVar()
    most_recent_coords.set('\nCurrent Coords:'+15*'\n')
    
    
    most_recent_coords_l=tk.Label(fit_frame, textvariable = most_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
    most_recent_coords_l.grid(column = 0, row = 2,columnspan =2,sticky = 'nw')
    widgets.enable_on_load.append(most_recent_coords_l)
    
    saved_recent_coords = tk.StringVar()
    saved_recent_coords.set('\nSaved Coords:\n')
    
    
    saved_recent_coords_l=tk.Label(fit_frame, textvariable = saved_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
    saved_recent_coords_l.grid(column = 1, row = 2,columnspan =2,sticky = 'n')
    widgets.enable_on_load.append(saved_recent_coords_l)
    
def setup_file_frame():#add settings frame
    text_size = 10
    text_font ="Helvetica"
    global option_menu_title
    button_height = 2
    button_width = 10
    file_frame = ttk.LabelFrame(root, text="File")
    
    file_frame.place(rely = .7, relx = .1)
    
    

    
    
    option_menu_title = tk.StringVar()
    option_menu_title.set(Data_files[0])
    option_menu = tk.OptionMenu(file_frame,option_menu_title,*Data_files)
    option_menu.config( height = button_height, width = 60)
    option_menu.grid(column = 0, row = 1)
    widgets.disable_on_load.append(option_menu)
    
    
    Load_Button = tk.Button(file_frame ,text='Load',font=(text_font, text_size))
    Load_Button.config( height = button_height, width = button_width,command = Load_File)
    Load_Button.grid(column = 1, row = 1)
    widgets.disable_on_load.append(Load_Button)
    
    #add settings tab
def setup_maths_frame():
    global analysis_button, Single_Peak_Mode_Only, Progress_Bar
    text_size = 10
    text_font ="Helvetica"
    button_height = 2
    button_width = 10
    
    analysis_frame = ttk.LabelFrame(root, text="Analysis")
    analysis_frame.place(rely = .05, relx = .85)
     
    analysis_button = tk.Button(analysis_frame,text = 'Analyse',command = Big_Maths)
    analysis_button.config( height = button_height, width = button_width)
    analysis_button.grid(column = 0,row = 0,columnspan = 1)
    

    Electronic_Gain = tk.Entry(analysis_frame,width = 10)
    Electronic_Gain.grid(column = 1,row = 3)
    Electronic_Gain.insert(1,string = str(default.ELEC_gain))
    Electronic_Gain_l=tk.Label(analysis_frame, text = 'Electronic Gain:',font=(text_font, text_size))
    Electronic_Gain_l.grid(column = 0,row = 3)

    ADC = tk.Entry(analysis_frame,width = 10)
    ADC.grid(column = 1,row = 2)
    ADC.insert(1,string = str(default.ADC_calibration))
    ADC_l=tk.Label(analysis_frame, text = ('ADC [{0}]:').format(default.ADC_unit[1]),font=(text_font, text_size))
    ADC_l.grid(column = 0,row = 2)

    Single_Peak_Mode_Only = tk.BooleanVar()
    Single_Peak_Mode_Only.set(False)
    Single_Peak_Mode_Only_CB = tk.Checkbutton(analysis_frame, text="Single Peak Only",command = Mode_Switch, variable = Single_Peak_Mode_Only,state = tk.DISABLED)
    Single_Peak_Mode_Only_CB.grid(column=1, row = 0,columnspan = 1)
    widgets.enable_on_load.append(Single_Peak_Mode_Only_CB)
    
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
setup_maths_frame()
setup_fit_frame()
setup_file_frame()
setup_info_frame()

root.bind('<space>', Add_Coords2) #binds useful keys to fucntions
root.bind('<BackSpace>', Remove_Coords2)



#add menu bar, to open settings and credit



root.mainloop()