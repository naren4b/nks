# Setup Minio S3 with Transport Layer Security (TLS) 1.2+ encryption

## Install minio certgen tool

```bash
curl https://github.com/minio/certgen/releases/latest/download/certgen-linux-amd64 \
   --create-dirs \
   -o $HOME/minio-binaries/certgen
chmod +x $HOME/minio-binaries/certgen
export PATH=$PATH:$HOME/minio-binaries/
```

## Install minio server

```bash
mkdir -p ~/minio/data
mkdir -p ~/minio/certs

cd ~/minio/certs
certgen -host "127.0.0.1,localhost"
ls
cd ../..

MINIO_ROOT_USER=minio
MINIO_ROOT_PASSWORD=minio123
```

Install the server

```bash
docker run  -d --rm --name minio  \
                    -p 9000:9000 \
                    -p 9001:9001 \
                    -v ~/minio/data:/data \
                    -v ~/minio/certs:/opts/certs \
                    -e "MINIO_ROOT_USER=$MINIO_ROOT_USER" \
                    -e "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" \
                    quay.io/minio/minio server /data --console-address ":9001" --certs-dir /opts/certs
```

## Access bucket via minio client mc

```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs \
  -o $HOME/minio-binaries/mc
chmod +x $HOME/minio-binaries/mc

mc alias set myminio https://127.0.0.1:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
mc admin info myminio
mc mb myminio/demo-bucket
touch demo.txt
echo "Hello My S3 "> demo.txt
mc cp demo.txt myminio/demo-bucket
mc ls myminio/demo-bucket
```

![image](https://github.com/naren4b/nks/assets/3488520/c031d629-1139-4beb-9247-987b5c685547)

## Access the bucket via s3cmd client

```
sudo apt install s3cmd

cat<<EOF >  ~/.s3cfg
host_base = 127.0.0.1:9000
host_bucket = 127.0.0.1:9000
bucket_location = us-east-1
use_https = True

# Setup access keys
access_key =  minio
secret_key = minio123

# Enable S3 v4 signature APIs
signature_v2 = False

EOF

s3cmd -c ~/.s3cfg --ca-certs=~/minio/certs/public.crt ls s3://demo-bucket

```

[Demo Environment](https://killercoda.com/killer-shell-ckad/scenario/playground)

ref:

- https://min.io/docs/minio/container/operations/network-encryption.html
