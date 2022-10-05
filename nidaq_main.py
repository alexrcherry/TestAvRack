import nidaqmx as ni
import numpy as np
from utils import log, ai_comm, mod_setup
#from utils.ai_comm import pressure_output
from utils.mod_setup import do_tasks_init
import logging
import threading
import time
from queue import Queue
import datetime
import tkinter as tk
from tkinter import Button, Label, Canvas, Entry

from utils.do_comm import open_nc_valve, open_no_valve, close_nc_valve, close_no_valve, chann_disable, chann_enable, ignite

# start pressure, solenoid, and igniter loggers
press_data_log = log.init_logger('pressure_logs', 'logs/pt_log.csv')
valve_log = log.init_logger('valve_logs', 'logs/valve_log.csv')
ign_state_log = log.init_logger('ign_logs', 'logs/ign_log.csv')

# init pressure, solenoid, and igniter csv files -->will log all info
timestr = time.strftime("%Y%m%d")
press_headers = ['timestamp', 'helium pressure[psi]', 'helium supply pressure[psi]', 'pneumatics pressure[psi]', 'pneumatics supply pressure[psi]']
press_data_csv_fp = 'logs/pt_data_'+timestr+'.csv'
press_data_csv = log.init_csv_write(press_headers, press_data_csv_fp)

valve_csv_fp = 'logs/valve_data_'+timestr+'.csv'
valve_headers = ['timestamp', 'valve name', 'state']
valve_csv = log.init_csv_write(valve_headers, valve_csv_fp)

ign_state_csv_fp = 'logs/ign_data_'+timestr+'.csv'
ign_headers = ['timestamp', 'continuity[bool]', 'current']
ign_state_csv = log.init_csv_write(ign_headers, ign_state_csv_fp)

# initialize nidaqmx local system
sys = mod_setup.sys_init()

# create analog voltage input queue
ai_queue = Queue()
# create empty analog voltage array to be filled
ai_output = np.zeros([6, 100], dtype=np.float64)
# create empty list for valve states
valve_state = [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]
# initialize and start analog input task, for all four PT channels in pneumatics box
[ai_reader, ai_read_task] = mod_setup.ai_task_init(sys)

# create continuity reading queue
cont_queue = Queue()

# create list of valve state queues
do_queue_list = [Queue() for i in range(9)]
# initialize digital output tasks, for the 8 solenoids necessary for the LE Relaunch config
do_task_list = mod_setup.do_tasks_init(sys)

# set run mode = true
run = True

# create analog input thread
ai_thread = threading.Thread(target=ai_comm.ai_read, args=(lambda: run, ai_queue, ai_reader, ai_output, ai_read_task, press_data_log, press_data_csv_fp, cont_queue, ign_state_log, ign_state_csv_fp))
ai_thread.daemon = True
logging.info("Starting Analog Input thread")
ai_thread.start()

sys = ni.system.System.local()
task_list = do_tasks_init(sys)


def S1O():
    open_nc_valve(task_list[0])
    valve_state[0] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S1C():
    close_nc_valve(task_list[0])
    valve_state[0] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S2O():
    open_nc_valve(task_list[1])
    valve_state[1] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S2C():
    close_nc_valve(task_list[1])
    valve_state[1] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S3O():
    open_nc_valve(task_list[2])
    valve_state[2] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S3C():
    close_nc_valve(task_list[2])
    valve_state[2] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S4O():
    open_nc_valve(task_list[3])
    valve_state[3] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S4C():
    close_nc_valve(task_list[3])
    valve_state[3] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S5O():
    open_no_valve(task_list[4])
    valve_state[4] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S5C():
    close_no_valve(task_list[4])
    valve_state[4] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S6O():
    open_no_valve(task_list[5])
    valve_state[5] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S6C():
    close_no_valve(task_list[5])
    valve_state[5] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S7O():
    open_nc_valve(task_list[6])
    valve_state[6] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S7C():
    close_nc_valve(task_list[6])
    valve_state[6] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S8O():
    open_nc_valve(task_list[7])
    valve_state[7] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S8C():
    close_nc_valve(task_list[7])
    valve_state[7] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S9O():
    chann_disable(task_list[6])  # disable he prime valve
    chann_disable(task_list[7])  # disable he fill valve


def S9C():
    chann_enable(task_list[6])  # enable he prime valve
    chann_enable(task_list[7])  # enable he fill valve


def S10O():
    chann_disable(task_list[8])  # disable igniter circuit


def S10C():
    chann_enable(task_list[8])  # enable igniter circuit


def S11O():
    chann_disable(task_list[2])  # disable mpva valves
    chann_disable(task_list[2])  # disable mpva valves
    chann_disable(task_list[8])  # disable igniter


def S11C():
    chann_enable(task_list[2])  # enable mpva valves
    chann_enable(task_list[2])  # enable mpva valves
    chann_enable(task_list[8])  # enable igniter


def S12O():
    ignite(task_list[8])  # find out what delay should go after this
    open_nc_valve(task_list[3])
    time.sleep(0.25)
    open_nc_valve(task_list[2])
    valve_state[3] = 1
    valve_state[2] = 1
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def S13O():
    def cycle():  # need to use multiprocessing library instead so that process can be killed from outside
        while True:
            dur_off = int(duration_off.get())
            dur_on = int(duration_on.get())
            open_no_valve(task_list[4])
            valve_state[4] = 1
            log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)
            time.sleep(duration_on)
            close_no_valve(task_list[4])
            valve_state[4] = 0
            log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)
            time.sleep(duration_off)
    # create analog input thread
    cycle_process = Process(target=cycle)
    cycle_process.daemon = True
    cycle_process.start()



def S13C():
    cycle_thread.join()




def S14O():
    open_nc_valve(task_list[0])
    open_nc_valve(task_list[1])
    close_nc_valve(task_list[2])
    close_nc_valve(task_list[3])
    open_no_valve(task_list[4])
    open_no_valve(task_list[5])
    close_nc_valve(task_list[6])
    close_nc_valve(task_list[7])
    valve_state[0] = 1
    valve_state[1] = 1
    valve_state[2] = 0
    valve_state[3] = 0
    valve_state[4] = 1
    valve_state[5] = 1
    valve_state[6] = 0
    valve_state[7] = 0
    log.csv_write([time.strftime("%Y%m%d")]+valve_state, valve_csv)


def update_vals():
    #print(type(ai_comm.pressure_output))
    #print(type(ai_comm.pressure_output[0]))
    val0 = 'HE: ' + str(round(sum(ai_comm.pressure_output[0])/len(ai_comm.pressure_output[0]), 1)) + 'psi'
    val1 = 'HE Supply: ' + str(round(sum(ai_comm.pressure_output[1])/len(ai_comm.pressure_output[1]), 1)) + 'psi'
    val2 = 'Pneumatics: ' + str(round(sum(ai_comm.pressure_output[2])/len(ai_comm.pressure_output[2]), 1)) + 'psi'
    val3 = 'Pneumatics Supply: ' + str(round(sum(ai_comm.pressure_output[3])/len(ai_comm.pressure_output[3]), 1)) + 'psi'
    val4 = round(sum(ai_comm.pressure_output[4])/len(ai_comm.pressure_output[4]), 1)
    val5 = 'lox' + str(round(sum(ai_comm.pressure_output[5])/len(ai_comm.pressure_output[5]), 1))
    if val4 > 0:
        val4 = 'Continuity'
    else:
        val4 = 'No Continuity'
    time_val = datetime.datetime.now().strftime("Time: %H:%M:%S")
    label0.config(text=val0)
    label1.config(text=val1)
    label2.config(text=val2)
    label3.config(text=val3)
    label4.config(text=val4)
    label5.config(text=val5)
    time_lab.config(text=time_val)

    if valve_state[0] == 1:
        create_circle(95, 78, 4, myCanvas, fill='green')
    else:
        create_circle(95, 78, 4, myCanvas, fill='red')

    if valve_state[1] == 1:
        create_circle(295, 78, 4, myCanvas, fill='green')
    else:
        create_circle(295, 78, 4, myCanvas, fill='red')

    if valve_state[2] == 1:
        create_circle(495, 78, 4, myCanvas, fill='green')
    else:
        create_circle(495, 78, 4, myCanvas, fill='red')

    if valve_state[3] == 1:
        create_circle(695,78,4,myCanvas,fill = 'green')
    else:
        create_circle(695,78,4,myCanvas,fill = 'red')

    if valve_state[4] == 1:
        create_circle(95,258,4,myCanvas,fill = 'green')
    else:
        create_circle(95,258,4,myCanvas,fill = 'red')

    if valve_state[5] == 1:
        create_circle(295,258,4,myCanvas,fill = 'green')
    else:
        create_circle(295,258,4,myCanvas,fill = 'red')

    if valve_state[6] == 1:
        create_circle(495,258,4,myCanvas,fill = 'green')
    else:
        create_circle(495,258,4,myCanvas,fill = 'red')

    if valve_state[7] == 1:
        create_circle(695,258,4,myCanvas,fill = 'green')
    else:
        create_circle(695,258,4,myCanvas,fill = 'red')



    tk.after(100, update_vals)


tk = tk.Tk()
tk.geometry("1920x1080")
tk.title('Control Panel')
#indicators
myCanvas = Canvas(tk, height = 600, width = 1000)
myCanvas.place(x=0,y=0)
def create_circle(x,y,r,canvas, **kwargs):
	return canvas.create_oval(x-r,y-r,x+r, y+r, **kwargs)
#text for pres data
time_lab = Label(tk)
time_lab.place(x=10,y=10)

label0 = Label(tk)
label0.place(x=1000,y=70)

label1 = Label(tk)
label1.place(x=1200,y=70)

label2 = Label(tk)
label2.place(x=1400,y=70)

label3 = Label(tk)
label3.place(x=1600,y=70)

label4 = Label(tk)
label4.place(x=1000,y=140)

label5 = Label(tk)
label5.place(x=1000,y=240)
update_vals()




# first row
text = Label(tk, text="LRM")
text.place(x=100,y=70)
b1 = Button(tk, text="Open",width=20,height=3, command=S1O).place(x=100, y=100)
b2 = Button(tk, text="Closed",width=20,height=3,command=S1C).place(x=100, y=170)

text = Label(tk, text="HRM")
text.place(x=300,y=70)
b3 = Button(tk, text="Open",width=20,height=3, command=S2O).place(x=300, y=100)
b4 = Button(tk, text="Closed",width=20,height=3, command=S2C).place(x=300, y=170)

text = Label(tk, text="OX MPVA")
text.place(x=500,y=70)
b5 = Button(tk, text="Open",width=20,height=3, command=S3O).place(x=500, y=100)
b6 = Button(tk, text="Closed",width=20,height=3, command=S3C).place(x=500, y=170)

text = Label(tk, text="CH4 MPVA")
text.place(x=700,y=70)
b7 = Button(tk, text="Open",width=20,height=3,command=S4O).place(x=700, y=100)
b8 = Button(tk, text="Closed", width=20,height=3,command=S4C).place(x=700, y=170)

#second row
text = Label(tk, text="OB PNU")
text.place(x=100,y=250)
b10 = Button(tk, text="Open", width=20,height=3,command=S5C).place(x=100, y=280)
b9 = Button(tk, text="Closed",width=20,height=3, command=S5O).place(x=100, y=350)

text = Label(tk, text="HE VENT")
text.place(x=300,y=250)
b11 = Button(tk, text="Open",width=20,height=3, command=S6C).place(x=300, y=280)
b12 = Button(tk, text="Closed",width=20,height=3, command=S6O).place(x=300, y=350)

text = Label(tk, text="HE PRIME")
text.place(x=500,y=250)
b13 = Button(tk, text="Open",width=20,height=3, command=S7O).place(x=500, y=280)
b14 = Button(tk, text="Closed", width=20,height=3,command=S7C).place(x=500, y=350)

text = Label(tk, text="HE FILL")
text.place(x=700,y=250)
b15 = Button(tk, text="Open", width=20,height=3,command=S8O).place(x=700, y=280)
b16 = Button(tk, text="Closed", width=20,height=3,command=S8C).place(x=700, y=350)
#third row
text = Label(tk, text="PRESS SAFETY")
text.place(x=100,y=430)
b17 = Button(tk, text="On", width=20,height=3, command=S9O).place(x=100, y=460)
b18 = Button(tk, text="Off", width=20,height=3,command=S9C).place(x=100, y=530)

text = Label(tk, text="LAUNCH SAFETY")
text.place(x=300,y=430)
b19 = Button(tk, text="On",width=20,height=3, command=S10O).place(x=300, y=460)
b20 = Button(tk, text="Off",width=20,height=3,command=S10C).place(x=300, y=530)

text = Label(tk, text="IGNITER SAFETY")
text.place(x=500,y=430)
b21 = Button(tk, text="On",width=20,height=3, command=S11O).place(x=500, y=460)
b22 = Button(tk, text="Off", width=20,height=3,command=S11C).place(x=500, y=530)


b23 = Button(tk, text="Launch", font='Helvetica 18 bold',width=60,height=9, bg="green", command=S12O).place(x=100, y=630)


b24 = Button(tk, text="Vent Cycle On", width=20, height=3, bg="yellow", command=S13O).place(x=700, y=460)
b25 = Button(tk, text="Vent Cycle Off", width=20, height=3, bg="yellow", command=S13C).place(x=700, y=530)
duration_label1 = Label(tk, text='Duration On (S):').place(x=900, y=460)
duration_label2 = Label(tk, text='Duration Off (S):').place(x=900, y=530)
duration_on = Entry(tk).place(x=1000, y=460)
duration_off = Entry(tk).place(x=1000, y=530)


b26 = Button(tk, text="Abort", font='Helvetica 18 bold', width=60, height=9, bg="red", command=S14O).place(x=850, y=630)
tk.mainloop()
