# Local setup for testing vmbackup and vmrestore
![vmc-backup-restore](https://github.com/naren4b/nks/assets/3488520/52d0819b-8618-4103-b51f-c5f59cad78a8)


### Complete the test setup for monitoring-stack 
ref: [Setting up Monitoring Stack in a Node (docker container)](https://naren4b.github.io/nks/setup-monitoring-stack.html)

### Run minio for local:S3 | run-minio.sh

```bash
#! /bin/bash

name=$1
default_value="demo"
name=${name:-$default_value}
docker volume create minio-data

# minio
minio_name=${name}-minio
minio_host_port=9000,9001
docker rm ${minio_name} -f
docker run -d --restart unless-stopped --network host \
    --name=${minio_name} \
    -v minio-data:/data \
    -e "MINIO_ROOT_USER=ROOTNAME" \
    -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
    quay.io/minio/minio server /data --console-address ":9001"

docker ps -l
```

### Install the mc client for creating the bucket

```bash
docker run --privileged -v ${PWD}:/tmp -it --network host --entrypoint=/bin/sh minio/mc

S3_ALIAS=demo
S3_ENDPOINT=http://localhost:9000
ACCESS_KEY=ROOTNAME
SECRET_KEY=CHANGEME123
BUCKET_NAME=data
mc alias set $S3_ALIAS $S3_ENDPOINT $ACCESS_KEY $SECRET_KEY --api "s3v4" --path "auto"

mc --insecure rm -r --force $S3_ALIAS/$BUCKET_NAME
mc --insecure mb $BUCKET_NAME

#ref: https://github.com/minio/minio/issues/4769#issuecomment-320319655

```

### Take the Backup

```bash
#!/bin/bash
cat <<EOF >/etc/credentials
[default]
aws_access_key_id=ROOTNAME
aws_secret_access_key=CHANGEME123
EOF

docker run -v victoria-metrics-data:/victoria-metrics-data --network host victoriametrics/vmbackup -storageDataPath=/victoria-metrics-data -snapshot.createURL=http://localhost:8428/snapshot/create -dst=s3://localhost:9000/data -credsFilePath=/etc/credentials -customS3Endpoint=http://localhost:9000


```

### Do the Restore

```bash
cat<<EOF>/etc/credentials
[default]
aws_access_key_id=ROOTNAME
aws_secret_access_key=CHANGEME123
EOF

docker run  -v victoria-metrics-data:/victoria-metrics-data --network host victoriametrics/vmrestore -storageDataPath=/victoria-metrics-data -snapshot.createURL=http://localhost:8428/snapshot/create    -src=s3://localhost:9000/data -credsFilePath=/etc/credentials -customS3Endpoint=http://localhost:9000

```

https://github.com/VictoriaMetrics/VictoriaMetrics/issues/353

### Ref:

- [Demo Environment](https://killercoda.com/killer-shell-cks/scenario/container-namespaces-docker)
- [monitoring-stack.git](https://github.com/naren4b/monitoring-stack.git)
