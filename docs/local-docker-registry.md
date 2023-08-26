# Setting up a secured local registry (local docker or k8s kind cluster)

![https://raw.githubusercontent.com/docker-library/docs/b09c592af0d6061629e02e4f674d22848f8236e8/registry/logo.png](https://raw.githubusercontent.com/docker-library/docs/b09c592af0d6061629e02e4f674d22848f8236e8/registry/logo.png)

### Prepare the certs

```
REGISTRY_URL=registry.nks.local

rm -rf registry/
CURRENT_PATH=${PWD}
mkdir -p ${CURRENT_PATH}/registry/certs && cd "$_"
openssl req -x509 -newkey rsa:4096 -days 365 -nodes -sha256             -keyout ${CURRENT_PATH}/registry/certs/tls.key             -out ${CURRENT_PATH}/registry/certs/tls.crt -subj "/CN=$REGISTRY_URL"             -addext "subjectAltName = DNS:$REGISTRY_URL"
cd ..



```

### Prepare the user credentials

```
mkdir auth
docker run \
  --entrypoint htpasswd \
  httpd:2 -Bbn testuser testpassword > auth/htpasswd

```

![image](https://user-images.githubusercontent.com/3488520/203063122-cd361841-b9f5-4c19-8f23-112ddc69a0ab.png)

# To setup in docker

```
docker run -d \
  --restart=always \
  --name registry \
  -v "$(pwd)"/certs:/certs \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/tls.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/tls.key \
  -v "$(pwd)"/auth:/auth \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  -p 443:443 \
  registry:2

# https://docs.docker.com/registry/insecure/#deploy-a-plain-http-registry


```

### Let's check the client part

```

mkdir -p /etc/docker/certs.d/$REGISTRY_URL
cp certs/tls.crt  /etc/docker/certs.d/$REGISTRY_URL/ca.crt
cp certs/tls.crt /usr/local/share/ca-certificates/$REGISTRY_URL.crt
echo "127.0.0.1 $REGISTRY_URL" >> /etc/hosts

echo $REGISTRY_URL
vi /etc/docker/daemon.json

{
  "insecure-registries" : ["registry.nks.local"]
}

systemctl restart docker
```

![image](https://user-images.githubusercontent.com/3488520/202599108-3833f8d5-657f-4ac5-983b-2d9d14762cc9.png)

### Let's try some operation

```
systemctl restart docker


docker pull alpine:3.14
docker tag alpine:3.14 $REGISTRY_URL/my-alpine:3.14

export REGISTRY_AUTH_USER=testuser
export REGISTRY_AUTH_PASSWORD=testpassword
docker login $REGISTRY_URL -u $REGISTRY_AUTH_USER -p $REGISTRY_AUTH_PASSWORD

docker push $REGISTRY_URL/my-alpine:3.14
docker pull $REGISTRY_URL/my-alpine:3.14

```

![image](https://user-images.githubusercontent.com/3488520/203063815-8f5806fa-9d6d-4d0c-afd7-48d8bdbadce0.png)
![image](https://user-images.githubusercontent.com/3488520/203063931-ce91496a-0b04-4cfa-9006-cb1419da50c7.png)

### Let's do some more images that needs to be pushed to local-registry

```
cat > images.txt <<EOF
ghcr.io/siderolabs/flannel:v0.19.2
EOF
```

### Push the images

```
for image in `cat images.txt`; do docker pull $image; done

for image in `cat images.txt`; do \
    docker tag $image `echo $image | sed -E 's#^[^/]+/#registry.nks.local/#'`; \
  done

for image in `cat images.txt`; do \
    docker push `echo $image | sed -E 's#^[^/]+/#registry.nks.local/#'`; \
  done

```

### Check

```
docker exec -it registry ls /var/lib/registry/docker/registry/v2/repositories
```

![image](https://user-images.githubusercontent.com/3488520/203064898-f1bd705c-bbe2-4e3e-8634-18efa489d893.png)

# Setuping up same in a kubernetes cluster (kind)

### Let's setup certficate and password for docker pod in k8s

```
kubectl create secret tls certs-secret --cert=${CURRENT_PATH}/registry/certs/tls.crt --key=${CURRENT_PATH}/registry/certs/tls.key
kubectl create secret tls certs-secret --cert=${CURRENT_PATH}/registry/certs/tls.crt --key=${CURRENT_PATH}/registry/certs/tls.key
kubectl create secret generic auth-secret --from-file=${CURRENT_PATH}/registry/auth/htpasswd
```

### Create the PV registry-pv.yaml

```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: docker-repo-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /tmp/repository
EOF
```

### Create your PVC registry-pvc.yaml

```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: docker-repo-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF
```

### Create the pod registry-pod.yaml

```
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: docker-registry-pod
  labels:
    app: registry
spec:
  containers:
  - name: registry
    image: registry:2.6.2
    volumeMounts:
    - name: repo-vol
      mountPath: "/var/lib/registry"
    - name: certs-vol
      mountPath: "/certs"
      readOnly: true
    - name: auth-vol
      mountPath: "/auth"
      readOnly: true
    env:
    - name: REGISTRY_AUTH
      value: "htpasswd"
    - name: REGISTRY_AUTH_HTPASSWD_REALM
      value: "Registry Realm"
    - name: REGISTRY_AUTH_HTPASSWD_PATH
      value: "/auth/htpasswd"
    - name: REGISTRY_HTTP_TLS_CERTIFICATE
      value: "/certs/tls.crt"
    - name: REGISTRY_HTTP_TLS_KEY
      value: "/certs/tls.key"
  volumes:
  - name: repo-vol
    persistentVolumeClaim:
      claimName: docker-repo-pvc
  - name: certs-vol
    secret:
      secretName: certs-secret
  - name: auth-vol
    secret:
      secretName: auth-secret
EOF
```

### Check the pod, service and files

```
kubectl get pod,svc
kubectl port-forward docker-registry-pod 5000 --address 0.0.0.0
```

![image](https://user-images.githubusercontent.com/3488520/202592241-d55698b5-c28b-4cb2-a4fe-02cb71a15096.png)

Demo at : https://killercoda.com/killer-shell-cks/scenario/container-namespaces-docker
