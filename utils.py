import requests
import datetime
import yaml
import json
import sys
import urllib3
import ssl
from datetime import datetime, timedelta
from cryptography import x509

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def ImportYAML(configPath: str) -> dict:
    config = []
    with open(configPath, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except:
            print(exc)
    return config

def TestSelfSignedCertificate(url: str) -> bool:
    serverCert = ssl.get_server_certificate((url.strip("https://"), 443))
    x509obj = x509.load_pem_x509_certificate(bytes(serverCert, 'utf-8'))

    if x509obj.issuer == x509obj.subject:
        return True
    else:
        return False

def TestCertificateExpiration(url: str) -> bool:
    serverCert = ssl.get_server_certificate((url.strip("https://"), 443))
    x509obj = x509.load_pem_x509_certificate(bytes(serverCert, 'utf-8'))
    CurrentTimeDelta = x509obj.not_valid_after - timedelta(days=30)

    return(CurrentTimeDelta < datetime.now())

def GetAuthToken(url: str, body: json, header: json) -> str:
    try:
        response = requests.post((url + "/api/oauth"), data=body, verify=False, headers=header)

        if TestConnection(response) == False:
            raise Exception
        else:
            return response.json()["access_token"]
    except:
        print("There was an issue getting the auth token. Please check the username and password in your config file")
        sys.exit()

def GetServers(url: str, headers: dict) -> dict:
    try:
        response = requests.get((url + "/api/cluster/server"), headers=headers, verify=False)
        if TestConnection(response) == False:
            raise Exception
        else:
            return (response.json())["_embedded"]
    except:
        print("Error getting servers from the cluster")

def UpdateServerCert(url: str, uuid: str, headers: dict, body: dict) -> bool:

    ServerEndpoint = (url+"/api/server-cert/name/%s/HTTPS(ECC)"%uuid)

    try:
        response = requests.put(url=ServerEndpoint, headers=headers, data=body, verify=False)

        if TestConnection(response) == False:
            raise Exception
        else:
            return True
    except:
        print("There was an error updating the cert for UUID:",uuid)
        return False

def TestConnection(req: requests.Response) -> bool:
    if req.status_code == 200:
        return True
    else:
        return False
