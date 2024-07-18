

webex_api_url = "https://webexapis.com/v1"

scheme, netloc, *_ = webex_api_url.replace('://', ' ').split()

print (scheme, netloc)