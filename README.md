# JPK-data-analysis-topography
In these scripts Gwyddion libraries are used to read "JPK"file formats. These libraries are compatible with Python 2 so this script should be executed in Python 2 environments. In the beginning of the script a path to Python 2 "site-packages" i.e. ('/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages') is needed. Moreover, a path to the "pygwy" file is also crucial to be add to the script i.e. ('/opt/local/share/gwyddion/pygwy'). 

After a successful execution of the "FixToZero_PlaneLevel_HeightChannel_BatchProcessing.py" script, all the "JPK" file formats in the current directory is preprocessed and saved in the created "preprocessed" folder as a PNG file format.

In "Hieght_distribution.py" script computer vision (OpenCV) is used to create a statistical analysis of the measured samples. By running the script, user will be asked to provide the threshhold of the maximum Height of the samples (between 0.01 to 0.99) in order to create a mask over the selected regions. selecting lower threshhold means more areas will be selected which might include some unwanted debris in the sample. 
After slecting Height threshhold, user should provide the possible Height range of the interested areas (i.e. 20 nm to 500 nm).
Based on the inputs "Histo_Processed.png" will present the height distribution of the selected areas in all the "JPK" files in the current directory.
