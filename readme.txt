To run this, call python3 ./CertUpdater.py config.yaml

CertUpdater takes a single positional parameter for the path to a configuration yaml file.

The confiuration yaml should have all target server clusters under the clusters tag. Reference the included example yaml file for details. CertUpdater will go through each cluster listed in the yaml, get a list of all servers, then send a put request to each server uuid to grab a new pkcs12 cert from a url and update the servers cert.

This was thrown together in a couple of hours of hacking, so if theres any issues or features that need to be added, submit an issue to the github and i'll update it as soon as possible.

Goodluck.
