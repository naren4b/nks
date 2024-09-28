# Set Up S3 Bucket Replication(MINIO 🥡)
Bucket replication uses rules to synchronize the contents of a bucket on one MinIO deployment to a bucket on a remote MinIO deployment.

![s3-replicate-minio drawio](https://github.com/user-attachments/assets/a8b00cf9-fcd1-49a8-a0fc-43673f23f0e2)



#### Replication can be done in any of the following ways:
- **Active-Passive** Eligible objects replicate from the source bucket to the remote bucket. Any changes on the remote bucket do not replicate back.
- **Active-Active** Changes to eligible objects of either bucket replicate to the other bucket in a two-way direction.
- **Multi-Site Active-Active** Changes to eligible objects on any bucket set up for bucket replication replicate to all of the other buckets.

#### Bucket replication requires specific permissions on the source and destination deployments to configure and enable replication rules.

- The **EnableRemoteBucketConfiguration** statement grants permission for creating a remote target for supporting replication.
- The **EnableReplicationRuleConfiguration** statement grants permission for creating replication rules on a bucket. The "arn:aws:s3:::* resource applies the replication permissions to any bucket on the source deployment. You can restrict the user policy to specific buckets as-needed.

#### Replication Requires Versioning
MinIO relies on the immutability protections provided by versioning to support replication and resynchronization.

```bash
  --config-dir value, -C value  path to configuration folder (default: "/root/.mc") [$MC_CONFIG_DIR]                                                                                                                              
  --quiet, -q                   disable progress bar display [$MC_QUIET]                                                                                                                                                          
  --disable-pager, --dp         disable mc internal pager and print to raw stdout [$MC_DISABLE_PAGER]                                                                                                                             
  --no-color                    disable color theme [$MC_NO_COLOR]                                                                                                                                                                
  --json                        enable JSON lines formatted output [$MC_JSON]                                                                                                                                                     
  --debug                       enable debug output [$MC_DEBUG]                                                                                                                                                                   
  --resolve value               resolves HOST[:PORT] to an IP address. Example: minio.local:9000=10.10.75.1 [$MC_RESOLVE]                                                                                                         
  --insecure                    disable SSL certificate verification [$MC_INSECURE]                                                                                                                                               
  --limit-upload value          limits uploads to a maximum rate in KiB/s, MiB/s, GiB/s. (default: unlimited) [$MC_LIMIT_UPLOAD]                                                                                                  
  --limit-download value        limits downloads to a maximum rate in KiB/s, MiB/s, GiB/s. (default: unlimited) [$MC_LIMIT_DOWNLOAD]                                                                                              
  --id value                    id for the rule, should be a unique value                                                                                                                                                         
  --tags value                  format '<key1>=<value1>&<key2>=<value2>&<key3>=<value3>', multiple values allowed for multiple key/value pairs                                                                                    
  --storage-class value         storage class for destination, valid values are either "STANDARD" or "REDUCED_REDUNDANCY"                                                                                                         
  --disable                     disable the rule                                                                                                                                                                                  
  --priority value              priority of the rule, should be unique and is a required field (default: 0)                                                                                                                       
  --remote-bucket value         remote bucket, should be a unique value for the configuration                                                                                                                                     
  --replicate value             comma separated list to enable replication of soft deletes, permanent deletes, existing objects and metadata sync (default: "delete-marker,delete,existing-objects,metadata-sync")                
  --path value                  bucket path lookup supported by the server. Valid options are ['auto', 'on', 'off']' (default: "auto")                                                                                            
  --region value                region of the destination bucket (optional)                                                                                                                                                       
  --bandwidth value             set bandwidth limit in bytes per second (K,B,G,T for metric and Ki,Bi,Gi,Ti for IEC units)                                                                                                        
  --sync                        enable synchronous replication for this target. default is async                                                                                                                                  
  --healthcheck-seconds value   health check interval in seconds (default: 60)                                                                                                                                                    
  --disable-proxy               disable proxying in active-active replication. If unset, default behavior is to proxy
```
# Enable Two-Way Server-Side Bucket Replication
The procedure on this page creates a new bucket replication rule for two-way `active-active` synchronization of objects between MinIO buckets.

**Setting up two minio S3**
#### Install Minio Client(mc)
```bash
curl https://dl.min.io/client/mc/release/linux-amd64/mc \
  --create-dirs \
  -o $HOME/minio-binaries/mc
chmod +x $HOME/minio-binaries/mc
export PATH=$PATH:$HOME/minio-binaries/

```
#### Install certgen
```bash
curl https://github.com/minio/certgen/releases/latest/download/certgen-linux-amd64 \
   --create-dirs \
   -o $HOME/minio-binaries/certgen
chmod +x $HOME/minio-binaries/certgen
export PATH=$PATH:$HOME/minio-binaries/
```
#### Pull the latest image of minio
```bash
docker pull quay.io/minio/minio:latest
```
#### Let's get the Docker Host IP 
```bash
DOCKER_GATEWAY_IP=$(/sbin/ip route|awk '/docker0/ { print $9 }')
echo $DOCKER_GATEWAY_IP
```
#### Set up minio-1
```bash

MINIO_NAME_1=minio-1
mkdir -p ~/$MINIO_NAME_1/data
mkdir -p ~/$MINIO_NAME_1/certs

cd ~/$MINIO_NAME_1/certs
certgen -host "127.0.0.1,localhost,$MINIO_NAME_1"
ls
cd ../..

MINIO_ROOT_USER_1=$MINIO_NAME_1
MINIO_ROOT_PASSWORD=minio123

docker run  -d --rm --name $MINIO_NAME_1  \
                    -p 9000:9000 \
                    -p 9001:9001 \
                    -v ~/$MINIO_NAME_1/data:/data \
                    -v ~/$MINIO_NAME_1/certs:/opts/certs \
                    -e "MINIO_ROOT_USER=$MINIO_ROOT_USER_1" \
                    -e "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" \
                    quay.io/minio/minio server /data --console-address ":9001" --certs-dir /opts/certs
mc config host add $MINIO_NAME_1 http://${DOCKER_GATEWAY_IP}:9000 $MINIO_ROOT_USER_1 $MINIO_ROOT_PASSWORD


wget -O - https://min.io/docs/minio/linux/examples/ReplicationAdminPolicy.json | \
mc admin policy create $MINIO_NAME_1 ReplicationAdminPolicy /dev/stdin
mc admin user add $MINIO_NAME_1 ReplicationAdmin LongRandomSecretKey
mc admin policy attach $MINIO_NAME_1 ReplicationAdminPolicy --user=ReplicationAdmin
mc admin policy ls $MINIO_NAME_1

mc admin info $MINIO_NAME_1
mc mb $MINIO_NAME_1/data
mc version enable $MINIO_NAME_1/data
```

#### Set up minio-2
```bash
MINIO_NAME_2=$MINIO_NAME_2

mkdir -p ~/$MINIO_NAME_2/data
mkdir -p ~/$MINIO_NAME_2/certs

cd ~/$MINIO_NAME_2/certs
certgen -host "127.0.0.1,localhost,$MINIO_NAME_2"
ls
cd ../..

MINIO_ROOT_USER_2=$MINIO_NAME_2
MINIO_ROOT_PASSWORD=minio123

docker run  -d --rm --name $MINIO_NAME_2  \
                    -p 9002:9000 \
                    -p 9003:9001 \
                    -v ~/$MINIO_NAME_2/data:/data \
                    -v ~/$MINIO_NAME_2/certs:/opts/certs \
                    -e "MINIO_ROOT_USER=$MINIO_ROOT_USER_2" \
                    -e "MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD" \
                    quay.io/minio/minio server /data --console-address ":9001" --certs-dir /opts/certs
mc config host add $MINIO_NAME_2 http://$DOCKER_GATEWAY_IP:9002 $MINIO_ROOT_USER_2 $MINIO_ROOT_PASSWORD     

wget -O - https://min.io/docs/minio/linux/examples/ReplicationAdminPolicy.json | \
mc admin policy create $MINIO_NAME_2 ReplicationAdminPolicy /dev/stdin
mc admin user add $MINIO_NAME_2 ReplicationAdmin LongRandomSecretKey
mc admin policy attach $MINIO_NAME_2 ReplicationAdminPolicy --user=ReplicationAdmin
mc admin policy ls $MINIO_NAME_2

mc admin info $MINIO_NAME_2
mc mb $MINIO_NAME_2/data
mc version enable $MINIO_NAME_2/data
```
#### Enable the Replication
This procedure creates two-way, active-active replication between two MinIO

```bash
mc replicate add $MINIO_NAME_1/data --remote-bucket $MINIO_NAME_2/data  --priority 1
```
#### Test the setup  
**Upload the Minio-1** 
```
echo "Hello $MINIO_NAME_1 `date` ">> app.log   
mc cp app.log  $MINIO_NAME_1/data
```
**Check** 
```bash
echo && echo $MINIO_NAME_1 && mc cat   $MINIO_NAME_1/data/app.log && echo &&echo $MINIO_NAME_2 && mc cat $MINIO_NAME_2/data/app.log && echo 
```
**Upload the Minio-2**
```
echo "Hello $MINIO_NAME_2 `date` ">> app.log   
mc cp app.log  $MINIO_NAME_2/data
```
**Check** 
```bash
echo && echo $MINIO_NAME_1 && mc cat   $MINIO_NAME_1/data/app.log && echo &&echo $MINIO_NAME_2 && mc cat $MINIO_NAME_2/data/app.log && echo 
```






