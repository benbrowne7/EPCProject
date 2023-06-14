import os 
import csv
import pandas as pd
import numpy as np
from collections import defaultdict
from csv import writer
from numpy import interp
from bokeh.plotting import figure, show, save
from bokeh.io import show, output_file
from bokeh.io import curdoc
from bokeh.models import HoverTool
from bokeh.models import TabPanel, Tabs, ColumnDataSource, FixedTicker, GeoJSONDataSource, LinearColorMapper, ColorBar, FixedTicker, BasicTicker, FactorRange
from bokeh.models import Span
from bokeh.palettes import brewer
import geopandas as gpd
from bokeh.palettes import mpl, HighContrast3


def addcol(filename, row):
  with open(filename + ".csv", 'a', newline='') as fd:
    writer = csv.writer(fd, dialect='excel')
    writer.writerow(row)
  

abspath = os.path.abspath(__file__)
sourcedir = os.path.dirname(abspath)

os.chdir(sourcedir + "/culmulative_hp")

airdf = pd.read_csv("air-source.csv", low_memory=False)
grounddf = pd.read_csv("ground-source.csv", low_memory=False)

ons_str = "E06000014"

codes = airdf['ONS'].values
ind = -1
years = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
heatpumps = ['Air Source', 'Ground Source']
years = [str(x) for x in years]
ratios = []
for i in range(0,len(codes)):
  if ons_str == codes[i]:
    ind = i
    break

if ind != -1:
  data1 = airdf.iloc[ind][1:].tolist()
  data2 = grounddf.iloc[ind][1:].tolist()
  constit_name = data1[0]
  air_culm = data1[1:]
  ground_culm = data2[1:]
  data = {'years':years, 'Air Source': air_culm, 'Ground Source': ground_culm}


 
  p4 = figure(x_range=years, title="Cumulative Heat Pump Installations under RHI Scheme", toolbar_location=None, tools="hover", tooltips="$name @years: @$name", width=1000, height=800)
  p4.title.text_font_size = '16pt'
  p4.title.align = "center"
  p4.vbar_stack(heatpumps, x='years', source=data, width=0.4, legend_label=heatpumps, color=['blue', 'red'])
  p4.xgrid.grid_line_color = None
  p4.y_range.start = 0
  p4.y_range.start = 0
  p4.x_range.range_padding = 0.1
  p4.xgrid.grid_line_color = None
  p4.axis.minor_tick_line_color = None
  p4.outline_line_color = None
  p4.legend.location = "top_left"
  p4.legend.orientation = "horizontal" 
  tab3 = TabPanel(child=p4, title="Installed Heat Pumps")

  output_file("heatpump_cum.html")
  save(Tabs(tabs=[tab3], width=1000))


  




  









