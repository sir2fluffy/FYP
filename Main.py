# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
import sys, csv, clipboard
import numpy as np
import pylab as pl
from os import listdir
from os.path import isfile, join

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import optimize as sc

CSV_files = []
for file in listdir('Data'):
    if isfile(join('Data', file)) and file[-4:]=='.csv':
        CSV_files.append(file)
#ff
root = tk.Tk()

class ref:
    lastest_coords = None
    peak_coords = []
    max_peak_coords = 15
    array_length = None
    default_stdev = 100
    lines = 0
    relevent_imgs = []
    number_of_peaks = None
    images_list = []
    adc_gradient = None
    disable = False
def Load_CSV(disable_widgets, enable_widgets):
    
    global array, canvas
    for widget in disable_widgets:
        widget.config(state="disabled")        
    for widget in enable_widgets:
        widget.config(state="normal")        
    CSV_name = option_menu_title.get()
    CSV_path = join('Data',CSV_name)
    root.title(('PPP: {0}').format(CSV_name))
    file = open(CSV_path)
    csv_reader = csv.reader(file)
    lines = 0 #count lines in the chosen csv
    for row in csv_reader:
        lines += 1
    array = np.zeros((lines,2))
    ref.array_length = lines
    #make empty array    
    file = open(CSV_path)#for some reason i need to repeate this bit otherwise it wont work WHO KNOWS
    csv_reader = csv.reader(file)
    line = 0
    for row in csv_reader: #populate array
        array[line,0] = float(row[0])
        array[line,1] = float(row[1])
        line = line + 1

    ref.lines = line
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
        most_recent_coords.set(('Current Coords:\n'+str(x)+', '+ str(y)))
        ref.lastest_coords=(x,y)
    canvas.mpl_connect('button_press_event',callback)
    
def Update():
    global Analyse_Button
    string = ''
    index = 1    
    for peak in ref.peak_coords:
        string = string + ('{0}: {1}, {2}\n').format(str(index),str(peak[0]),str(peak[1]))
        index += 1        
    string = 'Saved Coords:\n' + string
    saved_recent_coords.set(string)
    
    if len(ref.peak_coords) >= 3: #min length needed to do maths
        Analyse_Button.config(state="normal")
    else:
        Analyse_Button.config(state="disabled")       
        
def Add_Coords():
    global Add_Button, Remove_Button, Clear_Button
    if ref.disable == True:
        return
    if ref.lastest_coords != None and len(ref.peak_coords) < ref.max_peak_coords:
        ref.peak_coords.append(ref.lastest_coords)
        if len(ref.peak_coords) >= 1:
            Remove_Button.config(state="normal")
            Clear_Button.config(state="normal")
        if len(ref.peak_coords) >= ref.max_peak_coords:
            Add_Button.config(state="disabled")
    Update()
    
def Add_Coords2(event):
        Add_Coords()
        
def Remove_Coords(clear= False):
    global Remove_Button, Add_Button, Clear_Button, canvas
    if ref.disable == True:
        return
    if clear == True:
        ref.peak_coords = []
        Remove_Button.config(state="disabled")
        Clear_Button.config(state="disabled")
        Add_Button.config(state="normal")
    
    elif len(ref.peak_coords) > 0:
        ref.peak_coords = ref.peak_coords[:-1]    
        if len(ref.peak_coords) == 0:
            Remove_Button.config(state="disabled")
            Clear_Button.config(state="disabled")
        if len(ref.peak_coords) < ref.max_peak_coords:
            Add_Button.config(state="normal")
    else:
        User_Alert('Remove button should\nhave been disabled')
    Update()
    
def Remove_Coords2(event):
    if len(ref.peak_coords) != 0:
        Remove_Coords()

def User_Alert(text='An Error Occured',title = 'Error',clip_board = False,button_text = 'Ok',destroy_win = True):

    if clip_board == True:
        clipboard.copy(text)
    
    err = tk.Tk()
    err.geometry("400x300")
    def Destroy(destroy_win):
        
        err.destroy()
        if destroy_win == True:
            root.destroy()
            sys.exit()
    err.focus_force()
    err.after(1, lambda: err.focus_force())
    err.title(title)
    err.resizable(False, False)
    err.protocol("WM_DELETE_WINDOW",lambda: Destroy(destroy_win))
    Exit_Button = tk.Button(err, text=button_text,command= lambda: Destroy(destroy_win),font= ("Helvetica", 15))
    Exit_Button.grid(column=0,row=1)
    tk.Label(err, text = text,font= ("Helvetica", 12)).grid(column=0,row=0,sticky = 'NEWS')
    err.mainloop()


def Mode_Switch():
    if Single_Peak_Mode_Only.get() == True:
        ref.max_peak_coords = 3
    else:
        ref.max_peak_coords = 15
        
    if not(len(ref.peak_coords) <= 3 and Single_Peak_Mode_Only.get() == True):
    
        ref.peak_coords = []
    Update()


def Big_Maths(disable_widgets, enable_widgets, P_bar):
    global array, canvas
    ref.disable = True

    ref.number_of_peaks = len(ref.peak_coords)

    for widget in disable_widgets:
        widget.config(state="disabled")
    def plot_n_save(data,name,x_title = '',y_title = '',title = '',save = True,display = False):
        pass
    
    def Gaussian(x,height,center,stdev):
        return height*np.exp(-((x-center)**2)/(2*(stdev**2)))
    
    def Single_Fit(data, height, center, stdev):

        temp = sc.curve_fit(Gaussian,data[:,0],data[:,1],p0=(height,center,stdev))[0]
        print(temp)
        return temp
    #doo maths 

    if Single_Peak_Mode_Only.get() == True:
        lower_bound = ref.peak_coords[0][0] 
        upper_bound = ref.peak_coords[2][0]
        difference = upper_bound - lower_bound
        data = np.zeros((0,2))
        if upper_bound <= lower_bound:
            User_Alert('lower bound is larger than the upper bound')
        for index in range(0,ref.lines):
            if array[index,0] >= lower_bound and array[index,0] <= upper_bound:
                x = array[index,0]
                y = array[index,1]
                data = np.r_[data,[[x,y]]]
        
        fit_para = Single_Fit(data,ref.peak_coords[1][1],ref.peak_coords[1][0],ref.default_stdev)
        print(('height: {0} \ncenter: {1} \nstdev: {2}').format(*fit_para))
                                                            
        
        
        x_data = []
        y_data = []    
        for peak in ref.peak_coords:
            x_data.append(peak[0])
            y_data.append(peak[1])
           
        over_view = pl.figure()
        pl.title('Selected points')
        pl.plot(array[:,0],array[:,1])
        pl.plot(x_data,y_data,'+')
        pl.xlim(lower_bound-difference,upper_bound+difference)
        pl.ylim(0,(ref.peak_coords[1][1]*1.5))
        pl.rcParams['figure.figsize']  = 16,9
        pl.savefig('Saved/fig1.png')
        pl.xlabel('ADC')
        pl.ylabel('Entries')
        pl.show()
        pl.close(over_view)
        
   
        x_data = np.linspace(lower_bound-difference,upper_bound+difference,1000)
    
        single_fit = pl.figure()
        pl.title('Single Fit')
        pl.plot(x_data,Gaussian(x_data,*fit_para))
        pl.plot(data[:,0],data[:,1],'+')
        pl.xlim(lower_bound-difference,upper_bound+difference)
        pl.ylim(0,(ref.peak_coords[1][1]*1.5))
        pl.rcParams['figure.figsize']  = 16,9
        pl.savefig('Saved/fig2.png')
        pl.xlabel('ADC')
        pl.ylabel('Entries')
        pl.show()
        pl.close(single_fit)    
       
    if Single_Peak_Mode_Only.get() == False:
        def update_progress(peak,flat_amount = None):
            if flat_amount == None:
                amount = (peak+1)*(100/len(ref.peak_coords))
            else:
                amount = flat_amount
                
            P_bar['value'] = amount
            root.update_idletasks() 
        
        
        centers = []
        heights = []
        for i in range(0,len(ref.peak_coords)):
            heights.append(ref.peak_coords[i][1])
            centers.append(ref.peak_coords[i][0])

        
        #findign average differnce
        differnces = []
        for i in range(0,len(centers)-1):
            differnces.append(abs(centers[i+1]-centers[i]))
        differnce = np.average(differnces)/2
        
        # now we cycle though each peak and make a single gaussian fit for each
        fit_paras = []
        for peak in range(0,len(ref.peak_coords)):
            center = centers[peak]
            height = heights[peak]

            data = np.zeros((0,2))
            for index in range(0,ref.lines):# can make more efficent later maybe
                x = array[index,0]
                y = array[index,1]

                if (x > center-differnce) and (x< center+differnce):
                    data = np.r_[data,[[x,y]]]
                else:
                    data = np.r_[data,[[x,0]]]
            fit_para = Single_Fit(data,height,center,ref.default_stdev)
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
        pl.xlim(min(array[:,0]),5000)
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
        temp = 0
        for i in range(0,ref.number_of_peaks):
            temp = temp + (y[i]-stright_line(x[i], grad, intercept))**2
        Syy = temp/ref.number_of_peaks

        #then  make a pop up
        def idiot_proof(text,string):
            try:
                number = int(text)
            except:
                User_Alert(text = 'Number not entered in {0}'.format(string), title = 'you idiot')
            else:
                return number
        Adc_Calibration_Value = idiot_proof(Adc_Calibration.get(),'adc calibration')
        Electronic_Gain_Value = idiot_proof(Electronic_Gain.get(),'electronic gain')
        true_gain = grad* Adc_Calibration_Value
        true_gain_Syy = Syy * Adc_Calibration_Value
        
        line1 = 'ADC Gain: {0} ± {1}'.format(grad,Syy)
        line2 = 'Gain w/o Electronic Gain: {0} ± {1}'.format(true_gain,true_gain_Syy)
        line3 = 'True Gain: {0} ± {1}'.format((true_gain*Electronic_Gain_Value),(true_gain_Syy*Electronic_Gain_Value))
        
        User_Alert((line1,line2,line3),destroy_win=(False),title = 'Results',clip_board = True)

    


    
        P_bar['value'] = 0
    if enable_widgets != None:
        for widget in enable_widgets:# repalce this with image broswer window # dont do that
            widget.config(state="normal")  



    
    #make single gaussian fit a function then call that many times for the other thing, set the lower and uppwer bounds to the cenrter +- the smear
text_size = 10
text_font ="Helvetica"

root.title('PPP')
root.state('zoomed')    



x = 1500
y = 900

option_menu_title = tk.StringVar()
option_menu_title.set(CSV_files[0])
option_menu = tk.OptionMenu(root,option_menu_title,*CSV_files)
option_menu.place(x=x,y=y,width = 250,height = 40)


Load_Button = tk.Button(root, state = tk.NORMAL,text='Load',command= lambda: Load_CSV((Load_Button,option_menu),
                (most_recent_coords_l,saved_recent_coords_l,Add_Button,Single_Peak_Mode_Only_CB))
                        ,font=(text_font, text_size))
Load_Button.place(x=x+250,y=y+2,height = 36,width=58)





x = 1300
y = 300



most_recent_coords = tk.StringVar()
most_recent_coords.set('Current Coords:\n')

most_recent_coords_l=tk.Label(root, textvariable = most_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
most_recent_coords_l.place(x=x,y=y)

saved_recent_coords = tk.StringVar()
saved_recent_coords.set('Saved Coords:\n')

saved_recent_coords_l=tk.Label(root, textvariable = saved_recent_coords,font=(text_font, text_size),state = tk.DISABLED)
saved_recent_coords_l.place(x=x+100,y=y)

Remove_Button = tk.Button(root,state = tk.DISABLED,text='Remove',command= lambda:Remove_Coords(),font=(text_font, text_size))
Remove_Button.place(x=x+60,y=y-50,height = 36,width=58)

Clear_Button = tk.Button(root,state = tk.DISABLED,text='Clear',command= lambda:Remove_Coords(clear = True),font=(text_font, text_size))
Clear_Button.place(x=x-10,y=y-50,height = 36,width=58)

Add_Button = tk.Button(root,state = tk.DISABLED,text='Add',command= lambda:Add_Coords(),font=(text_font, text_size))
Add_Button.place(x=x+130,y=y-50,height = 36,width=58)


x = 1700
y = 250
Analyse_Button = tk.Button(root,state = tk.DISABLED,text='Analyse',command= lambda:Big_Maths((most_recent_coords_l,Remove_Button,saved_recent_coords_l,Add_Button,Adc_Calibration,Analyse_Button,Clear_Button , Single_Peak_Mode_Only_CB),(None),(Progress_Bar)),font=(text_font, text_size))
Analyse_Button.place(x=x,y=y,height = 36,width=58)

Single_Peak_Mode_Only = tk.BooleanVar()
Single_Peak_Mode_Only.set(False)
Single_Peak_Mode_Only_CB = tk.Checkbutton(root, command = Mode_Switch, text="Single Peak Only", variable=Single_Peak_Mode_Only,state = tk.DISABLED)
Single_Peak_Mode_Only_CB.place(x=x,y=y+80)

Progress_Bar = ttk.Progressbar(root,length = 100, orient = tk.HORIZONTAL, mode = 'determinate')
Progress_Bar.place(x=x,y=y+50)

Adc_Calibration = tk.Entry(root,width = 10)
Adc_Calibration.place(x=x+45,y=y+120)
Adc_Calibration.insert(1,string = '40')
Adc_Calibration_l=tk.Label(root, text = 'ADC:',font=(text_font, text_size))
Adc_Calibration_l.place(x=x,y=y+120)

y = y + 50
Electronic_Gain = tk.Entry(root,width = 10)
Electronic_Gain.place(x=x+45,y=y+120)
Electronic_Gain.insert(1,string = '32')
Electronic_Gain_l=tk.Label(root, text = 'Electronic Gain:',font=(text_font, text_size))
Electronic_Gain_l.place(x=x-55,y=y+120)



root.bind('<space>', Add_Coords2)
#root.bind('<Enter>', Big_Maths2)
root.bind('<BackSpace>', Remove_Coords2)
root.mainloop()


