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