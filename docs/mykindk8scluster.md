![IMG_E5385](https://github.com/naren4b/nks/assets/3488520/08e281f5-640e-4fe6-915d-6c11526b79b2)

# Create the Certificates

```bash
NAME=konark
CLUSTER_NAME=$NAME-cluster
HOST=$NAME.local.com
APP_NAME=$NAME-app
NAMESPACE=$NAME-demo
echo $CLUSTER_NAME, $HOST,$APP_NAME,$NAMESPACE

mkdir ${APP_NAME}
cd ${APP_NAME}

```

# Create KIND cluster

```bash
mkdir -p $NAME
cd $NAME
cat > ${CLUSTER_NAME}-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${CLUSTER_NAME}
nodes:
- role: control-plane
  image: kindest/node:v1.22.2
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
  - containerPort: 1024
    hostPort: 1024
- role: worker
  image: kindest/node:v1.22.2
- role: worker
  image: kindest/node:v1.22.2
- role: worker
  image: kindest/node:v1.22.2
EOF

kind create cluster --name ${CLUSTER_NAME} --config ${CLUSTER_NAME}-config.yaml

kubectl cluster-info --context kind-${CLUSTER_NAME}

kubectl label nodes ${CLUSTER_NAME}-control-plane ingress-ready="true"

```

# Deploy ingress controller

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl get pod -n ingress-nginx
```

# Deploy Storage class

```bash
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
# For tetsing
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pvc/pvc.yaml
kubectl create -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/examples/pod/pod.yaml
kubectl get pv
kubectl get pvc
kubectl exec volume-test -- sh -c "echo local-path-test > /data/test"
kubectl exec volume-test -- sh cat /data/test

ssh <kubernetes node ip>
$ ls /var/lib/rancher/k3s/storage/

```

# Build a sample application

```bash
# Create an index page

cat > index.html <<EOF
<!DOCTYPE html>
<html>
<body>
<img src="https://github.com/naren4b/nks/assets/3488520/08e281f5-640e-4fe6-915d-6c11526b79b2"  width="600" height="500">
</body>
</html>
EOF

# An Error Page

cat > error.html <<EOF
<!DOCTYPE html>
<html>
<body>
<p style="color:red;">You don't have access to this page at ${HOST} </p>
</body>
</html>
EOF

# Dockerfile to build the image

cat > Dockerfile <<EOF
FROM nginx:alpine
COPY . /usr/share/nginx/html
EOF

# Build the image and load into kind cluster

docker build -t ${APP_NAME}:0.0.1 .
kind load docker-image ${APP_NAME}:0.0.1 --name ${CLUSTER_NAME}

```

# Create k8s manifest files

```bash
# Create namespace

kubectl create ns ${NAMESPACE}

cat > ${APP_NAME}.yaml <<EOF
kind: Pod
apiVersion: v1
metadata:
  name: ${APP_NAME}
  labels:
    app: ${APP_NAME}
spec:
  containers:
  - name: ${APP_NAME}
    image: ${APP_NAME}:0.0.1
---
# Create Service
kind: Service
apiVersion: v1
metadata:
  name: ${APP_NAME}
spec:
  selector:
    app: ${APP_NAME}
  ports:
  - port: 80
---

# Create Ingress

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ${APP_NAME}
spec:
  rules:
  - host: ${HOST}
    http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: ${APP_NAME}
            port:
             number: 80
  tls:
  - hosts:
      - ${HOST}
    secretName: ${APP_NAME}-tls

EOF
```

# Apply the Manifest file

```bash
k create -f ${APP_NAME}.yaml -n ${NAMESPACE}

# Create the TLS Secret
cd ..
kubectl create secret generic ${APP_NAME}-tls --from-file=tls.crt=${HOST}.crt --from-file=tls.key=${HOST}.key --from-file=ca.crt=ca.crt -n ${NAMESPACE}

curl -ks https://$HOST

```

# Special Notes

```bash
echo "127.0.0.1 ${HOST}" >> /etc/hosts
for windows update the same line in "C:\Windows\System32\drivers\etc\hosts file"

```

# Create Certificates inside a container (Optional)

```bash
docker run -it --rm -e HOST=${HOST} -v ${HOME}:/root/ -v ${PWD}:/work -w /work --net host quay.io/jitesoft/alpine:3.17.1 sh
apk add openssl
openssl req -x509 -sha256 -newkey rsa:4096 -keyout ca.key -out ca.crt -days 356 -nodes -subj "/CN=${HOST} Cert Authority"
openssl req -new -newkey rsa:4096 -keyout ${HOST}.key -out ${HOST}.csr -nodes -subj "/CN=${HOST}"
openssl x509 -req -sha256 -days 365 -in ${HOST}.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out ${HOST}.crt
```

# Delete the cluster

```bash
kind delete clusters ${CLUSTER_NAME}

```
