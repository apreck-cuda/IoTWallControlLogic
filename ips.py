import requests 
from requests.auth import HTTPBasicAuth

def main():
    url = "http://10.10.10.114:8080/rest/firewall/v1/forwarding-firewall/rules/dynamic/"  # Replace with your URL
    username = "api"
    password = "Demo-123"

    response = requests.get(url, auth=HTTPBasicAuth(username, password))

    if response.status_code == 200:
        json_data = response.json()
        print("JSON Response:")
        print(json_data)
    else:
        print("Request failed with status code:", response.status_code)

if __name__ == "__main__":
    main()