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

	offices = pd.read_csv('main/static/main/Companies.csv').values.tolist()
	kl_df = pd.DataFrame({"Neighborhood": offices})

	# call the function to get the coordinates, store in a new list using list comprehension
	coords = [get_latlng(neighborhood, city) for neighborhood in kl_df["Neighborhood"].tolist()]
	# create temporary dataframe to populate the coordinates into Latitude and Longitude
	df_coords = pd.DataFrame(coords, columns=['Latitude', 'Longitude'])
	# merge the coordinates into the original dataframe
	kl_df['Latitude'] = df_coords['Latitude']
	kl_df['Longitude'] = df_coords['Longitude']

	# get the coordinates of Kuala Lumpur
	address = city + ', India'

	connected = False

	while not connected:
		try:
			geolocator = Nominatim(user_agent="my-application")
			location = geolocator.geocode(address)
			latitude = location.latitude
			longitude = location.longitude
			print('The geograpical coordinate of {}, India is {}, {}.'.format(city, latitude, longitude))
			connected = True
		except:
			pass

	# create map of Toronto using latitude and longitude values
	map_kl = folium.Map(location=[latitude, longitude], zoom_start=12)

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
			fill_opacity=0.7).add_to(map_kl)

	# Render the HTML template with the data in the context variable
	return render(request, 'main/location.html', context=context)
