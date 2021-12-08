import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString
import folium
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import numpy as np

# parameters pandas
pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

# path
inputDirectory = "./data/Results/Solutions-electric/"
outputDirectory = "./output/"

# 1. entrer des données :
solution = pd.read_csv(inputDirectory+"instance_ouput_1.0.txt", sep=';')
delivery = pd.read_csv("./data/vrp_deliveries.csv", sep=';')


# 2. Merge solution and delivery to get x and y coordinates
## Jointure
delivery = delivery.drop_duplicates("location_id")
print("Dimension de la table avant jointure : {}".format(solution.shape))
solution = pd.merge(solution, delivery, how='left', left_on=["location_id"], right_on = ["location_id"])
print("Dimension de la table après jointure : {}".format(solution.shape))

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(solution, geometry=gpd.points_from_xy(solution['x'], solution['y']))

gdf.head()

# Sort and group points to make lines
gdf = gdf[["vehicle_id", "arrival_time", "x", "y", "geometry"]]
line_gdf = gdf.sort_values(by=['arrival_time']).groupby(['vehicle_id'])['geometry'].apply(lambda x: LineString(x.tolist()))
line_gdf = gpd.GeoDataFrame(line_gdf, geometry='geometry', crs = "EPSG:2154")
# vehicle_id
# line_gdf.head()

# line_gdf.plot()

# Write out
line_gdf.to_file(outputDirectory + "lines.shp")

# Creating a folium map
m = folium.Map(location=[45.742330364, 4.821996712], zoom_start=14, tiles='CartoDB positron')

## Getting the necessary data for the plot
#1. filter the data from dataframe
# I choose route 7
# df.loc[df['column_name'] == some_value]
route_SoC = solution.loc[solution['vehicle_id'] == 'vehicle_LEAD_7']
route_SoC = route_SoC['name', 'distance', 'SoC', 'SoC %', 'Maximum Range', 'Duration', 'Activity_counter']

#2. turn the dataframe into a .csv file
route_SoC.to_csv(outputDirectory+"route_SoC.csv", index=False, header=True, delimiter=";")

## Plotting the charging station

plt.rcParams['text.latex.preamble'] = '\\usepackage{lmodern}'
#Options
params = {'text.usetex': True,
          'font.size': 10,
          'font.family': 'lmodern'
          }
plt.rcParams.update(params)
fig, ax = plt.subplots(1, 2)
fig.set_size_inches(6, 3.5)
with cbook.get_sample_data(outputDirectory+'route_SoC.csv') as file:
    array = np.loadtxt(file, delimiter=";")
    ax[0].plot(array[:, 0], array[:, 1], label="SoC")
    ax[0].set_xlabel('Iteration', fontsize=10, fontname="Times New Roman")
    ax[0].set_ylabel('Average waiting time [s]', fontsize=10, fontname="Times New Roman")
    ax[0].legend(fontsize=10)
    ax[0].set_title("(a) Waiting times", fontsize=10, fontname="Times New Roman")
    ax[0].grid(visible=True, which="both")
fig.tight_layout()
plt.savefig("route_SoC.pdf")
plt.show()
