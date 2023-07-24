import requests
import json
import yaml
import argparse
import sys
import datetime
from datetime import datetime, timezone
from OpenSSL import crypto

parser = argparse.ArgumentParser(
    prog='Aruba Clearpass Certificate Updater',
    description='This program is designed to update certificates on aruba clearpass servers'
)

parser.add_argument('-config', type=str, help="The file location of the configuration YAML. Ex: -config='./config.yaml")
parser.add_argument('-t', action='store_true', help="This will enable a function to verify weather the cluster's \
                    certificate is coming up on renewal, and that the target certificate is valid for replacement.")

args = parser.parse_args()
config = ""

with open(args.config, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except:
        print(exc)

print(config)

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


    if args.t == True:
        ControllerCertExpiration = (requests.get((cluster["baseURL"]), headers=Header, verify=False)).headers["Expires"]
        NewCertificate = requests.get(CertLocation["pkcs12_file_url"], headers=Header, verify=False)
        
        chunks = []

        for chunk in NewCertificate.iter_content(chunk_size=4096):
            chunks.append(chunk)

        RawCert = b''.join(chunks)
        ActualCert = crypto.load_pkcs12(RawCert, bytes(CertLocation["pkcs12_passphrase"], "utf-8"))

        timestamp = ActualCert.get_certificate().get_notAfter()

        timestamp = bytes.decode(timestamp, "utf-8")

        newCerTS = datetime.strptime(timestamp, '%Y%m%d%H%M%S%z')
        curCertTS = datetime.strptime(ControllerCertExpiration, "%a, %d %b %Y %H:%M:%S %Z")
        curCertTS = curCertTS.replace(tzinfo=timezone.utc)


        CertTimeDelta = newCerTS - curCertTS
        CurrentTimeDelta = curCertTS - (datetime.now().astimezone(timezone.utc))


        if CurrentTimeDelta.days >= 25 and CertTimeDelta.days <= 0:
            next()


    
    Data = json.dumps(Data)
    jsonCertLocation = json.dumps(CertLocation)

    access_token = ((requests.post((cluster["baseURL"] + "/api/oauth"), data=Data, verify=False, headers=Header)).json())["access_token"]

    Header["Authorization"] = "Bearer " + access_token

    servers = (requests.get((cluster["baseURL"] + "/api/cluster/server"), headers=Header, verify=False)).json()
    servers = servers["_embedded"]


    for server in servers["items"]:
        uuid = server["server_uuid"]

        ServerEndpoint = (cluster["baseURL"]+"/api/server-cert/name/%s/HTTPS(ECC)"%uuid)

        sendCertificate = requests.put(url=ServerEndpoint, headers=Header, data=jsonCertLocation, verify=False)

        