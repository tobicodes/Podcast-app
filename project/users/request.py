import requests

res = requests.get('https://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/genres', params={'id': 26})
## makes a query string and makes request to get all data for podcasts

res.json()