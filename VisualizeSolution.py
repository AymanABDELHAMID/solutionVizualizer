import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

# parameters pandas
pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

# path
inputDirectory = "./data/"
outputDirectory = "./output/"

# 1. entrer des données :
solution = pd.read_csv(inputDirectory+"instance_output.txt", sep=';')
delivery = pd.read_csv(inputDirectory+"vrp_deliveries.csv", sep=';')


# 2. Merge solution and delivery to get x and y coordinates
## Jointure
solution = pd.merge(solution, delivery, how='left', left_on=["location_id"], right_on = ["location_id"], indicator='Exist')
print("Dimension de la table après jointure : {}".format(solution.shape))

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame(solution, geometry=gpd.points_from_xy(solution['x'], solution['y']))

gdf.head()

# Sort and group points to make lines
#line_gdf = gdf.sort_values(by=['vehicle_id'])['geometry'].apply(lambda x: LineString(x.tolist()))
gdf = gdf[["vehicle_id", "activity_index", "x", "y", "geometry"]]
line_gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
# vehicle_id
line_gdf.head()

line_gdf.plot()

# Write out
line_gdf.to_file(outputDirectory + "lines.shp")