# Setting up NKS PKI 
![nks-pki](https://github.com/naren4b/nks/assets/3488520/d4ba7496-fbc5-423a-a9ba-01a290a6685d)

### Let's have kubernetes cluster
```bash
curl https://raw.githubusercontent.com/naren4b/dotfiles/main/ws/install.sh | bash
```
### Ingress controller 
```
# Above Step does installs by default 
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl label nodes controlplane ingress-ready="true"
kubectl wait --for=condition=ready pod -n ingress-nginx -l app.kubernetes.io/component=controller
```
### Install cert-manager
```bash
helm repo add jetstack https://charts.jetstack.io --force-update
helm repo update
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.1/cert-manager.crds.yaml
helm install \
  cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.14.1
kubectl get pod -n cert-manager
```
![image](https://github.com/naren4b/nks/assets/3488520/c14f0768-63fe-46a3-9e46-82b31bfd59f1)


### Create your Root CA
```bash
CA_NAME="NKS Certificate Authority"
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -subj "/CN=${CA_NAME}" -days 10000 -out ca.crt

kubectl create secret tls nks-pki-tls --cert=ca.crt --key=ca.key -n cert-manager
```
### Install ClusterIssuer
```bash
cat<<EOF > nks-pki-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: nks-pki-issuer
spec:
  ca:
    secretName: nks-pki-tls
EOF

kubectl apply -f nks-pki-issuer.yaml
```
![image](https://github.com/naren4b/nks/assets/3488520/e2732275-cb31-4e2a-95c0-d024cf1d4279)



### Install Application and Certificates 
```bash
kubectl create deployment echoserver --image k8s.gcr.io/echoserver:1.10
kubectl expose deployment echoserver --port=8080
kubectl create ingress echoserver   --class=nginx   --rule="echoserver.127.0.0.1.nip.io/*=echoserver:8080,tls=echoserver-ingress-tls"
 
cat<<EOF > echoserver-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name:  echoserver-certificate
spec:
  isCA: false
  duration: 2160h # 90d
  renewBefore: 360h # 15d
  commonName: echoserver.127.0.0.1.nip.io
  dnsNames:
  - echoserver.127.0.0.1.nip.io
  - www.echoserver.127.0.0.1.nip.io
  secretName: echoserver-ingress-tls
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
  issuerRef:
    name: nks-pki-issuer
    kind: ClusterIssuer
    group: cert-manager.io
EOF
kubectl apply -f echoserver-certificate.yaml
```
![image](https://github.com/naren4b/nks/assets/3488520/75d10254-94fd-4b4c-bcb1-84f913173720)


### Test the certificate 
```
sudo openssl s_client -connect echoserver.127.0.0.1.nip.io:443 -showcerts </dev/null 
```
![image](https://github.com/naren4b/nks/assets/3488520/a3acbcca-a973-426a-84c6-853dfe55bc38)

- Demo Environment: https://killercoda.com/playgrounds/scenario/kubernetes





