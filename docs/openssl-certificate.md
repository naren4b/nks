# Setting up your Own PKI with OpenSSL
```
CA_NAME="NKS Certificate Authority"
CERT_NAME="Dummy Server"
NODE_IP=127.0.0.1
DOMAIN=nks.in
```

# Prepare the csr.conf

```
cat<< EOF >csr.conf
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = IN
ST = Karnataka
L = Bangalore
O = Naren4Biz
OU = nks
CN = $CERT_NAME

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = kubernetes
DNS.2 = kubernetes.default
DNS.3 = kubernetes.default.svc
DNS.4 = kubernetes.default.svc.cluster
DNS.5 = kubernetes.default.svc.cluster.local
DNS.6 = *.$NODE_IP.nip.io
DNS.7 = $DOMAIN
DNS.8 = *.$DOMAIN
IP.1 = $NODE_IP


[ v3_ext ]
authorityKeyIdentifier=keyid,issuer:always
basicConstraints=CA:FALSE
keyUsage=keyEncipherment,dataEncipherment
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF
```

# Generate ca.key and ca.crt
```
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=${CA_NAME}" -days 10000 -out ca.crt
```
![image](https://user-images.githubusercontent.com/3488520/215917544-6589747a-0787-4d88-8fa0-f7bf696fe30e.png)

# Generate Server Key & Server crt
```
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -config csr.conf
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key     -CAcreateserial -out server.crt -days 10000     -extensions v3_ext -extfile csr.conf -sha256
```
![image](https://user-images.githubusercontent.com/3488520/215917579-ba038caf-b827-4998-beaa-664c893ffd61.png)

# View the certificate
```
openssl req  -noout -text -in ./server.csr
openssl x509  -noout -text -in ./server.crt
```
![image](https://user-images.githubusercontent.com/3488520/215917656-ffb4f441-5a79-4e2c-8770-a90779d70fe0.png)



