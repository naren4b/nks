# Setting up Basic Harbor Registry in a Kubernetes Cluster 
![harbor](https://github.com/naren4b/nks/assets/3488520/b01ad8c0-c649-45d1-938c-6abc44760af1)

### Let's have kubernetes cluster
```bash
#export KIND_EXPERIMENTAL_PROVIDER=podman
NAME=demo
cat>my-kind-config<<EOF 
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $NAME
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".registry]
    config_path = "/etc/containerd/certs.d"
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

kind create cluster --config=my-kind-config
k get nodes
```

### Setup Harbor Helm-Chart 
```
curl -s https://raw.githubusercontent.com/naren4b/harbor-registry/main/setup.sh | bash
```
### Install Ingress controller
```bash
curl -L -o deploy.yaml https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl label nodes $NAME-control-plane ingress-ready="true"
kubectl apply -f deploy.yaml 
kubectl wait --for=condition=ready pod -n ingress-nginx -l app.kubernetes.io/component=controller
```
### Install harbor 
```
DOMAIN=.127.0.0.1.nip.io # CHANGE
SOURCE_REGISTRY="" # IF any 
cat > harbor-values.yaml <<EOF
expose:
  ingress:
    hosts:
      core: registry${DOMAIN} #TODO
      notary: notary${DOMAIN} #TODO
externalURL: https://registry${DOMAIN} # TODO

nginx:
  image:
    repository: ${SOURCE_REGISTRY}goharbor/nginx-photon

portal:
  image:
    repository: ${SOURCE_REGISTRY}goharbor/harbor-portal

core:
  image:
    repository: ${SOURCE_REGISTRY}goharbor/harbor-core

jobservice:
  image:
    repository: ${SOURCE_REGISTRY}goharbor/harbor-jobservice

registry:
  registry:
    image:
      repository: ${SOURCE_REGISTRY}goharbor/registry-photon
  controller:
    image:
      repository: ${SOURCE_REGISTRY}goharbor/harbor-registryctl

trivy:
  enabled: false
  image:
    repository: ${SOURCE_REGISTRY}goharbor/trivy-adapter-photon

database:
  internal:
    image:
      repository: ${SOURCE_REGISTRY}goharbor/harbor-db

redis:
  internal:
    image:
      repository: ${SOURCE_REGISTRY}goharbor/redis-photon

exporter:
  image:
    repository: ${SOURCE_REGISTRY}goharbor/harbor-exporter
EOF
helm repo add harbor https://helm.goharbor.io
helm repo update
helm uninstall -n registry harbor  && kubectl delete pvc -n registry -l app=harbor
helm upgrade --install harbor harbor/harbor -f harbor-values.yaml -n registry --create-namespace
kubectl wait --for=condition=ready pod -n registry -l app=harbor -l component=portal
```
### Setup Client 
```
URL=$HARBOR_URL
CERT_PATH=/etc/docker/certs.d/${URL}
sudo mkdir -p $CERT_PATH
sudo openssl s_client -connect ${URL}:443 -showcerts </dev/null | sed -n -e '/-.BEGIN/,/-.END/ p' > /etc/docker/certs.d/${URL}/ca.crt
sudo systemctl restart docker
# for any local URL 
echo 127.0.0.1 $URL >> /etc/hosts 
```

### Load an image to registry 
```
docker login registry.127.0.0.1.nip.io -u admin -p Harbor12345
docker pull nginx:latest
docker tag nginx:latest $HARBOR_URL/library/nginx:latest
docker push $HARBOR_URL/library/nginx:latest
```
### 
[NEXT: Let's try basic Harbor API](harbor-api.md)


Ref: 
- [Demo Environment](https://killercoda.com/killer-shell-cks/scenario/container-namespaces-docker)



