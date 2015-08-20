# google-analytics-dataframes
pandas dataframe wrapper for the Google Analytics API.

Requires an OAuth 2.0 client auth secrets file, which is expected to be named csec.json and placed in the execution directory, i.e., ```path.dirname(__file__)```. About setting up access through OAuth 2.0: https://console.developers.google.com/project/coej/apiui/credential

(This depends on, and includes some of the demo code from, the google-api-python-client package.)
