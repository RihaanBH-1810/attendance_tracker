#run this file to test the mark attendance route
import hmac, hashlib
import requests

def generate_hmac(secret_key, message):
    secret_key_bytes = secret_key.encode('utf-8')
    message_bytes = message.encode('utf-8')
    hmac_digest = hmac.new(secret_key_bytes, message_bytes, hashlib.sha256)
    hmac_hex = hmac_digest.hexdigest()
    return hmac_hex

if __name__ == '__main__':
    secret_key = "" #put  your secret key here 
    message = "" #put a random message here
    username = "" #put your username here
    password = "" #put your password here

    hmac = generate_hmac(secret_key, message)
    data = {"username":username, "password": password, "message": message,"list": ["amFOSS_2192603", "amFOSS_906802"], "hmac" : hmac}
    r = requests.post('http://localhost:5000/mark_attendance', json = data)

    response_json = r.json()
    print(response_json)