"""
Created on Sat Feb 18 13:24:37 2023

@author: Lara, based on script on eeg-notebooks github by ErikBjare
and pieces of code from professor Daniele Marinazzo

MMN script with 0 being the standard and 1 being the deviant

"""
#
#setting directory and calling script in anaconda
#cd C:\Users\Asus\Desktop
#python MMN_muse_testrun_sound.py
#
import os
from time import time, sleep
from glob import glob
import random 
from optparse import OptionParser
from operator import itemgetter

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event, sound

from eegnb import generate_save_fn

##pieces needed when running custom script

from eegnb.devices.eeg import EEG


board_name = 'muse2'
experiment = 'MMN trialrun'
session = 2
subject = 2
record_duration = 180

# Create output filename

save_fn = generate_save_fn(board_name, experiment, subject, session)
eeg_device = EEG(device=board_name)

#initialize window

mywin = visual.Window([1920, 1080], monitor="testMonitor", units="deg", fullscr=True, color = (1,1,1))
mywin.mouseVisible = False

def show_instructions():

    instruction_text = """
    Welcome to the MMN experiment! 
 
    Stay still, focus on the centre of the screen, and try not to blink.
    Press the spacebar to continue. 
    
    """
    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=(-1, -1, -1))
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")
    
def show_goodbye():

    instruction_text = """
    Thank you for participating!
    Press the spacebar to exit. 
    
    """
    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=(-1, -1, -1))
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")
    
def present(save_fn: str = save_fn, duration=180, itis=1, jitter = 0, secs=0.07, volume=0.8, eeg= eeg_device, n_stimuli = 500):
    
    markernames = [1, 2]
    record_duration = np.float32(duration)

    ## Initialize stimuli
    aud1 = sound.Sound(500, secs=secs)  
    aud1.setVolume(volume)
    
    aud2 = sound.Sound(550, secs=secs)
    aud2.setVolume(volume)
    
    auds = [aud1, aud2]

     ##generate trial list

    dev1 = [[0,0,1]] * 20
    dev2 = [[0,0,0,1]] * 20 
    dev3 = [[0,0,0,0,1]] * 20 

    stand2 = [[0,0]] * 15 
    stand3 = [[0,0,0]] * 10

    seq_list= dev1 + dev2 + dev3 + stand2 + stand3


     # get indices
    Ind = range(len(seq_list))

     # scramble indices
    Ind_s=np.random.permutation(Ind)


     # scramble seq_list
    seq_list_s = itemgetter(*Ind_s)(seq_list)
     
     # "flatten" the list (taken from http://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python)
    trial_list = [item for sublist in seq_list_s for item in sublist]
     
     # make dataframe
    trials = DataFrame(trial_list, columns = ["stimulus"])
    #create dummy column to save jittered itis
    trials["iti"] = -99
   
    counter = 0
    
    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        eeg.start(save_fn, duration=record_duration)
        
    show_instructions()
 # Setup graphics, simple fixation cross
    fixation = visual.TextStim(win= mywin, text = "+", height =0.5, pos=[0, 0], color = (-1,-1,-1))
    fixation.draw()
    mywin.flip()
    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()
    
    # Iterate through the events
    for ii, trial in trials.iterrows():
        
        counter = counter+ 1
        #add random latency jitter if requested
        if jitter == 0:
            interval = itis
        else:
            interval = itis + random.uniform(0,jitter) #adds a random latency jitter of between 0 and requested upper bound of jitter seconds to requested iti
        trial["iti"] = interval
        
       

        # Select and play sound
        ind = int(trial["stimulus"])
        
        core.wait(interval)
        
        auds[ind].stop()
        auds[ind].play()

        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [trials["stimulus"][counter-1]]
                marker = list(map(int, marker))
            else:
                marker = trials["stimulus"][counter-1]
            eeg.push_sample(marker=marker, timestamp=timestamp)
            
        if len(event.getKeys()) > 0:
            break
        if (time() - start) > record_duration:
            break
        
        event.clearEvents()

        if counter == n_stimuli:
            break

    # Cleanup
    if eeg:
        eeg.stop()
    
    core.wait(3)
    
    show_goodbye()
    
    mywin.close()


present()

