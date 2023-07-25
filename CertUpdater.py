import utils
import requests
import json
import argparse
import sys
import urllib3

#Clear's insecure connection warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Setup command line arguements

parser = argparse.ArgumentParser(
    prog='Aruba Clearpass Certificate Updater',
    description='This program is designed to update certificates on aruba clearpass servers'
)

parser.add_argument('-config', type=str, help="The file location of the configuration YAML. Ex: -config='./config.yaml")
parser.add_argument('-t', action='store_true', help="This will enable a function to verify weather the cluster's \
                    certificate is coming up on renewal, and that the target certificate is valid for replacement.")

args = parser.parse_args()

#Import YAML and check to make sure theres actually a cluster to run against

config = utils.ImportYAML(args.config)

if len(config["clusters"]) == 0:
    sys.exit(1)

#Begin parsing through clusters

for cluster in config["clusters"].values():

    print("Working on cluster: %s",(list(cluster.keys())[0]))

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

    Data = json.dumps(Data)
    jsonCertLocation = json.dumps(CertLocation)

    if args.t == True:
        try:
            response = requests.get(cluster["BaseURL"], headers=Header, data=Data, verify=False)

            if utils.TestConnection(response) == False:
                raise Exception
            else:
                test = utils.TestCertificateExpiration(response, CertLocation, Header)

                if test == True:
                    print("The certificate will be updated")
                else:
                    print("The new certificate is not valid")
                    next()
        except:
            print("Error getting certificate information from the cluster URL")
    


    access_token = utils.GetAuthToken(cluster["BaseURL"], Data, Header)
    Header["Authorization"] = "Bearer " + access_token

    servers = utils.GetServers(cluster["BaseURL"], Header)

    for server in servers["items"]:
        uuid = server["server_uuid"]
        utils.UpdateServerCert(cluster["BaseURL"], uuid, Header, jsonCertLocation)