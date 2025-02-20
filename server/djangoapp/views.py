from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealer_reviews_from_cf, get_dealers_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')


# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:base')
        else:
            return redirect('djangoapp:base')

# Create a `logout_request` view to handle sign out request


def logout_request(request):
    logout(request)
    return redirect('djangoapp:base')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}

    if request.method == "GET":
        return render(request, 'djangoapp/registration.html')
    elif request.method == "POST":
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['fname']
        last_name = request.POST['lname']
        user_exist = False

        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")

        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect('djangoapp:base')
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the base page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/a2c9bdd2-c454-4b7d-bb66-97af8efc34cf/default/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        states = [dealer.st for dealer in dealerships]
        unique_states = list(set(states))
        context["unique_states"] = unique_states
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return (render(request, './base.html', context))


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/a2c9bdd2-c454-4b7d-bb66-97af8efc34cf/default/get-review"
        dealer_details = get_dealer_reviews_from_cf(url, dealer_id)
        context["dealer_details"] = dealer_details
        context["dealer_id"] = dealer_id
        return (render(request, 'djangoapp/dealer_details.html', context))


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/a2c9bdd2-c454-4b7d-bb66-97af8efc34cf/default/get-dealership"
        dealership = get_dealers_from_cf(url, dealer_id=dealer_id)
        context["dealership"] = dealership
        for dealer_name in dealership:
            context["dealer_name"] = dealer_name
        context["dealer_id"] = dealer_id
        if request.user.is_authenticated:
            print("User is authenticated")
        else:
            print("User is not authecticated")

        return (render(request, 'djangoapp/add_review.html', context))

    elif request.method == "POST":
        if request.user.is_authenticated:

            review = dict()
            review["dealership"] = request.POST["dealer_id"]
            review["review"] = request.POST["content"]
            review["purchase_date"] = request.POST["purchasedate"]
            review["purchase"] = False
            review["name"] = request.user.get_username()

            post_data = request.POST
            for key in post_data:
                if (key == "purchasecheck"):
                    review["purchase"] = True

            car = request.POST["car"].split("-")
            car_make = car[0]
            car_modal = car[1]
            car_year = car[2]

            review["car_make"] = car_make
            review["car_model"] = car_modal
            review["car_year"] = car_year

            url = "https://us-south.functions.appdomain.cloud/api/v1/web/a2c9bdd2-c454-4b7d-bb66-97af8efc34cf/default/post-review"
            try:
                post_request(url, review)
            except:
                print("\nAN ERROR OCCURED WHILE TRYING TO POST REQUEST\n")

            print("****REVIEWS*****", review)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)

    # if (request.user.is_authenticated()):
    #     review = dict()
    #     review["time"] = datetime.utcnow().isoformat()

    # else:
    #     return ("User is not authenticated")
