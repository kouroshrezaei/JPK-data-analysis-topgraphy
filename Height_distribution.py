#!/usr/bin/env python
# coding: utf-8

# In[4]:


#!/usr/bin/env python




### Created by Kourosh Rezaei 
###       June 2020
### Last edit 30 March 2022

###  !!!!!   First you have to move this code to the folder of your data you want to be processed. !!!!
### THIS CODE WORKS ONLY WITH PYTHON 2.X 

###                                       What does this code do? 
###  By running this code two barplots will be saved in the directory.
###    "Histo_Processed_10" which shows the height distribution of the sample based on the 
###   user inputs (threshhold and diameter range). 
###   
###  "Height" channel of the all data preprocessed (fixed to zero % plane level) PLUS areas selected 
###  based on the height threshhold and diameter range getting from the user: 
###

### by running the code the coordinate of the targetet samples are printed
### so that makes it in-situ preselection for further measurements


    





import sys
sys.path.append('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')
import pygtk
pygtk.require20() # adds gtk-2.0 folder to sys.path
import gtk
import gwy
import glob, os, re, shutil
sys.path.append('/opt/local/share/gwyddion/pygwy')
import gwyutils
import fnmatch

import numpy as np
import cv2
import matplotlib as mpl
import matplotlib.pyplot as plt

import time


#format of Containers: '/int/data', '/int/data/title', '/int/meta', '/int/data/log'.

# '/int/data' = DataField of channel number 'int'
# '/int/data/title' = Name of channel number 'int'
# '/int/data/log' = Stringlist of channel number 'int'
# '/int/meta' = Container of channel number 'int'

print("--------------------------------------------------------")
Height_thresh = raw_input("Enter your Height threshold (something from 0.01 to 0.99) : ")

print("--------------------------------------------------------")
Size_min = raw_input("Enter your minimum sample Height (in nm) to be selected : ")
print("--------------------------------------------------------")
Size_max = raw_input("Enter your maximum sample Height (in nm) to be selected : ")
print("--------------------------------------------------------")


start_time = time.time()


path = os.getcwd()

channels = list()
titles = list()


h_hist = []
#d_hist = []


for filename in glob.glob( os.path.join(path, '*.jpk') ):
    #print(filename)
    c = gwy.gwy_file_load(filename, gwy.RUN_INTERACTIVE)
    
   
    
    for key in c.keys_by_name():
        if re.match(r'^/\d+/data/title$', key): # ??????? #
            channels.append(c[key])
            titles.append(key)
            #print(c[key],key)
            
            ## selecting 'Height' channel
    dictionary = dict(zip(channels, titles))
    string = dictionary['Height (measured)']
    Height_channel = string.split("/title")
    HC = Height_channel[0]
    field = c[HC]
    
    ## Bridge from Gwyddion to Numpy or other libraries ##

           
        
     ### image resoulution of chosen channel ###
    xres = field.get_xres()
    yres = field.get_yres()

    xreal = field.get_xreal()
    yreal = field.get_yreal()
    xoff = field.get_xoffset()
    yoff = field.get_yoffset()
    dx = field.get_dx()
    dy = field.get_dy()
    
    xarray = np.linspace(xoff, xreal+xoff, xres)
    yarray = np.linspace(yoff, yreal+yoff, yres)
    
    
    x_min = round((xoff)*10**6,2)
    y_min = round((yoff)*10**6,2)
    x_max = round((xreal+xoff)*10**6,2)
    y_max = round((yreal+yoff)*10**6,2)
    
    Dx = (dx)*10**6 ### pixel size in um
    Dy = (dy)*10**6
    x_Width = x_max - x_min
    y_Width = y_max - y_min

    

    
     ### plane level for chosen channel ###
    coeffs = field.fit_plane()
    field.plane_level(*coeffs)
    field.data_changed()
         
     ### fix to zero for chosen channel ###
    field.add(-field.get_min())
    field.data_changed()
     
    ### replace the processed channel back to the original container    
    c[HC] = field
  
   

    ## Save in GWY format ##
    name_for_saving = filename.split("/")
    FN = name_for_saving[-1].split(".jpk")
    name_of_the_original_file = FN[0]
    #gwy.gwy_file_save(c, name_of_the_original_file+"_Processed.gwy", gwy.RUN_INTERACTIVE)

    
    


    ## Bridge from Gwyddion to Numpy or other libraries ##

    Height_data = gwyutils.data_field_data_as_array(field) 
    afm_data = np.flip(Height_data.T,0)
    
    
        # Convert data to nanometers (nm)
    afm_data *= (10**9)
    
    
    max_value = round(np.amax(afm_data),2)
    min_value = round(np.amin(afm_data),2)
    strmin = str(min_value)
    strmax = str(max_value)
    
    
    masked_afm_data = Height_data.T > float(Height_thresh)*max_value
    
    masked_afm_data = masked_afm_data.astype(int) 
    
    image_8bit = np.uint8(masked_afm_data * 255)
    
    threshold_level = 127 # Set as you need...
    _, binarized = cv2.threshold(image_8bit, threshold_level, 255, cv2.THRESH_BINARY)

    _, contours, hierarchy = cv2.findContours(binarized, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    countor_maps = np.zeros((256,256))
    print(" ")
    #print("coordinates of the possible target based on inputs: ")
    print("File name: "+str(filename.split('/')[-1]))
    for i in range(len(contours)):
        (x,y),radius = cv2.minEnclosingCircle(contours[i])
        area = cv2.contourArea(contours[i])
        center = (int(x),int(y))
        #print("coordinates of the possible target based on inputs: ")
        print('                            Coordinate (x,y) (in um): '+str((xarray[center[0]])*10**6)+','+ str((yarray[center[1]])*10**6)+'     Height (in nm): '+str(Height_data[center[0]][center[1]]))
        #print(Height_data[center[0]][center[1]])
        print(" ")
        #for j in range(len(contours[i])):

            #countor_maps[center[0],center[1]] = 256
        #mask_afm[center[0],center[1]] = 0
            #radius = int(radius)
           # countor_maps[contours[i][j][0][0]][contours[i][j][0][1]]=256
       

        h_hist.append(Height_data[center[0]][center[1]])
        #d_hist.append(dx*1e9*radius*2)
h_hist = [x for x in h_hist if int(Size_min) < x < int(Size_max)]



fig = plt.figure(figsize=(20,12))
plt.hist(h_hist, bins=50)
plt.xlabel('Height (nm)',fontsize=20)
plt.ylabel('Frequency',fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.savefig("Histo_Processed.png",dpi=300)
plt.clf()
plt.close()


number_JPK_files =str( len(fnmatch.filter(os.listdir(path), '*.jpk')) )
print("---------------------------------------------")
print("For "+number_JPK_files+" JPK files it took:")
print("--- %s seconds ---" % (time.time() - start_time))
print("---------------------------------------------")

