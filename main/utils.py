# File containing all the helper functions.

import numpy as np # library to handle data in a vectorized manner
import pandas as pd # library for data analsysis
import json # library to handle JSON files
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
import geocoder # to get coordinates
import requests # library to handle requests
from bs4 import BeautifulSoup # library to parse HTML and XML documents
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors
# import k-means from clustering stage
from sklearn.cluster import KMeans
import folium # map rendering library
from math import radians, cos, sin, asin, sqrt 

def get_latlng(office, city):
	'''
	Function to get coordinates of an place in a city/state
	'''
	# initialize your variable to None
	lat_lng_coords = None
	# loop until you get the coordinates
	while(lat_lng_coords is None):
		g = geocoder.arcgis('{}, {}, India'.format(office, city))
		lat_lng_coords = g.latlng
	return lat_lng_coords

def distance(lat1, lat2, lon1, lon2):
    '''
    Function to calculate distance between two points on Earth
    '''
    # The math module contains a function named 
    # radians which converts from degrees to radians. 
    lon1 = radians(lon1) 
    lon2 = radians(lon2) 
    lat1 = radians(lat1) 
    lat2 = radians(lat2) 

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

    c = 2 * asin(sqrt(a)) 

    # Radius of earth in kilometers. Use 3956 for miles 
    r = 6371

    # calculate the result 
    return(c * r)