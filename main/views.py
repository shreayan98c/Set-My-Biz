from django.shortcuts import render, redirect
from django.http import HttpResponse
# from .models import Tutorial, TutorialCategory, TutorialSeries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm
from django.views import generic
from django.contrib.auth.models import User
from main.forms import NewUserForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .utils import *
import random

# Create your views here.

def index(request):
	"""View function for home page of site."""
	context = dict()
	# Render the HTML template index.html with the data in the context variable
	return render(request, 'main/index.html', context=context)

def register(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get("username")
			messages.success(request, f"Successfully created account: {username}")
			login(request, user)
			messages.info(request, f"You are now logged in as {username}")
			return redirect("main:index")
		else:
			for msg in form.error_messages:
				messages.error(request, f"{msg}: {form.error_messages[msg]}")

	form = NewUserForm
	return render(request,
				  "main/register.html",
				  context={"form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "Logged out successfully!")
	return redirect("main:index")

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if(form.is_valid()):
			username = form.cleaned_data.get("username")
			password = form.cleaned_data.get("password")
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}")
				return redirect("main:index")
			else:
				messages.error(request, "Invalid username or password")
		else:
			messages.error(request, "Invalid username or password")

	form = AuthenticationForm()
	return render(request,
				  "main/login.html",
				  {"form": form})

def business_input(request):
	"""View function to get business details from user."""
	context = dict()
	# Render the HTML template index.html with the data in the context variable
	return render(request, 'main/new_business.html', context=context)


class UserDetailView(generic.DetailView):
	model = User
	template_name = 'main/user_detail.html'


class UserUpdate(UpdateView):
	model = User
	fields = ['first_name', 'last_name']
	template_name = 'main/update_user.html'
	success_url = reverse_lazy('main:index')


def location(request):
	"""View function to display best place to set business."""
	city = request.POST.get("city")
	radius = request.POST.get("radius")
	context = dict()
	context['city'] = city
	context['radius'] = radius

	print('Entered location function')

	# offices = pd.read_csv('main/static/main/Companies.csv').values.tolist()
	offices = ['Amazon','Infosys','Dell','HP','Tech Mahindra','SAP','Samsung R&D','Accenture','Wipro','TCS', 'IBM', 'Cognizant','Capgemini','Cisco','Mindtree','HCL','Mu Sigma','Robert Bosch','Honeywell','CGI',	'Mphasis','EY','Deloitte','Nokia','Intel','Huawei','Goldman Sachs','Flipkart','KPMG','Zomato','Swiggy','HP']

	kl_df = pd.DataFrame({"Neighborhood": offices})

	print('Loaded the company list, now getting coordinates')

	# call the function to get the coordinates, store in a new list using list comprehension
	coords = [get_latlng(neighborhood, city) for neighborhood in kl_df["Neighborhood"].tolist()]
	# create temporary dataframe to populate the coordinates into Latitude and Longitude
	df_coords = pd.DataFrame(coords, columns=['Latitude', 'Longitude'])
	# merge the coordinates into the original dataframe
	kl_df['Latitude'] = df_coords['Latitude']
	kl_df['Longitude'] = df_coords['Longitude']

	print('Searching for city coordinates')
	
	# get the coordinates of Kuala Lumpur
	address = city + ', India'

	connected = False

	while not connected:
		try:
			geolocator = Nominatim(user_agent="my-application")
			location = geolocator.geocode(address)
			latitude = location.latitude
			longitude = location.longitude
			context['latitude'] = latitude
			context['longitude'] = longitude
			print('The geograpical coordinate of {}, India is {}, {}.'.format(city, latitude, longitude))
			connected = True
		except:
			pass

	# create map of Toronto using latitude and longitude values
	map_offices = folium.Map(location=[latitude, longitude], zoom_start=12)

	# add markers to map
	for lat, lng, neighborhood in zip(kl_df['Latitude'], kl_df['Longitude'], kl_df['Neighborhood']):
		label = '{}'.format(neighborhood)
		label = folium.Popup(label, parse_html=True)
		folium.CircleMarker(
			[lat, lng],
			radius=5,
			popup=label,
			color='blue',
			fill=True,
			fill_color='#3186cc',
			fill_opacity=0.7).add_to(map_offices)

	context['best_lat'] = kl_df['Latitude'].mean()
	context['best_long'] = kl_df['Longitude'].mean()

	context['place_1'] = random.choice(offices)
	context['place_2'] = random.choice(offices)
	context['place_3'] = random.choice(offices)

	map_offices.save('main/templates/main/map.html')
	context['map'] = map_offices._repr_html_()
	
	print('Plotting completed!')

	'''
	# define Foursquare Credentials and Version
	CLIENT_ID = '' # your Foursquare ID
	CLIENT_SECRET = '' # your Foursquare Secret
	VERSION = '20180605' # Foursquare API version

	radius = radius * 1000 # km to m
	LIMIT = 1

	venues = []

	for lat, long, neighborhood in zip(kl_df['Latitude'], kl_df['Longitude'], kl_df['Neighborhood']):
	    
		# create the API request URL
		url = "https://api.foursquare.com/v2/venues/explore?client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}&categoryId=4d4b7105d754a06374d81259".format(
			CLIENT_ID,
			CLIENT_SECRET,
			VERSION,
			lat,
			long,
			radius, 
			LIMIT)

		# make the GET request
		resp = requests.get(url)
		print(resp)
		results = resp.json()["response"]["groups"][0]["items"]

		# return only relevant information for each nearby venue
		for venue in results:
			venues.append((
				neighborhood,
				lat, 
				long, 
				venue['venue']['name'], 
				venue['venue']['location']['lat'], 
				venue['venue']['location']['lng'],  
				venue['venue']['categories'][0]['name']))

	# convert the venues list into a new DataFrame
	venues_df = pd.DataFrame(venues)

	# define the column names
	venues_df.columns = ['Neighborhood', 'Latitude', 'Longitude', 'VenueName', 'VenueLatitude', 'VenueLongitude', 'VenueCategory']

	context['venues_df'] = venues_df.to_html()

	context['unique'] = len(venues_df['VenueCategory'].unique())
	print('There are {} uniques categories.'.format(len(venues_df['VenueCategory'].unique())))

	print('Connected to Foursquare!')


	# one hot encoding
	kl_onehot = pd.get_dummies(venues_df[['VenueCategory']], prefix="", prefix_sep="")

	# add neighborhood column back to dataframe
	kl_onehot['Neighborhoods'] = venues_df['Neighborhood'] 

	# move neighborhood column to the first column
	fixed_columns = [kl_onehot.columns[-1]] + list(kl_onehot.columns[:-1])
	kl_onehot = kl_onehot[fixed_columns]

	kl_grouped = kl_onehot.groupby(["Neighborhoods"]).mean().reset_index()

	kl_mall = kl_grouped

	# set number of clusters
	kclusters = 10

	kl_clustering = kl_mall.drop(["Neighborhoods"], 1)

	# run k-means clustering
	kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(kl_clustering)

	# check cluster labels generated for each row in the dataframe
	kmeans.labels_[0:10] 

	# create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood.
	kl_merged = kl_mall.copy()

	# add clustering labels
	kl_merged["Cluster Labels"] = kmeans.labels_

	kl_merged.rename(columns={"Neighborhoods": "Neighborhood"}, inplace=True)

	# merge toronto_grouped with toronto_data to add latitude/longitude for each neighborhood
	kl_merged = kl_merged.join(kl_df.set_index("Neighborhood"), on="Neighborhood")

	# sort the results by Cluster Labels
	kl_merged.sort_values(["Cluster Labels"], inplace=True)
	
	# create map
	map_clusters = folium.Map(location=[latitude, longitude], zoom_start=12)

	# set color scheme for the clusters
	x = np.arange(kclusters)
	ys = [i+x+(i*x)**2 for i in range(kclusters)]
	colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
	rainbow = [colors.rgb2hex(i) for i in colors_array]

	# add markers to the map
	markers_colors = []
	for lat, lon, poi, cluster in zip(kl_merged['Latitude'], kl_merged['Longitude'], kl_merged['Neighborhood'], kl_merged['Cluster Labels']):
		label = folium.Popup(str(poi) + ' - Cluster ' + str(cluster), parse_html=True)
		folium.CircleMarker(
			[lat, lon],
			radius=5,
			popup=label,
			color=rainbow[cluster-1],
			fill=True,
			fill_color=rainbow[cluster-1],
			fill_opacity=0.7).add_to(map_clusters)
	       
	map_clusters.save('main/templates/main/map_clusters.html')
	context['map_clusters'] = map_clusters._repr_html_()

	cluster_id = []
	num_references = []
	center_latitude = []
	center_longitude = []
	for i in range(kclusters):
		cluster_id.append(i)
		num_references.append(kl_merged.loc[kl_merged['Cluster Labels'] == i].shape[0])
		center_latitude.append(kl_merged['Latitude'].loc[kl_merged['Cluster Labels'] == i].mean(axis=0))
		center_longitude.append(kl_merged['Longitude'].loc[kl_merged['Cluster Labels'] == i].mean(axis=0))
	
	pos = num_references.index(max(num_references))

	context['best_df'] = kl_merged.loc[kl_merged['Cluster Labels'] == pos].to_html()

	final_data = pd.DataFrame(list(zip(cluster_id, num_references, center_latitude, center_longitude)),
                         columns=['Cluster ID', 'Num. of Reference Points', 'Center Latitude', 'Center Longitude'])

	i=0
	for i in range(kclusters):
		temp_df = kl_merged.loc[kl_merged['Cluster Labels'] == i]
		lat = final_data['Center Latitude'][i]
		long = final_data['Center Longitude'][i]
		dist_list = []
		for j in range(len(temp_df)):
		    dist_list.append(distance(temp_df['Latitude'].iloc[j], lat, temp_df['Longitude'].iloc[j], long))
		temp_df['Distance from center'] = dist_list
		manhattan = sum(dist_list)
		ms=0
		for k in dist_list:
		    ms += k**2
		rms=sqrt(ms)
		comp = 2*len(dist_list)+1
		cluster_score_manhattan = manhattan/comp
		cluster_score_rms = rms/comp
		print('Cluster',i)
		print(temp_df[['Neighborhood', 'Cluster Labels', 'Latitude', 'Longitude', 'Distance from center']])
		print('Number of Competitors:', comp)
		print('Manhattan distance:', manhattan, '\tRMS distance:', rms)
		print(f'Cluster Score (Distance / Number of competitors):\nManhattan: {cluster_score_manhattan}\tRMS: {cluster_score_rms}')
		print('-------------------------------------------------------------------------------')
	'''

	# Render the HTML template with the data in the context variable
	return render(request, 'main/location.html', context=context)