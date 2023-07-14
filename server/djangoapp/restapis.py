import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))


def get_request(url, api_key=None, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    print("GET REQUEST KWARGS********: ", kwargs)
    if (api_key):
        try:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        except:
            # If any error occurs
            print("Network exception occurred")
    else:
        # no authentication GET
        response = requests.get(url, params=kwargs)

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    requests.post(url, params=kwargs, json=json_payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    print("KWARGS-------", kwargs)
    if (kwargs):
        json_result = get_request(url, dealer_id=kwargs["dealer_id"])
    else:
        json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["result"]["docs"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            # dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []

    # - Call get_request() with specified arguments
    json_result = get_request(url, dealer_id=dealerId)

# - Parse JSON results into a DealerView object list
    if (json_result):
        reviews = json_result["data"]["docs"]

        for review_doc in reviews:
            # print(review_doc)
            review_obj = DealerReview(dealership=review_doc["dealership"], name=review_doc["name"],
                                      purchase=review_doc["purchase"], review=review_doc["review"],
                                      purchase_date=review_doc["purchase_date"], car_make=review_doc["car_make"],
                                      car_modal=review_doc["car_model"], car_year=review_doc["car_year"],
                                      sentiment=analyze_review_sentiments(
                                          text=review_doc["review"]),
                                      id=review_doc["_id"],)
            results.append(review_obj)
    for result in results:
        print("RESULT: ", result.sentiment)
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    api_key = "SUWdXfgU_mYmw6PnnjBOPowbbusMkReRx2c4O0H70PoC"
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/e886639e-c0e9-499e-a9c1-4de6616359cb"
    # params = dict()
    # params["text"] = kwargs["text"]
    # params["version"] = kwargs["version"]
    # params["features"] = kwargs["features"]
    # params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    # response = get_request(url=url, api_key=api_key, kwargs=params)

    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)

    natural_language_understanding.set_service_url(url)

    response = natural_language_understanding.analyze(
        text=text,
        features=Features(
            entities=EntitiesOptions(sentiment=True))).get_result()

    print("RESPONSE:  "+json.dumps(response))
    # print(response["entities"])

    for key, val in enumerate(response["entities"]):
        # print(key, ",", val)
        print(val["sentiment"]["label"])
        return (val["sentiment"]["label"])
