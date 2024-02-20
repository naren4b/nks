# Setting up Basic Harbor Registry in a Kubernetes Cluster 
![harbor](https://github.com/naren4b/nks/assets/3488520/b01ad8c0-c649-45d1-938c-6abc44760af1)

### Let's have kubernetes cluster
```bash
curl -s https://raw.githubusercontent.com/naren4b/dotfiles/main/ws/install.sh | bash
```

### Setup Harbor Helm-Chart 
```
curl -s https://raw.githubusercontent.com/naren4b/harbor-registry/main/setup.sh | bash
```

### Install harbor 
```
curl -O https://raw.githubusercontent.com/naren4b/harbor-registry/main/harbor-values.yaml #change the values if you want 
HARBOR_URL=registry.127.0.0.1.nip.io
curl https://raw.githubusercontent.com/naren4b/harbor-registry/main/install.sh | bash
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



