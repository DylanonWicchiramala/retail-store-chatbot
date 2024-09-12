import os
import requests
import utils
from langchain_core.tools import tool

utils.load_env()


def find_place_from_text(input_text, location=None, radius=2000):
    "Finds a place based on text input and location bias."
    # Retrieve the API key from environment variables
    api_key = os.getenv('GPLACES_API_KEY')

    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

    # Define the endpoint URL
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

    # Define the parameters for the request
    params = {
        'fields': 'formatted_address,name,rating,opening_hours,geometry',
        'input': input_text,
        'inputtype': 'textquery',
        'key': api_key
    }
    
    params['locationbias'] = f'circle:{radius}@{location}' if location is not None and radius is not None else None

    # Make the request to the Google Maps API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return the JSON response
    else:
        response.raise_for_status()  # Raise an exception for HTTP errors


def find_location(input_text:str, location:str=None, radius=2000):
    """Returns the latitude and longitude of a location based on text input."""
    # Call the find_place_from_text function to get the location data
    data = find_place_from_text(input_text, location, radius)

    # Extract the latitude and longitude from the response
    candidates = data.get('candidates', [])
    if len(candidates)==0:
        raise ValueError("No location found.")

    # Assuming we're taking the first candidate
    geometry = candidates[0].get('geometry', {})
    location = geometry.get('location', {})

    latitude = location.get('lat')
    longitude = location.get('lng')

    if latitude is None or longitude is None:
        raise ValueError("Latitude or Longitude not found in the response.")

    # Return the latitude and longitude as a formatted string
    return f"{latitude},{longitude}"


def nearby_search_old(keyword:str, location:str, radius=2000, place_type=None):
    """Searches for nearby places based on a keyword and location."""
    # Retrieve the API key from environment variables
    api_key = os.getenv('GPLACES_API_KEY')

    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

    # Define the endpoint URL
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Set up the parameters for the request
    params = {
        'keyword': keyword,
        'location': location,
        'radius': radius,
        'type': place_type,
        'key': api_key,
    }

    # Send the GET request to the Google Maps API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Error with request: {response.status_code}, {response.text}")

    # Parse the JSON response
    data = response.json()

    # Return the response data
    return data['results']


def nearby_search(keyword:str, location:str, radius=2000, place_type=None):
    # Retrieve the API key from environment variables
    api_key = os.getenv('GPLACES_API_KEY')

    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

    # Define the endpoint URL
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Set up the parameters for the request
    params = {
        'keyword': keyword,
        'location': location,
        'radius': radius,
        'type': place_type,
        'key': api_key,
        "rankPreference": "DISTANCE"
    }

    # Send the GET request to the Google Maps API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Error with request: {response.status_code}, {response.text}")

    # Parse the JSON response
    data = response.json()
    results = data['results']

    # search into next page
    while data.get('next_page_token', False):
        params = {'next_page_token': data['next_page_token']}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Error with request: {response.status_code}, {response.text}")
        
        data = response.json()
        
        results.append(data['results'])
        

    # Return the response data
    return results


def nearby_dense_community(location:str, radius:int=1000):
    # Retrieve the API key from environment variables
    api_key = os.getenv('GPLACES_API_KEY')

    if not api_key:
        raise ValueError("API key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

    # Define the endpoint URL
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    # Set up the parameters for the request
    params = {
        "includedTypes": ["lodging", "mall", "school"],
        'location': location,
        'radius': radius,
        'key': api_key,
        "rankPreference": "DISTANCE"
    }

    # Send the GET request to the Google Maps API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Error with request: {response.status_code}, {response.text}")

    # Parse the JSON response
    data = response.json()
    results = data['results']

    # Return the response data
    return results