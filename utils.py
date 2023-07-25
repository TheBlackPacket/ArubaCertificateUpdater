import requests
import datetime
import yaml
import json
import sys
import urllib3
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import pkcs12


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ImportYAML(configPath: str) -> dict:
    config = []
    with open(configPath, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except:
            print(exc)
    return config


def TestSelfSignedCertificate() -> bool:
    return True

def TestCertificateExpiration(currentCert: requests.request, newCertData: dict, headers: dict) -> bool:
    
    try:
        NewCertificate = requests.get(newCertData["pkcs12_file_url"], headers=headers, verify=False)

        if TestConnection(NewCertificate) == False:
            raise Exception

    except:
        print("Error downloading PKCS12 file. Response: %s",NewCertificate.status_code)
        sys.exit()
        
    chunks = []

    for chunk in NewCertificate.iter_content(chunk_size=4096):
        chunks.append(chunk)

    RawCert = b''.join(chunks)

    try:
        ActualCert = pkcs12.load_key_and_certificates(RawCert, bytes(newCertData["pkcs12_passphrase"], "utf-8"))
    except:
        print("There was an issue converting the file into a pkcs12 file")
        return False

    timestamp = ActualCert.get_certificate().get_notAfter()

    timestamp = bytes.decode(timestamp, "utf-8")

    newCerTS = datetime.strptime(timestamp, '%Y%m%d%H%M%S%z')
    curCertTS = datetime.strptime((currentCert.header["Expires"]), "%a, %d %b %Y %H:%M:%S %Z")
    curCertTS = curCertTS.replace(tzinfo=timezone.utc)


    CertTimeDelta = newCerTS - curCertTS
    CurrentTimeDelta = curCertTS - (datetime.now().astimezone(timezone.utc))


    if CurrentTimeDelta.days >= 25 and CertTimeDelta.days <= 0:
        return False
    else:
        return True



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
        print("There was an error updating the cert for UUID: %s",uuid)
        return False


def TestConnection(req: requests.Response) -> bool:
    if req.status_code == 200:
        return True
    else:
        return False