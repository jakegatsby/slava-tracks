import slavatracks

URLS = [
    "https://open.spotify.com/track/53o05J0uSWOedPwN4Z0oyo?si=XGAiSUelTOW6HTmHFkWn-A",
    "https://tidal.com/browse/track/370686004/u",
]

for url in URLS:
    data = {
        "streaming_link": url
    }
    slavatracks.track_from_request_data(data)