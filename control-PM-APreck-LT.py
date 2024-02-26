import subprocess
import requests 
import time
from requests.auth import HTTPBasicAuth
controlIP = "10.0.8.254:3333"
dynRule = "lists/Remote/MaintenanceAccess"
stopRule = "MaintanceAccess-KUKA1"
fwIP = "localhost"

def ioControl(color, state):
    try:
        if color == "red":
            url = "http://" + controlIP + "/out1/" + str(state)
            requests.post(url,timeout=2)
            print("RED is "+ state)
        elif color == "yellow":
            url = "http://" + controlIP + "/out2/" + str(state)
            requests.post(url,timeout=2)
            print("Yellow is "+ state)
        elif color == "green":
            url = "http://" + controlIP + "/out3/" + str(state)
            requests.post(url,timeout=2)
            print("Green is "+ state)
        elif color == "alarm":
            url = "http://" + controlIP + "/out4/" + str(state)
            requests.post(url,timeout=2)
            print("Alarm is "+ state)
        else:
            print("Invalid state, run error sequence")
            url = "http://" + controlIP + "/out1/" + "1"
            requests.post(url,timeout=2)
            time.sleep(2)
            url = "http://" + controlIP + "/out1/" + "0"
            requests.post(url,timeout=2)
            time.sleep(2)
            url = "http://" + controlIP + "/out2/" + "1"
            requests.post(url,timeout=2)
            time.sleep(2)
            url = "http://" + controlIP + "/out2/" + "0"
            requests.post(url)
            time.sleep(2)
            url = "http://" + controlIP + "/out3/" + "1"
            requests.post(url,timeout=2)
            time.sleep(2)
            url = "http://" + controlIP + "/out3/" + "0"
            requests.post(url,timeout=2)
    except Exception as e:
        print("An error occurred:", e)  

def remoteControl():
    try:
        url = "http://"+ fwIP +":8080/rest/firewall/v1/forwarding-firewall/rules/dynamic/" + dynRule  # Replace with your URL
        username = "api"
        password = "Demo-123"

            #{'action': 'none', 'expiresIn': 0, 'expireAction': 'none'}

        response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=5)

        if response.status_code == 200:
            json_data = response.json()
            ruleState = json_data['action']
            if ruleState == "enable":
                print("Remote Access Active")
                print(json_data)
                ioControl("yellow", "1")
            else:
                print("Remote Access disabled")
                ioControl("yellow", "0")

        else:
            print("Request failed with status code:", response.status_code)
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

def emergencyStop():

    try:
        url = "http://" + controlIP + "/in1"  # Replace with your URL
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            json_data = response.json()
            ioState = json_data['state']
            if ioState == 1:
                print("Emergency Stop Active")
                print("Activating Rule")
                urlRule = "http://" + fwIP + ":8080/rest/firewall/v1/forwarding-firewall/rules/dynamic/" + stopRule
                username = "api"
                password = "Demo-123"
                payload = {
                    "action": "enable",
                    "expiresIn": 0,
                    "expireAction": "disable"
                }
                responseRule = requests.post( urlRule, json=payload, auth=HTTPBasicAuth(username, password), timeout=5)
                print("Rule activated with code: " + responseRule)
                ioControl("red", "1")
                ioControl("yellow", "0")
                ioControl("green", "0")
            else:
                print("No Emergancy STOP detected - all good")
                ioControl("red", "0")
                ioControl("green", "1")
                print("Seaktivating Emergany Rule")
                urlRule = "https://" + fwIP + ":8080/rest/firewall/v1/forwarding-firewall/rules/dynamic/" + stopRule
                username = "api"
                password = "Demo-123"
                payload = {
                    "action": "disable",
                    "expiresIn": 0,
                    "expireAction": "disable"
                }
                responseRule = requests.post( urlRule, json=payload, auth=HTTPBasicAuth(username, password), timeout=5)
                print("Rule activated with code: " + responseRule)
        else:
            print("Request failed with status code:", response.status_code)
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.RequestException as e:
        print("Request error:", e)

def ipsHit():
    command = ["acpfctrl", "cache", "view", "scan", "|", "wc", "-l"]
    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  #acpfctrl cache view scan  -  on the firewall 
    ipsCountH = output.stdout.decode("utf-8").strip()
    ipsCount = len(ipsCountH)
    print (ipsCount)
    try:
        if int(ipsCount) >= 1:
            print("Threat deteced")
            ioControl("red", "1")
            urlRule = "http://" + fwIP + ":8080/rest/firewall/v1/forwarding-firewall/rules/dynamic/" + dynRule
            username = "api"
            password = "Demo-123"
            payload = {
                "action": "disable",
                "expiresIn": 0,
                "expireAction": "disable"
             }
            responseRule = requests.post( urlRule, json=payload, auth=HTTPBasicAuth(username, password), timeout=5)
            print("Remote Access deactivated with code: " + responseRule)
        else:
            print("All good, no threats found")
            ioControl("red", "0")
            ioControl("green", "1")

    except Exception as e:
        print("ipsHits throw an erroe:", e)

def main():
    try:
        ioControl("green",1)
        while True:
            remoteControl()    
            emergencyStop()
            ipsHit()
            time.sleep(2)
    except KeyboardInterrupt:
        print("FINISHED by key STROKE!!!!!")

if __name__ == "__main__":
    main()
