# How to create,build,push,host,deploy Private Helm Charts using Chartmuseum 
#### Assumption
- Server url http://nks-charts:8080

#### host : Installation of Chartmuseum  via Docker 
```
mkdir charts
chmod 667 charts
docker run --rm -it -d -p 8080:8080   -e DEBUG=1   -e STORAGE=local   -e STORAGE_LOCAL_ROOTDIR=/charts   -v $(pwd)/charts:/charts ghcr.io/helm/chartmuseum:v0.14.0
```

#### create At Developer Machine Prepare your chart 
```
git clone https://github.com/naren4b/helm-charts.git
cd helm-charts/charts
helm create nks-web
git add -A
git commit -m "nks-web chart added"
git push
```
![image](https://user-images.githubusercontent.com/3488520/192074163-a10d0097-ef1f-4760-a3fe-181feda4bfe5.png)
![image](https://user-images.githubusercontent.com/3488520/192074099-2327a912-ba7f-4c7d-b6f0-c555c558cd2b.png)


#### package & push :  machine side for packaging and pushing the chart 
```
helm plugin install https://github.com/chartmuseum/helm-push
git clone https://github.com/naren4b/helm-charts.git
cd helm-charts/charts
helm package nks-web --version 1.0.0 --app-version 1.0.0
curl --data-binary "@nks-web-1.0.0.tgz" http://nks-charts:8080/api/charts
//or 
helm repo add nks http://nks-charts:8080
helm cm-push nks-web nks --version 0.1.0 --app-version 0.1.0
```

#### At Deployment 
```
helm repo add nks-charts http://nks-charts:8080/
helm repo update
helm search repo nks-charts
helm install nks/nks-web --generate-name
```
![image](https://user-images.githubusercontent.com/3488520/192074351-18c9bf41-b533-47b9-914e-7339bb5d4b02.png)
![image](https://user-images.githubusercontent.com/3488520/192074377-1f743e53-fe55-47fe-b72b-98160d395af7.png)
![image](https://user-images.githubusercontent.com/3488520/192074420-c4253391-67d7-4459-83a7-4e97ad8b9354.png)



#### ref: 
- https://github.com/helm/chartmuseum/blob/main/README.md
- https://github.com/chartmuseum/helm-push
