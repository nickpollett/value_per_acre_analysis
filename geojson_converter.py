import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

df = pd.read_csv(r"C:\Users\Nicholas Pollett\Downloads\n.csv")

df['area_acres'] = df['SHAPE.STArea()'] / 4046.86
df['tax_per_acre'] = df['tax_total'] / df['area_acres']

total_area = df['area_acres'].sum()
df['expense_allocation'] = df['area_acres'] / total_area * 21597263
df['expense_per_acre'] = df['expense_allocation'] / df['area_acres']

df['tax_expense_difference'] = df['tax_per_acre'] - df['expense_per_acre']

df['geometry'] = df['geometry_rings'].apply(lambda x: Polygon(eval(x)[0]))
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:26913")
gdf = gdf.to_crs("EPSG:4326")


gdf.to_file("vs.geojson", driver="GeoJSON")