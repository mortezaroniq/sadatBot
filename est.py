
import requests

token = '8088475882:AAGHxr-2VZudZkunsgm3IDqaDiCucFV6L-4'
response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates')
print(response.json())
