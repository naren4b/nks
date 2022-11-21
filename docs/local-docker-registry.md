
# Setting up a secured local registry (local docker or k8s kind cluster)
![https://raw.githubusercontent.com/docker-library/docs/b09c592af0d6061629e02e4f674d22848f8236e8/registry/logo.png](https://raw.githubusercontent.com/docker-library/docs/b09c592af0d6061629e02e4f674d22848f8236e8/registry/logo.png)
### Prepare the certs 
```
CURRENT_PATH=${PWD}
mkdir -p ${CURRENT_PATH}/registry/certs && cd "$_"
openssl req -x509 -newkey rsa:4096 -days 365 -nodes -sha256 \
            -keyout ${CURRENT_PATH}/registry/certs/tls.key \
            -out ${CURRENT_PATH}/registry/certs/tls.crt -subj "/CN=docker-registry" 
            -addext "subjectAltName = DNS:docker-registry" \
            
```
### Prepare the user credentials 
```
mkdir -p ${CURRENT_PATH}/registry/auth
read -p  "Enter User Name: " username
read -s -p "Enter Password: " password
echo ""
docker run --rm --entrypoint htpasswd registry:2.6.2 -Bbn ${username} ${password} > ${CURRENT_PATH}/registry/auth/htpasswd
ls ${CURRENT_PATH}/registry/auth/htpasswd
```

![image](https://user-images.githubusercontent.com/3488520/202599219-4e51c3ad-4d96-47e3-88c3-73c1cd1a0a07.png)

# To setup in docker 
```
docker run -d \
   -p 5000:5000 \
   --restart=always \
   --name docker-registry \
   -v ${CURRENT_PATH}/registry/auth:/auth \
   -e "REGISTRY_AUTH=htpasswd" \
   -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
   -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
   -v ${CURRENT_PATH}/registry/certs:/certs \
   -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/tls.crt \
   -e REGISTRY_HTTP_TLS_KEY=/certs/tls.key \
   registry:2.6.2

```
### Let's check the client part 
```
export REGISTRY_NAME="docker-registry"
export REGISTRY_IP="127.0.0.1"
echo '$REGISTRY_IP $REGISTRY_NAME' >> /etc/hosts
sudo mkdir -p /etc/docker/certs.d/docker-registry:5000
sudo cp ${CURRENT_PATH}/registry/certs/tls.crt /etc/docker/certs.d/docker-registry:5000/ca.crt
sudo docker login docker-registry:5000
```
![image](https://user-images.githubusercontent.com/3488520/202599108-3833f8d5-657f-4ac5-983b-2d9d14762cc9.png)


### Let's try some operation 
```
docker pull kennethreitz/httpbin
docker tag kennethreitz/httpbin docker-registry:5000/httpbin
docker push docker-registry:5000/httpbin
```
![image](https://user-images.githubusercontent.com/3488520/202599900-66372490-f2ed-4fd9-85d4-bcb28d401d69.png)
![image](https://user-images.githubusercontent.com/3488520/202600528-2e5ff735-ac30-40f2-ab7b-19a6ad3a15d8.png)


### Let's do some more images that needs to be pushed to local-registry
```
cat > images.txt <<EOF 
ghcr.io/siderolabs/flannel:v0.19.2
ghcr.io/siderolabs/install-cni:v1.2.0-2-gf14175f
docker.io/coredns/coredns:1.9.3
gcr.io/etcd-development/etcd:v3.5.5
k8s.gcr.io/kube-apiserver:v1.25.2
k8s.gcr.io/kube-controller-manager:v1.25.2
k8s.gcr.io/kube-scheduler:v1.25.2
k8s.gcr.io/kube-proxy:v1.25.2
ghcr.io/siderolabs/kubelet:v1.25.2
ghcr.io/siderolabs/installer:v1.2.5
k8s.gcr.io/pause:3.6
EOF
```
### Push the images 
```
for image in `cat images.txt`; do docker pull $image; done

for image in `cat images`; do \
    docker tag $image `echo $image | sed -E 's#^[^/]+/#docker-registry:5000/#'`; \
  done
  
for image in `cat images.txt`; do \
    docker push `echo $image | sed -E 's#^[^/]+/#docker-registry:6000/#'`; \
  done

```
### Check 
![image](https://user-images.githubusercontent.com/3488520/202604971-46e30bc5-27ac-4a22-81c5-4df7eb5a7d7d.png)



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
