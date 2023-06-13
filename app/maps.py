
import mpld3
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import statistics
import numpy as np
import json
from bokeh.plotting import figure, show, save
from bokeh.io import show, output_file
from bokeh.io import curdoc
from bokeh.models import HoverTool
from bokeh.models import TabPanel, Tabs, ColumnDataSource, FixedTicker, GeoJSONDataSource, LinearColorMapper, ColorBar, FixedTicker, BasicTicker, FactorRange
from bokeh.models import Span
from bokeh.palettes import brewer
import geopandas as gpd
from bokeh.palettes import mpl
from bng_latlon import WGS84toOSGB36

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

  w = int(0.41 * w)
  h = int(0.8*h)

  curdoc().theme = "dark_minimal"

  geosource = GeoJSONDataSource(geojson = json_data)
  palette = mpl['Inferno'][10]
  color_mapper = LinearColorMapper(palette=palette, low = 50, high=70)
  hover = HoverTool(tooltips = [('LAD', '@LAD20NM'), ('ONS', '@LAD20CD'),('Av. EPC', '@epc_means')])
  tools = "pan,wheel_zoom,reset"
  color_bar = ColorBar(color_mapper=color_mapper, bar_line_color='black', major_tick_line_color='black', ticker=BasicTicker(desired_num_ticks=len(palette)+1))
  p1 = figure(title = 'Av. EPC by Local Authority District', toolbar_location = 'right', toolbar_sticky = False, tools = [tools, hover], active_scroll='wheel_zoom', width=w, height=h)
  p1.title.text_font_size = '18pt'
  p1.title.align = "center"
  p1.axis.visible = False
  p1.xgrid.grid_line_color = None
  p1.ygrid.grid_line_color = None#Add patch renderer to figure.
  p1.patches('xs','ys', source = geosource,fill_color = {'field' :'epc_means', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p1.add_layout(color_bar, 'below')
  tab1 = TabPanel(child=p1, title="EPC")


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
  tab2 = TabPanel(child=p2, title="HPR")

  os.chdir(sourcedir + "/templates/bigmap")
  output_file("constit_map.html")
  save(Tabs(tabs=[tab1,tab2], width=w))



def graph(ons,w,h):

  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)
  filename = sourcedir + "/data/EPCByYear/" + ons + "-yoy.csv"
  ons_str = str(ons)

  #if os.path.isfile(sourcedir + "/templates/maps/epc_" + ons + "_trend.html"):
  # return True

  df = pd.read_csv(filename)
  yoy = df['y/y'].values
  av_yoy = round(np.mean(yoy),1)
  dates = df['date'].values
  ratings = df['average_rating'].values
  dates = [int(x) for x in dates]
  ratings = [int(x) for x in ratings]

  w = int(0.535 * w)
  h = int(0.45*0.85*h)



  curdoc().theme = "dark_minimal"
  tools = "reset,save"
  hover = HoverTool(tooltips = [('EPC', '$y'), ('Year', '$x{0000}')], )
  p1 = figure(title="Average EPC", x_axis_label='Year', y_axis_label='EPC Rating', sizing_mode="stretch_width", toolbar_location = 'right', toolbar_sticky = False, tools = [tools, hover], width=w, height=h)
  p1.title.text_font_size = '16pt'
  p1.title.align = "center"
  p1.line(dates, ratings, line_width=4, legend_label=ons_str)
  p1.legend.location = "bottom_right"
  p1.legend.label_text_font_style = "bold"
  p1.legend.border_line_width = 3
  p1.legend.border_line_color = "black"
  tab1 = TabPanel(child=p1, title="EPC Trend")

  #-----------------------------------------------------------


  hover = HoverTool(tooltips = [('%Y/Y', '$y'), ('Year', '$x{0000}')], )
  p2 = figure(title="EPC %Y/Y", x_axis_label='Year', y_axis_label="% Change", sizing_mode="stretch_width", toolbar_location = 'right', toolbar_sticky = False, tools = [tools,hover], width=w, height=h)
  p2.title.text_font_size = '16pt'
  p2.title.align = "center"
  p2.line(dates, yoy, line_width=4, legend_label=ons_str)
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
    p3 = figure(x_range=years, title="Age Distribution of EPCs", toolbar_location=None, tools=[hover], width=w, height=h)
    p3.title.text_font_size = '16pt'
    p3.title.align = "center"
    p3.vbar(x='x', top='data', width=0.4, source=source)
    p3.xgrid.grid_line_color = None
    p3.y_range.start = 0
    tab3 = TabPanel(child=p3, title="Age Distribution")



  os.chdir(sourcedir + "/templates/graphs")
  name = ons + "_graph" ".html"
  output_file(name)
  save(Tabs(tabs=[tab1,tab2,tab3], width=w))

  return name, av_yoy, exp

def ladmap(ons,w,h):

  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  filename = sourcedir + "/data/constitbounds_data/" + ons + ".geojson"
  ons_str = str(ons)
  map = gpd.read_file(filename)
  filename = sourcedir + "/data/postcode_data/" + ons_str + "-postcode.csv"
  df = pd.read_csv(filename)

  lat_mean = np.mean(df['lat'].values)
  long_mean = np.mean(df['long'].values)
  lat_std = statistics.stdev(df['lat'].values)
  long_std = statistics.stdev(df['long'].values)
  inds = []
  for index, row in df.iterrows():
    lat = row['lat']
    long = row['long']
    if abs(lat-lat_mean) > 1.8*lat_std:
      inds.append(index)
    if abs(long-long_mean) > 1.8*long_std:
      if index not in inds:
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