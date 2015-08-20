# google-analytics-dataframes
pandas dataframe wrapper for the Google Analytics API.

Requires an OAuth 2.0 client auth secrets file, which is expected to be named csec.json and placed in the execution directory, i.e., ```path.dirname(__file__)```. About setting up access through OAuth 2.0:  
https://developers.google.com/api-client-library/python/start/get_started  
https://console.developers.google.com/project/_/apiui/credential

(This depends on, and includes some of the demo code from, the google-api-python-client package - https://github.com/google/google-api-python-client)
