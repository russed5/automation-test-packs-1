#!/bin/bash
set -x
curl --insecure https://tls-service.cpsd.dell:7001/tls-service/v1/pki/ca | sudo tee /usr/local/share/ca-certificates/cpsd.dell.ca.crt
sudo update-ca-certificates
curl -O --header "Content-Type: application/json" --request POST --data '{"common_name": "taf.cpsd.dell"}' https://tls-service.cpsd.dell:7001/tls-service/v1/pki/issue/bundle.tar.gz
sudo tar -zxvf bundle.tar.gz -C /usr/local/share/ca-certificates/
sudo update-ca-certificates