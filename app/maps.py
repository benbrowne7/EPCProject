import mpld3
import pandas as pd
import matplotlib.pyplot as plt
import os

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

  fig, ax = plt.subplots(figsize=(10,8))
  labels = []

  for i in range(0,n):
    constit = names[i]
    rating = means[i]
    labels.append("{}: {}".format(constit, rating))


  ax.set_title("Av. EPC Rating by Constituency", fontsize=40)
  scatter = ax.scatter(longs,lats, c=means, cmap="inferno", s=20)
  #ax.colorbar(label="mean rating")
  ax.set_xlabel("Latitude", fontsize=20)
  ax.set_ylabel("Logitude", fontsize=20)
  
  fig.colorbar(scatter, ax=ax)

  position = mpld3.plugins.MousePosition()
  mpld3.plugins.connect(fig,position)

  tooltip = mpld3.plugins.PointHTMLTooltip(scatter, labels=labels, css='.mpld3-tooltip{color:green; font: 15px Arial, sans-serif}')
  mpld3.plugins.connect(fig, tooltip)


  html_str = mpld3.fig_to_html(fig, figid='map1')

  html_doc = f'''
  <style type="text/css">
  div#map1 {{text-align: left}}
  </style>

  {html_str}
  '''

  Html_file = open("./app/templates/map1.html", "w")
  Html_file.write(html_str)
  print("updated")
  Html_file.close()
    

