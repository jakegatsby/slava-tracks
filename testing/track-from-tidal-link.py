#!/usr/bin/env python

import os
import sys
import base64
import requests

# Your TIDAL app credentials
CLIENT_ID = os.environ["TIDALCLIENTID"]
CLIENT_SECRET = os.environ["TIDALSECRET"]

# Base64-encode client credentials
def get_basic_auth_header(client_id, client_secret):
    credentials = f"{client_id}:{client_secret}"
    b64_credentials = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {b64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

# Step 1: Get access token
def get_access_token():
    url = "https://auth.tidal.com/v1/oauth2/token"
    data = {
        "grant_type": "client_credentials",  # No user login, just app-level access
        #"scope": "r_usr w_usr"  # Adjust scopes as needed
    }
    headers = get_basic_auth_header(CLIENT_ID, CLIENT_SECRET)
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

# Step 2: Use access token to get track info
def get_track_info(track_id, access_token, country_code='US'):
    url = f"https://openapi.tidal.com/v2/tracks/{track_id}?countryCode={country_code}"
    print(url)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    track_id = sys.argv[1]
    token = get_access_token()
    track_info = get_track_info(track_id, token)
    print(track_info)
    import pdb; pdb.set_trace()

    # Print track name and artist
    print("Track Name:", track_info["data"].get("title"))
    print("Artist:", track_info["artist"]["name"])
