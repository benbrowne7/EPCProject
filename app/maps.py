
import mpld3
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
import numpy as np

def map1():
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  file1 = sourcedir + "/data/ratingcoord.csv"
  df1 = pd.read_csv(file1)
  lats = df1["LAT"].values.tolist()
  longs = df1["LONG"].values.tolist()
  means = df1["MEANRATING"].values.tolist()
  names = df1["NAME"].values.tolist()
  constitid = df1["CONSTIT"].values.tolist()
  n = len(means)

  fig, ax = plt.subplots(figsize=(6,6))
  labels = []

  for i in range(0,n):
    constit = names[i]
    rating = means[i]
    labels.append("{}: {}".format(constit, rating))


  ax.set_title("Av. EPC Rating by Constituency", fontsize=20)
  scatter = ax.scatter(longs,lats, c=means, cmap="inferno", s=20)
  #ax.colorbar(label="mean rating")
  ax.set_xlabel("Latitude", fontsize=15)
  ax.set_ylabel("Longitude", fontsize=15)
  
  fig.colorbar(scatter, ax=ax)

  position = mpld3.plugins.MousePosition()
  mpld3.plugins.connect(fig,position)

  tooltip = mpld3.plugins.PointHTMLTooltip(scatter, labels=labels, css='.mpld3-tooltip{color:green; font: 15px Arial, sans-serif}')
  mpld3.plugins.connect(fig, tooltip)


  html_str = mpld3.fig_to_html(fig)

  Html_file = open("./app/templates/map1.html", mode = "w")
  Html_file.write(html_str)
  Html_file.close()

def mapepctrend(ons):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  filename = sourcedir + "/data/EPCByYear/" + ons + "-yoy.csv"

  if os.path.isfile(sourcedir + "/templates/maps/epc_" + ons + "_trend.html"):
    return True

  df = pd.read_csv(filename)
  years = df['date'].values.tolist()
  years = [str(x) for x in years]
  rating = df['average_rating'].values.tolist()

  print(years)

  fig = plt.figure(figsize=(4,4))
  fig.patch.set_facecolor("black")
  fig.patch.set_alpha(1)
  ax = fig.add_subplot(111)
  line = ax.plot(years, rating)
  

  ax.set_title("Trends in EPC for {}".format(ons), fontsize=16, color="white")
  ax.set_xlabel("Year", fontsize=10, color="white")
  ax.set_ylabel("Av. EPC Rating", fontsize=10, color="white")
  ax.spines['bottom'].set_color('white')
  ax.spines['left'].set_color('white')
  ax.tick_params(axis='both', which='major', labelsize=8, colors='white')
  ax.set_xticklabels(years)
  ax.xaxis.label.set_color('white')
  ax.yaxis.label.set_color('white')
  ax.set_facecolor('black')

  labels = []
  for ind, row in df.iterrows():
    labels.append(str(row['date']) + ": " + str(row['average_rating']))

  tooltip = mpld3.plugins.PointHTMLTooltip(line[0], labels=labels, css='.mpld3-tooltip{color:green; font: 15px Arial, sans-serif}')
  mpld3.plugins.connect(fig, tooltip)

  html_str = mpld3.fig_to_html(fig)

  Html_file = open(sourcedir + "/templates/maps/epc_" + ons + "_trend.html", mode = "w")
  Html_file.write(html_str)
  Html_file.close()

def mapepcyoy(ons):
  abspath = os.path.abspath(__file__)
  sourcedir = os.path.dirname(abspath)

  if os.path.isfile(sourcedir + "/templates/maps/epc_" + ons + "_yoy.html"):
    return True
  
  file = sourcedir + "/data/EPCByYear/" + ons + "-yoy.csv"
  df = pd.read_csv(file)
  years = df['date'].values.tolist()
  years = [str(x) for x in years]
  rating = df['y/y'].values.tolist()
  rating = [round(x,1) for x in rating]

  min_y = int(math.floor(min(rating)))
  max_y = int(math.ceil(max(rating)))

  fig, ax = plt.subplots(figsize=(4,4))
  
  ax.set_title("% Y/Y Change in EPC {}".format(ons), fontsize=16, color="white")
  ax.set_xlabel("Year", fontsize=10, color="white")
  ax.set_ylabel("'%'Y/Y Change", fontsize=10, color="white")
  ax.set_yticks(np.arange(min_y, max_y, 1))
  ax.spines['bottom'].set_color('white')
  ax.spines['left'].set_color('white')
  ax.tick_params(axis='both', which='major', labelsize=8, colors='white')
  ax.set_xticklabels(years)
  ax.xaxis.label.set_color('white')
  ax.yaxis.label.set_color('white')
  ax.set_facecolor('black')
  line = ax.plot(years, rating)
  ax.axhline(y=0, xmin=-1, color='white', linestyle='--')
  

  labels = []
  for ind, row in df.iterrows():
    labels.append(str(row['date']) + ": " + str(row['y/y']))

  tooltip = mpld3.plugins.PointHTMLTooltip(line[0], labels=labels, css='.mpld3-tooltip{color:green; font: 15px Arial, sans-serif}')
  mpld3.plugins.connect(fig, tooltip)

  html_str = mpld3.fig_to_html(fig)

  Html_file = open(sourcedir + "/templates/maps/epc_" + ons + "_yoy.html", mode = "w")
  Html_file.write(html_str)
  Html_file.close()


mapepctrend('E06000014')
