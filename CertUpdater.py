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

    print("Working on cluster: ",cluster["baseURL"])

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

        response = requests.get(cluster["baseURL"], verify=False)
        certificateTimeTest = False
        certificateSignTest = False

        if args.t == True:
            try:
                if utils.TestConnection(response) == False:
                    raise Exception
                else:
                    certificateTimeTest = utils.TestCertificateExpiration(cluster["baseURL"])

                    if certificateTimeTest == True:
                        print("The current certificate is close to expiration")
                    else:
                        print("The current certificate expires in more than 30 days")
            except:
                print("Error getting certificate information from the cluster URL")
        
            try:
                if utils.TestConnection(response) == False:
                    raise Exception
                else:
                    certificateSignTest = utils.TestSelfSignedCertificate(cluster["baseURL"])

                if certificateSignTest == True:
                    print("The certificate is self-signed")
                else:
                    print("The certificate is not self-signed")

            except:
                print("Error checking if the cluster certificate is self-signed")


        if certificateTimeTest == False and certificateSignTest == False:
            if (len(config) > 1):
                next()
            else:
                print("No more servers in cluster. Cert is up to date. Exiting...")
                sys.exit()
        else:
            print("Updating Certificate")


    access_token = utils.GetAuthToken(cluster["baseURL"], Data, Header)
    Header["Authorization"] = "Bearer " + access_token

    servers = utils.GetServers(cluster["baseURL"], Header)

    for server in servers["items"]:
        uuid = server["server_uuid"]
        print("Working on server: %s..."%uuid, end="")
        utils.UpdateServerCert(cluster["baseURL"], uuid=uuid, headers=Header, body=jsonCertLocation)
        print("complete.")
    
    print("Cluster complete.")