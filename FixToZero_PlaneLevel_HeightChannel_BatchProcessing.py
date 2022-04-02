#!/usr/bin/env python
# coding: utf-8

# In[19]:


### Created by Kourosh Rezaei 
###       June 2020
### Last edit 22 June 2020

###  !!!!!   First you have to move this code to the folder of your data you want to be processed. !!!!


###                                       What does this code do? 
###  By running this code a folder named "Processed" would be appeared in which you will find
###  "Height" channel of the all data processed (fixed to zero % plane level) and saved in the PNG format  


    

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
#%matplotlib inline
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import time

from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D



#format of Containers: '/int/data', '/int/data/title', '/int/meta', '/int/data/log'.

# '/int/data' = DataField of channel number 'int'
# '/int/data/title' = Name of channel number 'int'
# '/int/data/log' = Stringlist of channel number 'int'
# '/int/meta' = Container of channel number 'int'



start_time = time.time()

#path = '/Users/kourosh/Documents/Kourosh/Physics/Python_Course_Summer_2019/Python_Gwyddion/AFM_vi5587_PFA_noPBS_May20_Lab2_XY'
path = os.getcwd()
if not os.path.exists('Processed'):
    os.makedirs('Processed')
channels = list()
titles = list()
for filename in glob.glob( os.path.join(path, '*.jpk') ):
    #print "current file is: " + filename
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
    
    Dx = (dx)*10**6
    Dy = (dy)*10**6
    
    x_Width = x_max - x_min
    

    
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

    

    #### visualization ###

    Height_data = gwyutils.data_field_data_as_array(field) ## Bridge from Gwyddion to Numpy or other libraries ##
    afm_data = np.flip(Height_data.T,0)
   
    # Convert data to nanometers (nm)
    afm_data *= (10**9)
    
    max_value = round(np.amax(afm_data),2)
    min_value = round(np.amin(afm_data),2)
    strmin = str(min_value)
    strmax = str(max_value)
    
    # Font parameters
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.size'] = 18
    # Edit axes parameters
    mpl.rcParams['axes.linewidth'] = 2
    # Tick properties
    mpl.rcParams['xtick.major.size'] = 10
    mpl.rcParams['xtick.major.width'] = 2
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['ytick.major.size'] = 10
    mpl.rcParams['ytick.major.width'] = 2
    mpl.rcParams['ytick.direction'] = 'out'



    # Create figure and add axis
    fig = plt.figure(figsize=(8,5))

    ax = fig.add_subplot(111)
    # Remove x and y ticks
    ax.xaxis.set_tick_params(size=0)
    ax.yaxis.set_tick_params(size=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Height')

    # Show AFM image
    img = ax.imshow(afm_data, origin='lower', cmap='gist_heat', extent=(x_min, x_max, y_max, y_min), vmin=min_value, vmax=max_value)
    
    # Create scale bar
    if x_Width < 0.50:
        
        # scale bar calculation
        Scale_bar_size = 100 ## in nm
        Scale_string = str(Scale_bar_size)
        N =Scale_bar_size*10**-9/dx
        Nx = N*dx*10**6
  
        
        ax.fill_between(x=[x_min, x_min+Nx], y1=[y_max-(10*Dy), y_max-(10*Dy)], y2=[y_max-(12*Dy), y_max-(12*Dy)], color='white')

        Scale_bar_mid = (x_min +x_min+Nx)/2
        ax.text(x=Scale_bar_mid, y=y_max-(15*Dy), s='100 nm', va='bottom', ha='center', color='white', size=15)
    
    
    elif  x_Width >= 0.50 and x_Width < 1.00:
        
        # scale bar calculation
        Scale_bar_size = 500 ## in nm
        Scale_string = str(Scale_bar_size)
        N =Scale_bar_size*10**-9/dx
        Nx = N*dx*10**6
  
        # Create scale bar
        ax.fill_between(x=[x_min, x_min+Nx], y1=[y_max-(10*Dy), y_max-(10*Dy)], y2=[y_max-(12*Dy), y_max-(12*Dy)], color='white')

        Scale_bar_mid = (x_min +x_min+Nx)/2
        ax.text(x=Scale_bar_mid, y=y_max-(15*Dy), s='500 nm', va='bottom', ha='center', color='white', size=15)
    
    elif x_Width >= 1.00 and x_Width <= 3.20:
            # scale bar calculation
        Scale_bar_size = 1000 ## in nm
        Scale_string = str(Scale_bar_size)
        N =Scale_bar_size*10**-9/dx
        Nx = N*dx*10**6
  
        # Create scale bar
        ax.fill_between(x=[x_min, x_min+Nx], y1=[y_max-(10*Dy), y_max-(10*Dy)], y2=[y_max-(12*Dy), y_max-(12*Dy)], color='white')

        Scale_bar_mid = (x_min +x_min+Nx)/2
        ax.text(x=Scale_bar_mid, y=y_max-(15*Dy), s='1 um', va='bottom', ha='center', color='white', size=15)
    
    
    else:
                # scale bar calculation
        Scale_bar_size = 3000 ## in nm
        Scale_string = str(Scale_bar_size)
        N =Scale_bar_size*10**-9/dx
        Nx = N*dx*10**6
  
        # Create scale bar
        ax.fill_between(x=[x_min, x_min+Nx], y1=[y_max-(10*Dy), y_max-(10*Dy)], y2=[y_max-(12*Dy), y_max-(12*Dy)], color='white')

        Scale_bar_mid = (x_min +x_min+Nx)/2
        ax.text(x=Scale_bar_mid, y=y_max-(15*Dy), s='3 um', va='bottom', ha='center', color='white', size=15)
    
    # Create axis for colorbar
    cbar_ax = make_axes_locatable(ax).append_axes(position='right', size='5%', pad=0.1)

    # Create colorbar
    cbar = fig.colorbar(mappable=img, cax=cbar_ax)

    # Edit colorbar ticks and labels
    cbar.set_ticks([min_value,max_value])
    cbar.set_ticklabels([strmin,strmax+' nm'])
    # Save in png format
    plt.savefig(name_of_the_original_file+"_Processed.png", format='png')
    plt.clf()
    plt.close()

for f in glob.glob( os.path.join(path, '*_Processed.*',) ):
    shutil.move(f, path+'/Processed')
number_JPK_files =str( len(fnmatch.filter(os.listdir(path), '*.jpk')) )

print("---------------------------------------------")
print("For "+number_JPK_files+" JPK files it took:")
print("--- %s seconds ---" % (time.time() - start_time))
print("---------------------------------------------")





