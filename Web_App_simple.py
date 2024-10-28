import streamlit as st
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from py_functions.tutorial_funcs import *
from io import BytesIO, StringIO

st.set_page_config(initial_sidebar_state="collapsed")

#### Change lines with #change

# Load Dataframe (df) from \data_sources\

# I would change this flag based on whether I was working locally (flag_gh = False) or if I was about to push to GH and check if it works remotely. Technically the local streamlit could read this file from GH (flag_gh = True), and still work, you just need internet.
flag_gh = True
repository_name = r"Streamlit_Tutorial"
repository_name_st = r"streamlit_tutorial"
path_to_gh_repo = r"https://github.com/narvhal/"+ repository_name 			#change
gh_branch = r"main"   								#change
path_to_df = r"data_sources/df_initialize.xlsx"					 			#change
if flag_gh:
    fn = path_to_gh_repo + r"/raw/refs/heads/" + gh_branch + "/" + path_to_df
else:
	# use os.join, parent dir etc.
    fn = r"C:\Users" +etc+  r"\\" +repository_name+r"\data_sources\df_initialize.xlsx"   			#change


## Read Dataframe
df = pd.read_excel(fn)
cols = df.columns.to_list()

# Check if this df is read in properly: 
for c in cols:
	st.write(c, df[c].iloc[0]) # write column, first value

# Check that functions in py_functions/tutorial_funcs loaded properly: 
st.write("Math function: (x-y)/y, ", example_math(2,6))

##################
########### Let's think of this as where we start putting things onto the web app

st.header("Web app title")
st.write("  ")

str_example = "who"
st.write(f"F-strings can be formatted with in-line $Late\chi$. {str_example}?")

### Plotting!
st.subheader("Plots")

#####You'll change this depending on what data you want to plot
xcol = 'x'   			#change
ycol = 'y'  			#change
xv = df[xcol].iloc[0] 			#change default value of data
yv = df[ycol].iloc[0] 			#change
xvals = np.arange(10)*xv/2 + xv*0.1   			#change make list of slider values
yvals = np.arange(10)*yv/2 + yv*0.1 			#change


################
### Sliders/widgets will go here

# We need this function so that when someone clicks on a widget, the new value is included in the plot 
def proc(key):
    st.info(st.session_state[key])


### For now, assign x_data, y_data 
keystr = "selbox_xdata"
x_col = st.select_slider("Choose the data to plot on the x-axis: ", options = xvals,value = xvals[2],     			#change
	on_change=proc, key = keystr, args = (keystr,))
keystr = "selbox_ydata"
y_col = st.select_slider("Choose the data to plot on the y-axis: ", options = yvals,value = yvals[2],       			#change
	on_change=proc, key = keystr, args = (keystr,))



# this is going to just plot the single point. 
fig, ax = plt.subplots()
plt.scatter(x_col, y_col, 10, 'b')
plt.xlabel(xcol)
plt.ylabel(ycol)

## THREE WAYS to display
# 1
keystr = "checkbox_width"
use_container_width = st.checkbox("Use container width?", on_change=proc, key = keystr, args = (keystr,))
st.pyplot(fig, use_container_width = use_container_width) # instead of plt.show()

# 2 
if flag_gh:
	fn = r"/mount/src/"+repository_name_st+"/temp_img.svg"     # only for github hosted repositories (not local)
	fig.savefig(fn, format="svg")
	st.image(fn, width = 500)


## 3
fig.set_size_inches(3,1)
fig.tight_layout()
buf = BytesIO()
fig.savefig(buf, format="png")
st.image(buf, width = 500)


## Allow download of figure as png:
buf = BytesIO()
fig.savefig(buf, format="png")
st.download_button(label ="Download Figure",
        data=buf,
        file_name="FigureName.png",
        mime="image/png", key = "Download_figure" )

#### Other files you may want to display

if st.checkbox("Show examples of other file displays"):
   	# Show png that is in gh repository
	st.image( r"/mount/src/"+repository_name_st+"/something.png")       			#change to path to actual png
	
	# Allow download of pdf in gh repository
	url = r"/mount/src/"+repository_name_st+"/something.pdf"       			#change to path to actual pdf
	with open(url, "rb") as pdf_file:
		PDFbyte = pdf_file.read()

	st.download_button(label ="Download pdf",       			
                        data=PDFbyte,
                        file_name="Namefordownloadfile.pdf",       			
                        mime='application/octet-stream')    



## Exercise: Write interactive widgets that change qualities of the plots below: for example, allows the user to choose a column from df to plot below, changes axis scale from linear to logarithmic.
#      Use st.select_box, st.checkbox, st.multiselect. Make sure to read the docs to make sure you're using the right argument keywords!
#      Give each widget a UNIQUE name (key = str) and keep these argument values for all:  , on_change=proc, key = keystr, args = (keystr,))
#      Use widgets in a For loop: HOw would you give each widget a unique name if they're in a for loop? 
