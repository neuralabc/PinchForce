#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of basic mouse handling from the ioHub (a separate asynchronous process for
fetching and processing events from hardware; mice, keyboards, eyetrackers).

Initial Version: May 6th, 2013, Sol Simpson
Abbrieviated: May 2013, Jon Peirce
Updated July, 2013, Sol, Added timeouts
"""

from __future__ import absolute_import, division, print_function

import sys
import time
#import serial
from psychopy.iohub import launchHubServer
from psychopy import visual, core
from psychopy.sound import Sound
import numpy as np
import os

# XXX For audio events, recommend PTB (in preferences dialog)
#audioLib = ['PTB','sounddevice', 'pyo', 'pygame', ]
# sound can be played to each ear independently, using something like this:
# from: https://groups.google.com/forum/m/#!topic/psychopy-dev/NoSVA7ycBjM
# as per here: https://www.psychopy.org/download.html#linux this is required in linux for low latency sound with PTB:
# sudo apt-get install libusb-1.0-0-dev portaudio19-dev libasound2-dev
#freq_factor = 2*np.pi*np.linspace(0,0.5,22050)
#freqL = 440
#freqR = 340
#soundL = np.sin(freq_factor*freqL)
#soundR = np.sin(freq_factor*freqR)
#s_out = Sound(np.array([soundL,soundR]).T)
#s_out.play()

# event_parser_info dict:
#
# parser_function key value can be a str giving the module.function path,
# or it can be the actual function object to be run by the iohub process.
#
# *Important:* The function provided should be in a file that can be imported
# as a module without causing unwanted behavior on the iohub process.
# Some options:
#     1) Put the function in a file that contains only the function,
#        as is done in this example.
#     2) Ensure any script logic that will be run when the file is called by
#        a user ( i.e. python.exe filewithfunc.py ) is inside a:
#            if __name__ == '__main__':
#        condition so it is not run when the file is only imported.
    
event_parser_info = dict(parser_function="parseserial.checkForSerialEvents",
                         parser_kwargs=dict(var1='not used', var2=1234))

# Settings for serial port (Sequential Pinch Force Task response device) communication.
SERIAL_PORT = '/dev/ttyACM0'
BAUDRATE = 115200
BYTESIZE = 8
STOPBITS = 'ONE'
PARITY = 'NONE'
# configure iohub
psychopy_mon_name = 'Monitor_01'
exp_code = 'SPFT_device'
sess_code = 'S_{0}'.format((time.mktime(time.localtime())))

# create the process that will run in the background polling devices

if os.path.exists(SERIAL_PORT):
    iohubkwargs = {'psychopy_monitor_name': psychopy_mon_name,
               'experiment_code': exp_code,
               'session_code': sess_code,
               'serial.Serial': dict(name='serial', port=SERIAL_PORT, baud=BAUDRATE,
                                     bytesize=BYTESIZE,parity=PARITY,
                                     event_parser=dict(delimiter='\r\n'))} #event_parser_info
    SPFT_present = True
else:
    print('SPFT_device not detected')
    iohubkwargs = {'psychopy_monitor_name': psychopy_mon_name, 'experiment_code': exp_code,'session_code': sess_code}
    SPFT_present = False

io = launchHubServer(**iohubkwargs)    
# some default devices have been created that can now be used
display = io.devices.display
keyboard = io.devices.keyboard
mouse = io.devices.mouse
if SPFT_present:
    SPFT_device = io.devices.serial




# We can use display to find info for the Window creation, like the resolution
# (which means PsychoPy won't warn you that the fullscreen does not match your requested size)
display_resolution = display.getPixelResolution()

# ioHub currently supports the use of a single full-screen PsychoPy Window
win = visual.Window(display_resolution,
                    units='pix', fullscr=False, allowGUI=False, screen=0, gammaErrorPolicy='warn')

# Create some psychopy visual stim (same as how you would do so normally):
fixSpot = visual.GratingStim(win, tex="none", mask="gauss",
    pos=(0, 0), size=(30, 30), color='black', autoLog=False)
grating = visual.GratingStim(win, pos=(300, 0),
    tex="sin", mask="gauss",
    color=[1.0, 0.5, -1.0],
    size=(500.0, 500.0), sf=(0.01, 0.0),
    autoLog=False)
    
# XXX chris starts here:
bar_start_height = 30
bar_start_pos_y = -500
bar_start_pos_x = 250
bar_width = 200

#bar = visual.ShapeStim(win,pos=(0,0),size=(40,120),lineWidth=3, lineColor=[1.0,0,1.0])
bar = visual.Rect(win,pos=(bar_start_pos_x ,bar_start_pos_y),width=bar_width, height=bar_start_height,lineWidth=0, fillColor="Yellow") #[0.0,1.0,0.0])
bar_ref = visual.Rect(win,pos=(-bar_start_pos_x ,bar_start_pos_y),width=bar_width, height=bar_start_height,lineWidth=0, fillColor="Purple") #[1.0,1.0,0.0])
#bar_ref = visual.Line(win,start=(bar_start_pos_y, 1000), end=(bar_start_pos_y+10, 1000),lineWidth=20)
message = visual.TextStim(win, pos=(0.0, -(display_resolution[1]/3)),
    alignHoriz='center', alignVert='center', height=40,
    text='move=mv-spot, left-drag=SF, right-drag=mv-grating, scroll=ori',
    autoLog=False, wrapWidth=display_resolution[0] * .9)
message2 = visual.TextStim(win, pos=(0.0, -(display_resolution[1]/4)),
    alignHoriz='center', alignVert='center', height=40,
    text='Press Any Key to Quit.',
    autoLog=False, wrapWidth=display_resolution[0] * .9)
bar_text = visual.TextStim(win, pos=(bar_start_pos_x+bar_width, 0.0),
    alignHoriz='center', alignVert='center', height=40,
    text='',color='Black',
    autoLog=False)
max_line = visual.ShapeStim(win,vertices=[[bar_start_pos_x-bar_width/2, bar_start_pos_y],[bar_start_pos_x+bar_width/2,bar_start_pos_y]],lineColor='Firebrick')

# we construct the reference bar counterclockwise from the bottom left  
# castint as np.array allows us to add matrices, which might be necessary in some cases?
vtx1 = np.array([-bar_start_pos_x-int(bar_width/2), bar_start_pos_y])
vtx2 = np.array([-bar_start_pos_x+int(bar_width/2), bar_start_pos_y])
vtx3 = np.array([-bar_start_pos_x+int(bar_width/2), bar_start_pos_y+bar_start_height]) 
vtx4 = np.array([-bar_start_pos_x-int(bar_width/2), bar_start_pos_y+bar_start_height])
bar_ref2 = visual.ShapeStim(win=win,fillColor='Blue',lineWidth=0,lineColor='Black',
    vertices=[vtx1, vtx2, vtx3, vtx4])
    
bar_for2 = visual.ShapeStim(win=win,fillColor='Purple',lineWidth=0,lineColor='Black',
    vertices=[vtx1*[-1,1], vtx2*[-1,1], vtx3*[-1,1], vtx4*[-1,1]])

last_wheelPosY = 0

io.clearEvents('all')

demo_timeout_start = core.getTime()
# Run the example until a keyboard event is received.

kb_events = None

rise_amnt = 10
t_start = time.time()

flip_bit = 1 #this is just to flip the sign of width change

#-------------------------------
# SETUP SOUND STIMS
freq_factor = 2*np.pi*np.linspace(0,0.5,22050)
freqL = 440
freqR = 440
soundL = np.sin(freq_factor*freqL)
soundR = np.sin(freq_factor*freqR)
s_out = Sound(np.array([soundL,soundR]).T,secs=10)
#
#-------------------------------
t=1
while not kb_events:
    s_out.stop()
    if t==1:
        s_out.play()
        t=0
    
#    soundL = np.sin(freq_factor*(freqL+10))
#    soundR = np.sin(freq_factor*freqR)
#    s_out.setSound = np.array([soundL,soundR]).T
    # Get the current mouse position
    # posDelta is the change in position * since the last call *
    position, posDelta = mouse.getPositionAndDelta()
    mouse_dX, mouse_dY = posDelta

    # Get the current state of each of the Mouse Buttons
    left_button, middle_button, right_button = mouse.getCurrentButtonStates()

    # If the left button is pressed, change the grating's spatial frequency
    t_now = time.time()
    ref_pos = np.sin((t_now-t_start)*5)*200+200 # + np.cos((t_now-t_start)*10)*50+50
    #ref_pos = XXX_test_seq[t-1]+100 # + np.cos((t_now-t_start)*10)*50+50
    
#    if left_button:
#        grating.setSF(mouse_dX / 5000.0, '+')
#        bar.height -= rise_amnt
#        bar.pos[1] -= rise_amnt/2
#    elif right_button:
#        #grating.setPos(position)
#        bar.height += rise_amnt
#        bar.pos[1] += rise_amnt/2
    #bar.width += (t_now-t_start)*2*flip_bit #gets faster as time continues
    if SPFT_present:
        try:
            ser_str = SPFT_device.read().split('\r\n')[0:-1]
            SPFT_val = int(ser_str[-1]) #XXX this divisor is just to limit for testing, should be replaced with 5-30% of MVC calc
        except:
            continue
        
        bar.height = SPFT_val+bar_start_height #stays as last value, if the value has not been updated by the device
        bar.pos[1] = SPFT_val/2 + bar_start_pos_y
        bar_text.pos = (bar_start_pos_x,bar.pos[1]+bar.height/2)
        bar_text.text = "{:d}".format(int(SPFT_val))
        #this does not currently work
        max_line.setVertices=[[bar_start_pos_x-bar_width/2, bar.height],[bar_start_pos_x+bar_width/2, bar.height]]

        
        if bar.width >= 200:
            flip_bit *= -1
        elif bar.width <= 50:
            flip_bit *= -1
            
    bar_ref.height = ref_pos + bar_start_height
    bar_ref.pos[1] = bar_start_pos_y + ref_pos/2 + bar_start_height
    vtx3 = [-bar_start_pos_x+int(bar_width/2),ref_pos]
    vtx4 = [-bar_start_pos_x-int(bar_width/2),ref_pos]
    bar_ref2.vertices = [vtx1,vtx2,vtx3,vtx4]
#    bar_for2.vertices[2:] = [vtx1*[-1,1], vtx2*[-1,1],vtx3*[-1,1]+[0,SPFT_val+bar_start_height], vtx4*[-1,1]+[0,SPFT_val+bar_start_height]]
    
    # If no buttons are pressed on the Mouse, move the position of the mouse cursor.
    if True not in (left_button, middle_button, right_button):
        fixSpot.setPos(position)

#    if sys.platform == 'darwin':
#        # On macOS, both x and y mouse wheel events can be detected, assuming the mouse being used
#        # supported 2D mouse wheel motion.
#        wheelPosX, wheelPosY = mouse.getScroll()
#    else:
#        # On Windows and Linux, only vertical (Y) wheel position is supported.
        wheelPosY = mouse.getScroll()

    # keep track of the wheel position 'delta' since the last frame.
    wheel_dY = wheelPosY - last_wheelPosY
    last_wheelPosY = wheelPosY

    # Change the orientation of the visual grating based on any vertical mouse wheel movement.
    grating.setOri(wheel_dY * 5, '+')

    # Advance 0.05 cycles per frame.
    grating.setPhase(0.05, '+')

    # Redraw the stim for this frame.
#    fixSpot.draw()
#    grating.draw()
#    bar_ref2.vertices = bar_ref2.vertices + [[0,0],[0,0],[0,1],[0,1]]
    bar.draw()
    bar_ref.draw()
    message.draw()
    message2.draw()
    bar_text.draw()
    max_line.draw()
    bar_ref2.draw()
    bar_for2.draw()
    flip_time = win.flip()  # redraw the buffer

    # Check for keyboard orand mouse events.
    # If 15 seconds passes without receiving any kb or mouse event,
    # then exit the demo
    kb_events = keyboard.getEvents()
    mouse_events = mouse.getEvents()
    if mouse_events:
        demo_timeout_start = mouse_events[-1].time

    if flip_time - demo_timeout_start > 15.0:
        print("Ending Demo Due to 15 Seconds of Inactivity.")
        break

#    for serevt in SPFT_device.getEvents():
#        print(serevt)
    # Clear out events that were not accessed this frame.
    io.clearEvents()

# End of Example

win.close()
core.quit()

# The contents of this file are in the public domain.
