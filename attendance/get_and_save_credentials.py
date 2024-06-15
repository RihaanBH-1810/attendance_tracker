import getpass
import json
import requests

def get_and_save_credentials():
    print("Enter your amFOSS CMS Username and Password.")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    shared_secret = input("Shared Secret: ")
    data = {"username": username, "password": password, 'shared_secret' : shared_secret}
    variables = json.dumps(data)
    url = 'http://labtrack.pythonanywhere.com/verify' #for testing purpose
    
    
    r = requests.post(url, json=data)
    response_json = r.json()
    print(response_json)
    if response_json['message'] == 'Invalid credentials':
        print("Try again, please enter valid credentials")
        get_and_save_credentials()
        
    else:
        # Saves username and password
        with open('.credentials', 'w') as file:
            json.dump(data, file)
            print("Successfully saved, please run this script whenever you change your credentials.")


if __name__ == '__main__':
    get_and_save_credentials()