To run this, call python3 CertUpdater.py -config="config.yaml"

There are two parameters to use, one of which is mandatory
  -config="config.yaml" | Pass in a path to a configured YAML file. Reference the example YAML file to build your own.
  -t                    | This is the test flag. When passed, it will run a function to verify that the cluster's servers certificate is younger than the new certificate, and that the days from today to when the current certificate expires is less than 25. (Subject to change with further development)

The confiuration yaml should have all target server clusters under the clusters tag. Reference the included example yaml file for details. CertUpdater will go through each cluster listed in the yaml, get a list of all servers, then send a put request to each server uuid to grab a new pkcs12 cert from a url and update the servers cert.

This was thrown together in a couple of hours of hacking, so if theres any issues or features that need to be added, submit an issue to the github and i'll update it as soon as possible.

Goodluck.
