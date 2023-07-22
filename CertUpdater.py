import requests
import json
import yaml
import argparse
import sys

parser = argparse.ArgumentParser(
    prog='Aruba Clearpass Certificate Updater',
    description='This program is designed to update certificates on aruba clearpass servers'
)

parser.add_argument('yamlfile', type=str)

args = parser.parse_args()
config = ""


with open(args.yamlfile, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except:
        print(exc)


if len(config["clusters"]) == 0:
    sys.exit(1)

for cluster in config["clusters"].values():

    Data = {
        "grant_type": "password",
        "username": cluster["username"],
        "password": cluster["password"],
        "client_id": cluster["client_id"]
    }

    CertLocation = {
        "pkcs12_file_url": cluster["pkcs12_file_url"],
        "pkcs12_passphrase": cluster["pkcs12_passphrase"]
    }

    Header = {
        "content-type": "application/json"
    }


    print(Data)

    print(CertLocation)

    
    Data = json.dumps(Data)
    jsonCertLocation = json.dumps(CertLocation)

    access_token = ((requests.post((cluster["baseURL"] + "/api/oauth"), data=Data, verify=False, headers=Header)).json())["access_token"]

    Header["Authorization"] = "Bearer " + access_token

    servers = (requests.get((cluster["baseURL"] + "/api/cluster/server"), headers=Header, verify=False)).json()
    servers = servers["_embedded"]

    print(servers)


    for server in servers["items"]:
        uuid = server["server_uuid"]

        ServerEndpoint = (cluster["baseURL"]+"/api/server-cert/name/%s/HTTPS(ECC)"%uuid)

        sendCertificate = requests.put(url=ServerEndpoint, headers=Header, data=jsonCertLocation, verify=False)
