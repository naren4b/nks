# Emissary-ingress quick start in KIND Cluster (Windows)

![emissary](https://user-images.githubusercontent.com/3488520/212543711-92b75407-23ae-4e00-b448-b6f3c34361c6.jpg)

## Create KIND cluster

```
cat > emissary-ingress-kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  image: kindest/node:v1.23.12
  extraPortMappings:
  - containerPort: 443
    hostPort: 443
    listenAddress: "0.0.0.0"
  - containerPort: 80
    hostPort: 80
    listenAddress: "0.0.0.0"
EOF
kind create cluster --name emissary-ingress-k8s --config emissary-ingress-kind-config.yaml
kubectl get nodes -o wide
```

## Install emissary-ingress

```
# Add the Repo:
helm repo add datawire https://app.getambassador.io
helm repo update

# Create Namespace and Install:
kubectl create namespace emissary && \
kubectl apply -f https://app.getambassador.io/yaml/emissary/3.4.0/emissary-crds.yaml
kubectl wait --timeout=90s --for=condition=available deployment emissary-apiext -n emissary-system
helm install emissary-ingress --namespace emissary datawire/emissary-ingress --set daemonSet=true --set dnsPolicy=ClusterFirstWithHostNet --set hostNetwork=true --set agent.enabled=false --set security.podSecurityContext.runAsUser=0  && \
kubectl -n emissary wait --for condition=available --timeout=90s deploy -lapp.kubernetes.io/instance=emissary-ingress

```

## Install emissary-ingress Listener

```
kubectl apply -f - <<EOF
---
apiVersion: getambassador.io/v3alpha1
kind: Listener
metadata:
  name: emissary-ingress-https-listener
  namespace: emissary
spec:
  port: 443
  protocol: HTTPS
  securityModel: XFP
  hostBinding:
    namespace:
      from: ALL
---

apiVersion: getambassador.io/v3alpha1
kind: Listener
metadata:
  name: emissary-ingress-http-listener
  namespace: emissary
spec:
  port: 80
  protocol: HTTP
  securityModel: XFP
  hostBinding:
    namespace:
      from: ALL
EOF
```

## Install test Application `quickstart/qotm.yaml`

```
kubectl apply -f https://app.getambassador.io/yaml/v2-docs/3.4.0/quickstart/qotm.yaml
```

## Install emissary-ingress Host

```

kubectl apply -f - <<EOF
---
apiVersion: getambassador.io/v3alpha1
kind: Host
metadata:
  name: wildcard-host
spec:
  hostname: "*"
  acmeProvider:
    authority: none
  tlsSecret:
    name: tls-cert
EOF

```

## Install emissary-ingress Mapping

```
kubectl apply -f - <<EOF
---
apiVersion: getambassador.io/v3alpha1
kind: Mapping
metadata:
  name: quote-backend
spec:
  hostname: "*"
  prefix: /backend/
  service: quote
  docs:
    path: "/.ambassador-internal/openapi-docs"
EOF

```

## Test the http link

```
curl -i http://localhost/backend/
```

## Secure communication

#### Create the Certificate

```
#Linux
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -subj '/CN=ambassador-cert' -nodes

#Windows (git-bash)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -subj '//CN=ambassador-cert' -nodes

#Verifiy
ls *.pem

```

#### Create the TLS secret

```
kubectl create secret tls tls-cert --cert=cert.pem --key=key.pem
```

## Test the https link

```
curl -Lk https://localhost:8443/backend/
```

## Uninstall

```
kind delete cluster --name=emissary-ingress-k8s
```
