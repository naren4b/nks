# Setting up your Own PKI with OpenSSL

![misc-open-ssl](https://user-images.githubusercontent.com/3488520/216543035-7dfd337c-34fd-4210-897f-97f99b843ae9.jpg)

# Generate ca.key and ca.crt

```
CA_NAME="NKS Certificate Authority"
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=${CA_NAME}" -days 10000 -out ca.crt
```

![image](https://user-images.githubusercontent.com/3488520/215917544-6589747a-0787-4d88-8fa0-f7bf696fe30e.png)

# Prepare the csr.conf (Repeat for each Certificate Name CN)

```
CERT_NAME="My Server/Client"
NODE_IP=127.0.0.1
DOMAIN=nks.in

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
keyUsage=keyEncipherment,dataEncipherment,digitalSignature,nonRepudiation
extendedKeyUsage=serverAuth,clientAuth
subjectAltName=@alt_names
EOF
```

# Generate tls Key & tls crt

```
openssl genrsa -out tls.key 2048
openssl req -new -key tls.key -out tls.csr -config csr.conf
openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key     -CAcreateserial -out tls.crt -days 10000     -extensions v3_ext -extfile csr.conf -sha256
```

![image](https://user-images.githubusercontent.com/3488520/215917579-ba038caf-b827-4998-beaa-664c893ffd61.png)

# View the certificate

```
openssl req  -noout -text -in ./tls.csr
openssl x509  -noout -text -in ./tls.crt
```

![image](https://user-images.githubusercontent.com/3488520/215917656-ffb4f441-5a79-4e2c-8770-a90779d70fe0.png)

# Distribution

```
NAME=$1 # Name of the Server or client Certificate
cat tls.crt ca.crt > $NAME.crt
mv tls.key $NAME.key
rm tls.*

```
