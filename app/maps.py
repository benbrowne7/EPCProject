
import mpld3
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import statistics
import numpy as np
import json
from shapely.geometry import Point
from bokeh.plotting import figure, show, save
from bokeh.io import show, output_file
from bokeh.io import curdoc
from bokeh.models import HoverTool
from bokeh.models import TabPanel, Tabs, ColumnDataSource, FixedTicker, GeoJSONDataSource, LinearColorMapper, ColorBar, FixedTicker, BasicTicker, FactorRange
from bokeh.models import Span, Label
from bokeh.palettes import brewer
import geopandas as gpd
from bokeh.palettes import mpl, Inferno256
from bng_latlon import WGS84toOSGB36
from bng_latlon import OSGB36toWGS84
import plotly.express as px
import plotly.graph_objects as go
from .helper import *
import time


def round_down(n, decimals=1):
    return int(math.floor(n / 10.0)) * 10

def round_up(n, decimals=1):
    return int(math.ceil(n / 10.0)) * 10

def round_down_hpr(n, decimals=1):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

def round_up_hpr(n, decimals=1):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


def bigmap(w,h):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  if os.path.exists(sourcedir + "/templates/bigmap/constit_map.html"):
      return True

  file = "Local_Authority_Districts_(December_2020)_UK_BUC.shp"
  map=gpd.read_file(sourcedir + "/data/Shapefile/" + file)
  map.drop(map.index[314:357], inplace=True)

  constit = pd.read_csv(sourcedir + "/data/constit_data.csv", low_memory=False)

  epc_col = []
  hpr_col = []

  for index, row in map.iterrows():
    ons = row['LAD20CD']
    try:
      row_data = constit.loc[constit['ONS'] == ons]
    except:
      epc_mean = np.nan
      hpr_mean = np.nan
    else:
      epc_mean = row_data['EPC_MEAN'].values[0]
      hpr_mean = row_data['HPR_MEAN'].values[0]
    epc_col.append(epc_mean)
    hpr_col.append(hpr_mean)

  map['epc_means'] = epc_col
  map['hpr_means'] = hpr_col

  merged = map.merge(constit, left_on='LAD20CD', right_on='ONS')
  merged_json = json.loads(merged.to_json())
  json_data = json.dumps(merged_json)

  w = int(0.412 * w)
  h = int(0.8*h)

  curdoc().theme = "dark_minimal"

  geosource = GeoJSONDataSource(geojson = json_data)
  palette = mpl['Inferno'][10]
  color_mapper = LinearColorMapper(palette=palette, low = 50, high=70)
  hover = HoverTool(tooltips = [('LAD', '@LAD20NM'), ('ONS', '@LAD20CD'),('Av. EPC', '@epc_means')])
  tools = "pan,wheel_zoom,reset"
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='black', major_tick_line_color='black', ticker=BasicTicker(desired_num_ticks=len(palette)+1))
  p1 = figure(title = 'Av. EPC Rating by Local Authority District', toolbar_location = 'right', toolbar_sticky = False, tools = [tools, hover], active_scroll='wheel_zoom', width=w, height=h)
  p1.title.text_font_size = '18pt'
  p1.title.align = "center"
  p1.axis.visible = False
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None#Add patch renderer to figure.
  p1.patches('xs','ys', source = geosource,fill_color = {'field' :'epc_means', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p1.add_layout(color_bar, 'below')
  tab1 = TabPanel(child=p1, title="EPC Rating")


  palette = mpl['Inferno'][6]
  color_mapper = LinearColorMapper(palette=palette, low = 0.7, high=1)
  hover = HoverTool(tooltips = [('LAD', '@LAD20NM'), ('ONS', '@LAD20CD'), ('Av. HPR', '@hpr_means')])
  tools = "pan,wheel_zoom,reset"
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='black', major_tick_line_color='black', ticker=BasicTicker(desired_num_ticks=len(palette)+1))
  p2 = figure(title = 'Av. HPR by Local Authority District', toolbar_location = 'right', toolbar_sticky = False, tools = [tools,hover], active_scroll='wheel_zoom', width=w, height=h)
  p2.title.text_font_size = '18pt'
  p2.title.align = "center"
  p2.axis.visible = False
  p2.xgrid.grid_line_color = None
  p2.ygrid.grid_line_color = None#Add patch renderer to figure.
  p2.patches('xs','ys', source = geosource,fill_color = {'field' :'hpr_means', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p2.add_layout(color_bar, 'below')
  tab2 = TabPanel(child=p2, title="Heat Pump Readiness")

  os.chdir(sourcedir + "/templates/bigmap")
  output_file("constit_map.html")
  save(Tabs(tabs=[tab1,tab2], width=w))

def adoptionmap(w,h):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  if os.path.exists(sourcedir + "/templates/bigmap/adoption_map.html"):
      return True

  file = "LAD_DEC_2022_UK_BUC.shp"
  map=gpd.read_file(sourcedir + "/data/Shapefile/" + file)
  map.drop(map.index[320:352], inplace=True)

  heatpump = pd.read_csv(sourcedir + "/data/heatpump-cum.csv", low_memory=False)
  population = pd.read_csv(sourcedir + "/data/population.csv", engine='python')
  sum_col = []
  rate_col = []
  pop_col = []

  w = int(0.412 * w)
  h = int(0.8*h)

  curdoc().theme = "dark_minimal"


  for index, row in map.iterrows():
    ons = row['LAD22CD']
    try:
      row_data = heatpump.loc[heatpump['ONS'] == ons].values[0]
    except:
      sum_val = np.nan
      av_rate = np.nan
    else:
      sum_val = sum(row_data[2:])
      rates = row_data[13:]
      av_rate = (((rates[2] - rates[1]) / rates[1]) + ((rates[1] - rates[0]) / rates[0])) * 0.5
      av_rate = round(av_rate * 100,1)

    sum_col.append(sum_val)
    rate_col.append(av_rate)

    try:
      row_data = population.loc[population['ONS'] == ons].values[0]
    except:
      pop_val = np.nan
    else:

      pop_val = int(row_data[2].replace(",", ""))
    pop_col.append(pop_val)

  hp_density = []
  for i in range(0, len(sum_col)):
    val = round(sum_col[i] / pop_col[i] * 1000, 2)
    hp_density.append(val)

  #-----------------------------------------------------------
  new = []
  new1 = []
  for i in rate_col:
    if np.isnan(i) == True:
      continue
    else:
      new.append(i)
  for i in hp_density:
    if np.isnan(i) == True:
      continue
    else:
      new1.append(i)
  av_rate = statistics.mean(new)
  av_density = statistics.mean(new1)

  rate_percentile = np.percentile(new, [10,20,30,40,50,60,70,80,90])
  density_percentile = np.percentile(new1, [10,20,30,40,50,60,70,80,90])


  map['hp_density'] = hp_density
  map['hp_rate'] = rate_col

  merged = map.merge(heatpump, left_on='LAD22CD', right_on='ONS')
  merged_json = json.loads(merged.to_json())
  json_data = json.dumps(merged_json)

  min_density = min(hp_density)
  max_density = max(hp_density)

  

  geosource = GeoJSONDataSource(geojson = json_data)
  palette = Inferno256
  x_ticks = [0,5,10,15,20,25,30,35,40,45,50,55]
  color_mapper = LinearColorMapper(palette=palette, low = min_density, high=max_density)
  hover = HoverTool(tooltips = [('LAD', '@LAD22NM'),('HP per 1000', '@hp_density{0.0}')])
  tools = "pan,wheel_zoom,reset"
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='black', major_tick_line_color='black', ticker=FixedTicker(ticks=x_ticks))
  p1 = figure(title = 'Installed Heat Pumps Per 1000 People (RHI Scheme - 2022)', toolbar_location = 'right', toolbar_sticky = False, tools = [tools, hover], active_scroll='wheel_zoom', width=w, height=h)

  
  p1.axis.visible = False
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None#Add patch renderer to figure. 
  p1.patches('xs','ys', source = geosource,fill_color = {'field' :'hp_density', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p1.add_layout(color_bar, 'below')
  p1.title.text_font_size = '16pt'
  p1.title.align = "center"
  tab1 = TabPanel(child=p1, title="Heat Pump Density")

  #------------------------------------------------------------------------

  min_rate = int(min(rate_col))
  max_rate = int(max(rate_col))

  palette = Inferno256
  color_mapper = LinearColorMapper(palette=palette, low = min_rate, high=100)
  hover = HoverTool(tooltips = [('LAD', '@LAD22NM'), ('RATE HP', '@hp_rate{0.0}%')])
  tools = "pan,wheel_zoom,reset"
  x_ticks = [0,10,20,30,40,50,60,70,80,90,100]
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='black', major_tick_line_color='black', ticker=FixedTicker(ticks=x_ticks))

  
  p2 = figure(title = 'Average Yearly % Increase in Heat Pumps under RHI (since 2020)', toolbar_location = 'right', toolbar_sticky = False, tools = [tools,hover], active_scroll='wheel_zoom', width=w, height=h)
  p2.axis.visible = False
  p2.xgrid.grid_line_color = None
  p2.ygrid.grid_line_color = None#Add patch renderer to figure. 
  p2.patches('xs','ys', source = geosource,fill_color = {'field' :'hp_rate', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p2.add_layout(color_bar, 'below')
  p2.title.text_font_size = '18pt'
  p2.title.align = "center"
  tab2 = TabPanel(child=p2, title="Rate Heat Pump Adoption")


  try:
    os.chdir(sourcedir + "/templates/bigmap")
  except:
    return True
  else:
    output_file("adoption_map.html")

  save(Tabs(tabs=[tab1,tab2], width=w))

def graph(ons,w,h):

  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)
  filename = sourcedir + "/data/EPCByYear/" + ons + "-yoy.csv"
  ons_str = str(ons)

  df = pd.read_csv(filename)
  yoy = df['y/y'].values
  av_yoy = round(np.mean(yoy),1)
  dates = df['date'].values
  ratings = df['average_rating'].values
  dates = [int(x) for x in dates]
  ratings = [int(x) for x in ratings]

  w = int(0.535 * w)
  h = int(0.444*0.85*h)

  curdoc().theme = "dark_minimal"
  tools = "reset,save"
  hover = HoverTool(tooltips = [('EPC', '$y'), ('Year', '$x{0000}')], )
  p1 = figure(title="Average EPC for {}".format(ons), x_axis_label='Year', y_axis_label='EPC Rating', sizing_mode="stretch_width", toolbar_location = 'right', toolbar_sticky = False, tools = [tools, hover], width=w, height=h)
  p1.title.text_font_size = '16pt'
  p1.title.align = "center"
  p1.line(dates, ratings, line_width=6, legend_label=ons_str, color='blue')
  p1.legend.location = "bottom_right"
  p1.legend.label_text_font_style = "bold"
  p1.legend.border_line_width = 3
  p1.legend.border_line_color = "black"
  tab1 = TabPanel(child=p1, title="EPC Trend")

  #-----------------------------------------------------------


  hover = HoverTool(tooltips = [('%Y/Y', '$y'), ('Year', '$x{0000}')], )
  p2 = figure(title="EPC %Y/Y for {}".format(ons), x_axis_label='Year', y_axis_label="% Change", sizing_mode="stretch_width", toolbar_location = 'right', toolbar_sticky = False, tools = [tools,hover], width=w, height=h)
  p2.title.text_font_size = '16pt'
  p2.title.align = "center"
  p2.line(dates, yoy, line_width=6, legend_label=ons_str, color='blue')
  p2.legend.location = "bottom_right"
  p2.legend.label_text_font_style = "bold"
  p2.legend.border_line_width = 3
  p2.legend.border_line_color = "black"

  threshold = 0
  hline = Span(location=threshold, dimension='width', line_color='white', line_width=2)
  p2.renderers.extend([hline])

  tab2 = TabPanel(child=p2, title="EPC Y/Y")

  #-------------------------------------------------------------

  filename = sourcedir + "/data/averageyear.csv"
  df1 = pd.read_csv(filename)
  codes = df1['ONS'].values
  ind = -1
  years = [2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
  years = [str(x) for x in years]
  ratios = []
  for i in range(0,len(codes)):
    if ons_str == codes[i]:
      ind = i
      break

  if ind != -1:
    data = df1.iloc[ind][1:].tolist()
    source = ColumnDataSource({'x':years, 'data':data})
    total = sum(data)
    expired = sum(data[:5])
    exp = int(expired/total*100)
    hover = HoverTool(tooltips = [('Number', '@data'), ('Year', '@x')], )
    p3 = figure(x_range=years, title="Age Distribution of EPCs for {}".format(ons), x_axis_label='Year', y_axis_label="Certificates", toolbar_location=None, tools=[hover], width=w, height=h)
    p3.title.text_font_size = '16pt'
    p3.title.align = "center"
    p3.vbar(x='x', top='data', width=0.4, source=source, color='blue')
    p3.xgrid.grid_line_color = None
    p3.y_range.start = 0
    tab3 = TabPanel(child=p3, title="Age Distribution")
  
  #-----------------------------------------------------------------

  os.chdir(sourcedir + "/templates/graphs")
  name = ons + "_graph" ".html"
  output_file(name)
  save(Tabs(tabs=[tab1,tab2,tab3], width=w))

  return name, av_yoy, exp

def graphadoption(ons,w,h):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)
  ons_str = str(ons)

  w = int(0.535 * w)
  h = int(0.444*0.85*h)
  curdoc().theme = "dark_minimal"

  os.chdir(sourcedir + "/data/culmulative_hp")

  airdf = pd.read_csv("air-source.csv", low_memory=False)
  grounddf = pd.read_csv("ground-source.csv", low_memory=False)

  codes = airdf['ONS'].values
  ind = -1
  years = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022]
  heatpumps = ['Air Source', 'Ground Source']
  years = [str(x) for x in years]
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


 
    p4 = figure(x_range=years, title="Cumulative Heat Pump Installations under RHI Scheme for {}".format(ons),x_axis_label='Year', y_axis_label="Heat Pumps", toolbar_location=None, tools="hover", tooltips="$name @years: @$name", width=w, height=h)
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
    tab4 = TabPanel(child=p4, title="Heat Pump Installations")
  
  #------------------------------------------------------------------------
  cuml = pd.read_csv(sourcedir + "/data/heatpump-cum.csv")
  data = cuml.loc[cuml['ONS'] == ons].values[0][2:]
  rates = []
  for i in range(0,len(data)-1):
    if data[i] == 0:
      rates.append(0)
      continue
    val = round((data[i+1] - data[i]) / data[i], 1) * 100
    rates.append(val)

  hover = HoverTool(tooltips = [('%Y/Y', '$y'), ('Year', '$x{0000}')], )
  p1 = figure(title="Annual % Change for Heat Pump Installations (RHI Scheme) for {}".format(ons), x_axis_label='Year', y_axis_label='% Change', sizing_mode="stretch_width", toolbar_location = 'right', toolbar_sticky = False, tools = [hover], width=w, height=h)
  p1.title.text_font_size = '16pt'
  p1.title.align = "center"
  p1.line(years[1:], rates, line_width=6, legend_label=ons_str, color='blue')
  p1.legend.location = "bottom_right"
  p1.legend.label_text_font_style = "bold"
  p1.legend.border_line_width = 3
  p1.legend.border_line_color = "black"

  hline = Span(location=47, dimension='width', line_color='white', line_width=2)
  p1.renderers.extend([hline])
  label = Label(x=2010, y=47, y_offset=5, text='Annual % Increase required to hit 600,000 installations in 2028 Target (47%)', text_color='red')
  p1.add_layout(label)
  tab1 = TabPanel(child=p1, title="Annual % Increase in Installations")



  os.chdir(sourcedir + "/templates/graphsadoption")
  name = ons + "_graph" ".html"
  output_file(name)
  save(Tabs(tabs=[tab4,tab1], width=w))


def ladmap1(ons,w,h):

  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  filename = sourcedir + "/data/constitbounds_data/" + ons + ".geojson"
  ons_str = str(ons)
  map = gpd.read_file(filename)
  filename = sourcedir + "/data/postcode_data/" + ons_str + "-postcode.csv"
  df = pd.read_csv(filename)
  ons2outcodes = pd.read_csv(sourcedir + "/data/ons2outcodes.csv")

  inds = []
  
  outcodes = ons2outcodes.loc[ons2outcodes['ONS'] == ons_str].values[0][1:]

  for index, row in df.iterrows():
      postcode = row['postcode']
      if postcode not in outcodes:
        inds.append(index)

  df = df.drop(inds, axis=0)

  lats = df['lat'].values.tolist()
  longs = df['long'].values.tolist()
  easts = []
  norths = []
  for i in range(0,len(lats)):
    e, n = WGS84toOSGB36(float(lats[i]), float(longs[i]))
    easts.append(e)
    norths.append(n)

  df['long'] = easts
  df['lat'] = norths


  epcs = df['epc'].values.tolist()
  hprs = df['hpr'].values.tolist()
  epc_min = np.min(epcs)
  epc_max = np.max(epcs)
  hpr_min = np.min(hprs)
  hpr_max = np.max(hprs)

  w = int(0.41 * w)
  h = int(0.8*h)

  low = round_down(epc_min)
  high = round_up(epc_max)

  if high - low <= 30:
    x = 5
  else:
    x = 10

  tick = np.arange(low, high+x, x)

  t = len(tick)-1
  if t == 2:
    tick = np.arange(low,high+2.5, 2.5)


  cds = ColumnDataSource(df)

  merged_json = json.loads(map.to_json())
  json_data = json.dumps(merged_json)
  geosource = GeoJSONDataSource(geojson = json_data)

  
  if len(tick-1) <= 3:
    palette = brewer['YlOrRd'][3]
  else:
    palette = brewer['YlOrRd'][len(tick)-1]

  color_mapper = LinearColorMapper(palette=palette, low = low, high=high)
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='white', major_tick_line_color='white', ticker=FixedTicker(ticks=tick))


  p1 = figure(title = 'Av. EPC By Postcode for {}'.format(ons),  toolbar_location = None, width=w, height=h)
  p1.title.text_font_size = '16pt'
  p1.title.align = "center"
  p1.toolbar.active_drag = None
  p1.toolbar.active_scroll = None
  p1.toolbar.active_tap = None
  p1.axis.visible = False
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None
  circ = p1.circle(x='long', y='lat', source=cds, size=20, name='circle', fill_color = {'field' :'epc', 'transform' : color_mapper}, alpha=1)
  patch = p1.patches( source = geosource, fill_color='gray', fill_alpha=0.6, level='underlay')
  hover = HoverTool(renderers=[circ], tooltips = [('Postcode', '@postcode'), ('EPC', '@epc')])
  p1.add_tools(hover)
  p1.add_layout(color_bar, 'below')
  tab1 = TabPanel(child=p1, title="Av. EPC By Postcode")


  low = round_down_hpr(hpr_min)
  high = round_up_hpr(hpr_max)

  if high - low <= 0.3:
    x = 0.05
  else:
    x = 0.1

  tick = np.arange(low,high+x, x)

  if len(tick-1) <= 3:
    palette = brewer['YlOrRd'][3]
  else:
    palette = brewer['YlOrRd'][len(tick)-1]
  color_mapper = LinearColorMapper(palette=palette, low=low, high=high)
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='white', major_tick_line_color='white', ticker=FixedTicker(ticks=tick))

  p2 = figure(title = 'Av. HPR By Postcode for {}'.format(ons),  toolbar_location = None, width=w, height=h)
  p2.title.text_font_size = '16pt'
  p2.title.align = "center"
  p2.toolbar.active_drag = None
  p2.toolbar.active_scroll = None
  p2.toolbar.active_tap = None
  p2.axis.visible = False
  p2.xgrid.grid_line_color = None
  p2.ygrid.grid_line_color = None
  circ = p2.circle(x='long', y='lat', source=cds, size=20, name='circle', fill_color = {'field' :'hpr', 'transform' : color_mapper}, alpha=1)
  patch = p2.patches( source = geosource, fill_color='gray', fill_alpha=0.6, level='underlay')
  hover = HoverTool(renderers=[circ], tooltips = [('Postcode', '@postcode'), ('HPR', '@hpr')])
  p2.add_tools(hover)
  p2.add_layout(color_bar, 'below')
  tab2 = TabPanel(child=p2, title="Av. HPR by Postcode")


  os.chdir(sourcedir + "/templates/ladmaps")
  name = ons + "_map" ".html"
  output_file(name)
  save(Tabs(tabs=[tab1,tab2], width=w))
  return True


def ladmap(ons,w,h):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  filename = sourcedir + "/data/constitbounds_data/" + ons + ".geojson"
  gdf = gpd.read_file(filename)
  gdf = gdf.to_crs("EPSG:4326")
  
  
  try:
    g = json.loads(gdf.to_json())
    coords = g['features'][0]['geometry']['coordinates'][0]
  except:
    gdf = gpd.read_file(sourcedir + "/data/constitbounds_data/Local_Authority_Districts_December_2020_UK_BUC_2022.GEOJSON")
    gdf = gdf.loc[gdf['LAD20CD'] == str(ons)]
    gdf = gdf.to_crs("EPSG:4326")
    g = json.loads(gdf.to_json())
    coords = g['features'][0]['geometry']['coordinates'][0]
    

  try:
    os.chdir(sourcedir + "/data/Postcode-Data/" + str(ons))
  except:
    print("dir not found")
    return True
  
  outcode_df = pd.read_csv("outcode_data.csv")
  sector_df = pd.read_csv("sector_data.csv")
  #postcode_df = pd.read_csv("postcode_data.csv")

  #get rid of outcodes not in area
  ons2outcodes = pd.read_csv(sourcedir + "/data/ons2outcodes.csv")
  inds = []
  outcodes = ons2outcodes.loc[ons2outcodes['ONS'] == str(ons)].values[0][1:]
  for index, row in outcode_df.iterrows():
      postcode = row['outcode']
      if postcode not in outcodes:
        inds.append(index)
  outcode_df = outcode_df.drop(inds, axis=0)

  w = int(0.41 * w)
  h = int(0.8*h)

  mapbox_toke = "pk.eyJ1IjoiYmVuYnJvd25lNyIsImEiOiJjbGo1eWhsbnIwNDJsM21xcG1lcTJxY2thIn0.6alroAlfLvYEQlD8A8339g"
  

  lats = outcode_df['lat']
  lons = outcode_df['long']

  av_lat = statistics.mean(lats)
  av_lon = statistics.mean(lons)

  zoom, center = zoom_center(lons=lons, lats=lats)
  zoom = int(zoom*0.88)

  fig = px.scatter_mapbox(outcode_df, lat="lat", lon="long", hover_name="outcode", hover_data={'epc':True, 'hpr':True, 'lat':False, 'long':False}, color='epc', height=h, width=w, zoom=zoom, center=center)
  fig.update_traces(marker={'size': 14})

  fig1 = px.scatter_mapbox(sector_df, lat="long", lon="lat", hover_name="sector", hover_data={'epc':True, 'hpr':True, 'lat':False, 'long':False}, color='hpr', height=h, width=w, zoom=zoom, center=center)
  fig1.update_traces(marker={'size': 14})

  fig.add_trace(fig1.data[0])

  #alt style: stamen-terrain
  fig.update_layout(
    mapbox = {
        'style': "dark",
        'center': center,
        'zoom': zoom, 'layers': [{
            'source': {
                'type': "FeatureCollection",
                'features': [{
                    'type': "Feature",
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [[
                            coords
                        ]]
                    }
                }]
            },
            'type': "fill", 'below': "traces", 'color': "aliceblue", "opacity":0.6}]},
    margin = {'l':0, 'r':0, 'b':0, 't':0})
  fig.update_layout(mapbox_bounds={"west":av_lon-1, "east": av_lon+1, "south":av_lat-1, "north":av_lat+1})
  fig.update_layout(mapbox_accesstoken=mapbox_toke)

  return fig




def biggrid(w,h):

  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  northernpower = pd.read_csv(sourcedir + "/powerdata/raw/" + "northern-pow-demand.csv")
  nationalgrid = pd.read_csv(sourcedir + "/powerdata/raw/" + "WPD-Network-Capacity-Map.csv", low_memory=False)
  ukpowernetworks = pd.read_csv(sourcedir + "/powerdata/raw/" + "ukpn_primary_postcode_area.csv", low_memory=True)
  northwestelectric = pd.read_csv(sourcedir + "/powerdata/raw/" + "northwest-elec-primary-demand.csv")

  ukpowernetworks = ukpowernetworks.drop(['Geo Shape'], axis=1)

  #shapefile = "LAD_DEC_2022_UK_BUC.shp"
  #uk_bounds = gpd.GeoDataFrame.from_file(sourcedir + "/data/Shapefile/" + shapefile)

  combo_df, combined_dict = combinesubstationdata(nationalgrid, northernpower, ukpowernetworks, northwestelectric)
  


  w = w*0.66
  h = h*0.84

  mapbox_toke = "pk.eyJ1IjoiYmVuYnJvd25lNyIsImEiOiJjbGo1eWhsbnIwNDJsM21xcG1lcTJxY2thIn0.6alroAlfLvYEQlD8A8339g"
  px.set_mapbox_access_token(mapbox_toke)

  lats = combo_df['Latitude']
  lons = combo_df['Longitude']

  zoom, center = zoom_center(lons=lons, lats=lats)
  #zoom = int(zoom*0.8)

  fig = px.scatter_mapbox(combo_df, lat="Latitude", lon="Longitude", hover_name="Substation Name", hover_data={"Type":False, "Demand Headroom (MVA)":True, "Demand Headroom RAG":False, 'Firm Capacity (MVA)':True, 'Latitude':False, 'Longitude':False}, color='DNO', color_discrete_map={'nationalgrid':'green', 'northernpower':'#FFBF00'}, height=h, width=w, zoom=zoom, center=center)
  fig.update_layout(mapbox_style="dark")
  fig.update_traces(marker={'size': 6})



  fig.update_layout(legend=(dict(yanchor="top", y=0.99, xanchor="left", x=0.01)))
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
  fig.update_layout(mapbox_bounds={"west":-10, "east": 10, "south":48, "north":60})
  fig.write_html(sourcedir + "/templates/biggrid/biggrid.html")

  capacity_sum, headroom_sum = calculatetotalheadroom(combined_dict)

  constit22 = getconstitnames()

  return int(capacity_sum), int(headroom_sum), int((capacity_sum-headroom_sum)/capacity_sum*100), constit22

def zoom_center(lons, lats, projection='mercator'):
    width_to_height = 2.0
  
    
    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        'lon': round((maxlon + minlon) / 2, 6),
        'lat': round((maxlat + minlat) / 2, 6)
    }
    
    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
        0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
        0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
        47.5136, 98.304, 190.0544, 360.0
    ])
    
    if projection == 'mercator':
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f'{projection} projection is not implemented'
        )
    
    return zoom, center

def biggridsingle(w, h, constit_name):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  northernpower = pd.read_csv(sourcedir + "/powerdata/raw/" + "northern-pow-demand.csv")
  nationalgrid = pd.read_csv(sourcedir + "/powerdata/raw/" + "WPD-Network-Capacity-Map.csv", low_memory=False)
  ukpowernetworks = pd.read_csv(sourcedir + "/powerdata/raw/" + "ukpn_primary_postcode_area.csv", low_memory=True)
  northwestelectric = pd.read_csv(sourcedir + "/powerdata/raw/" + "northwest-elec-primary-demand.csv")

  ukpowernetworks = ukpowernetworks.drop(['Geo Shape'], axis=1)


  #get lad bounds
  ons2lad = pd.read_csv(sourcedir + "/data/ONS2LAD.csv")
  row = ons2lad.loc[ons2lad['LAD20NM'] == constit_name]
  try:
    ons = row['LAD20CD'].values[0]
  except:
    return True
  filename = sourcedir + "/data/constitbounds_data/" + ons + ".geojson"
  gdf = gpd.read_file(filename)
  gdf = gdf.to_crs("EPSG:4326")
  
  try:
    g = json.loads(gdf.to_json())
    coords = g['features'][0]['geometry']['coordinates'][0]
  except:
    gdf = gpd.read_file(sourcedir + "/data/constitbounds_data/Local_Authority_Districts_December_2020_UK_BUC_2022.GEOJSON")
    gdf = gdf.loc[gdf['LAD20CD'] == str(ons)]
    gdf = gdf.to_crs("EPSG:4326")
    g = json.loads(gdf.to_json())
    coords = g['features'][0]['geometry']['coordinates'][0]

  shapefile = "LAD_DEC_2022_UK_BUC.shp"
  uk_bounds = gpd.GeoDataFrame.from_file(sourcedir + "/data/Shapefile/" + shapefile)

  for row in uk_bounds.itertuples():
    if row[2] == constit_name:
      lad_bounds = row
      break
  
  poly = lad_bounds[8]

  
  combo_df, combined_dict = combinesubstationdata(nationalgrid, northernpower, ukpowernetworks, northwestelectric)
  

  valid_substations = {}
  for key, vals in combined_dict.items():
    lat = vals[3]
    long = vals[4]
    e, n = WGS84toOSGB36(float(lat), float(long))
    P = Point(e,n)
    if P.within(poly) == True:
      valid_substations[key] = vals
    
  if not valid_substations:
    return False

  validsubs_df = pd.DataFrame.from_dict(valid_substations, orient='index', columns=['Substation Name', 'ID', 'Type', 'Latitude', 'Longitude', 'Firm Capacity (MVA)', 'Demand Headroom (MVA)', 'Demand Peak (MVA)', 'Demand Headroom RAG', 'DNO'])

  w = w*0.66
  h = h*0.84

  mapbox_toke = "pk.eyJ1IjoiYmVuYnJvd25lNyIsImEiOiJjbGo1eWhsbnIwNDJsM21xcG1lcTJxY2thIn0.6alroAlfLvYEQlD8A8339g"
  px.set_mapbox_access_token(mapbox_toke)

  lats = validsubs_df['Latitude']
  lons = validsubs_df['Longitude']
  av_lat = statistics.mean(lats)
  av_lon = statistics.mean(lons)

  zoom, center = zoom_center(lons=lons, lats=lats)
  zoom = zoom*0.9


  fig = px.scatter_mapbox(validsubs_df, lat="Latitude", lon="Longitude", hover_name="Substation Name", hover_data={"Type":False, "Demand Headroom (MVA)":True, "Demand Headroom RAG":False, 'Firm Capacity (MVA)':True, 'Latitude':False, 'Longitude':False}, color='Demand Headroom RAG', color_discrete_map={'GREEN':'green', 'AMBER':'#FFBF00', 'RED':'red'}, height=h, width=w, zoom=zoom, center=center)
  fig.update_layout(mapbox_style="dark")
  fig.update_traces(marker={'size': 18})
  fig.update_layout(legend=(dict(yanchor="top", y=0.99, xanchor="left", x=0.01)))
  fig.update_layout(
    mapbox = {
        'style': "dark",
        'center': center,
        'zoom': zoom, 'layers': [{
            'source': {
                'type': "FeatureCollection",
                'features': [{
                    'type': "Feature",
                    'geometry': {
                        'type': "MultiPolygon",
                        'coordinates': [[
                            coords
                        ]]
                    }
                }]
            },
            'type': "fill", 'below': "traces", 'color': "aliceblue", "opacity":0.2}]},
    margin = {'l':0, 'r':0, 'b':0, 't':0})
  fig.update_layout(mapbox_bounds={"west":av_lon-1, "east": av_lon+1, "south":av_lat-1, "north":av_lat+1})


  fig.write_html(sourcedir + "/templates/biggrid/biggridsingle.html")

  return valid_substations

  
def calculatetotalheadroom(combined_dict):
  #[sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "DNO"]
  capacity_sum = 0
  demand_sum = 0
  headroom_sum = 0
  for key, vals in combined_dict.items():
    if math.isnan(vals[5]) or math.isnan(vals[6] or math.isnan(vals[7])):
      continue
    if vals[9] == 'Electricity North West':
      continue
    capacity_sum += float(vals[5])
    demand_sum += float(vals[7])
    headroom_sum += float(vals[6])

  return capacity_sum, headroom_sum

def combinesubstationdata(nationalgrid, northernpower, ukpowernetworks, northwestelectric):
  northernpow_dict = {}
  nationalgrid_dict = {}
  ukpowernetworks_dict = {}
  northwestelectric_dict = {}

  #makes dict for nationalgrid
  for index, row in nationalgrid.iterrows():
    sub_type = row['Asset Type']
    if sub_type != 'Primary':
      continue
    sub_name = row['Substation Name']
    sub_number = row['Substation Number']
    lat = float(row['Latitude'])
    long = float(row['Longitude'])
    firm_capacity = float(row['Firm Capacity of Substation (MVA)'])
    demand_headroom = round(float(row['Demand Headroom (MVA)']),2)
    demand_peak = row['Measured Peak Demand (MVA)']
    demand_headroom_rag = str(row['Demand Headroom RAG']).upper()
    nationalgrid_dict[sub_name] = [sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "National Grid"]
  
  #makes dict for northernpow
  for index, row in northernpower.iterrows():
    sub_type = row['Substation Class']
    if sub_type != 'Primary':
      continue
    sub_name = row['Substation Name']
    sub_number = row['Substation ID']
    firm_capacity = row['Firm Capacity']
    demand_peak = row['Maximum Demand (MVA)']
    try: 
      demand_headroom = round(float(firm_capacity) - float(demand_peak),2)
    except: 
      demand_headroom = 0
    demand_headroom_rag = row['Demand Classification'].upper()
    lat = float(row['lat'])
    long = float(row['long'])
    northernpow_dict[sub_name] = [sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "Northern Power"]
  
  #make dict for ukpowernetworks
  for index, row in ukpowernetworks.iterrows():
    sub_name = row['PrimarySubstationName']
    sub_number = row['PrimaryAlias']
    sub_type = 'Primary'
    if row['SeasonOfConstraint'] == 'Winter':
      try:
        firm_capacity = float(row['FirmCapacityWinter'])
      except:
        firm_capacity = 0
    elif row['SeasonOfConstraint'] == 'Summer':
      try:
        firm_capacity = float(row['FirmCapacitySummer'])
      except:
        firm_capacity = 0
    else:
      try:
        firm_capacity = float(row['FirmCapacityWinter'])
      except:
        firm_capacity = 0

    try:
      demand_headroom = round(firm_capacity * float(row['DemandHeadroom'][:-1]) / 100,2)
    except:
      demand_headroom = 0
    demand_peak = firm_capacity - demand_headroom  
    try:
      demand_headroom_rag = str(row['DemandRAG']).split(" ")[0].upper()
      if demand_headroom_rag == 'YELLOW':
        demand_headroom_rag = 'AMBER'
    except:
      demand_headroom_rag = "NA"
    lat = float(row['Geo Point'].split(',')[0])
    long = float(row['Geo Point'].split(',')[1])
    ukpowernetworks_dict[sub_name] = [sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "UK Power Networks"]

  #make dict for northwestelec
  for index, row in northwestelectric.iterrows():
    sub_name = row['Primary Substation']
    sub_number = 'na'
    sub_type = 'Primary'
    firm_capacity = 0.1
    demand_headroom = float(row['Demand Headroom (MW)'])
    if demand_headroom == 0:
      demand_headroom_rag = 'RED'
    elif demand_headroom < 2:
      demand_headroom_rag = 'AMBER'
    else:
      demand_headroom_rag = 'GREEN'
    (lat, long) = OSGB36toWGS84(float(row['Easting']), float(row['Northing']))
    demand_peak = round(firm_capacity - demand_headroom,2)
    northwestelectric_dict[sub_name] = [sub_name, sub_number, sub_type, lat, long, firm_capacity, demand_headroom, demand_peak, demand_headroom_rag, "Electricity North West"]
  
  combined_dict = nationalgrid_dict.copy()

  combined_dict.update(northernpow_dict)
  combined_dict.update(ukpowernetworks_dict)
  combined_dict.update(northwestelectric_dict)
  combo_df = pd.DataFrame.from_dict(combined_dict, orient='index', columns=['Substation Name', 'ID', 'Type', 'Latitude', 'Longitude', 'Firm Capacity (MVA)', 'Demand Headroom (MVA)', 'Demand Peak (MVA)', 'Demand Headroom RAG', 'DNO'])

  return combo_df, combined_dict

  


