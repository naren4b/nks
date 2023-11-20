# Collect the list of images 
```bash
  kubectl get pods --all-namespaces -o jsonpath='{range .items[*]}{"\n"}{.metadata.namespace}{"\t"}{range .spec.containers[*]}{.image}{", "}{end}{end}' |sort | uniq -c | awk '{print $2, $3, $4}' | tr "," " done"
```
# Segregate the images 
```py
import os

def process_dc_image_txt_files(directory):
    unique_images=set()
    files = os.listdir(directory)
    txt_files = [file for file in files if file.endswith('.txt')]
    for txt_file in txt_files:
        input_file = os.path.join(directory, txt_file)
        print("Fetch for: ",input_file)
        # namespace = collect_unique_ns(input_file)
        # # print("Unique Namespaces:")
        # # print("------------------")
        # # for ns in set(namespace):
        # #     print(ns)
        # # print()
        
        images = collect_images(input_file)
        unique_images.update(images)
    return unique_images

def collect_unique_ns(input_file):
    all_words_except_first = []

    # Read the file and collect all words except the first word
    with open(input_file, 'r') as file:
        for line in file:
            words = line.strip().split()
            if len(words) > 1:
                all_words_except_first.extend(words[0:1])

    return all_words_except_first

def collect_images(input_file):
    
    all_words_except_first = []

    # Read the file and collect all words except the first word
    with open(input_file, 'r') as file:
        for line in file:
            words = line.strip().split()
            if len(words) > 1:
                all_words_except_first.extend(words[1:])

    return all_words_except_first

def prepare_image_file(output_file, unique_images):
    with open(output_file, 'w') as file:
        for image in sorted(unique_images): 
             file.write(str(image) + '\n')

    
if __name__ == "__main__":
    directory = "/img/image-scan/list"  # Replace with your directory path
    unique_images=process_dc_image_txt_files(directory)
    output_file = "images.txt"
    prepare_image_file(output_file,unique_images)
    print("done")
      
```

# Scan Image List 
```bash
#!/bin/bash

###########################################################################
# How to run ? bash scan_images.sh <images-list-file-full-path> <metrics-prefix>  #
# example : bash scan_images.sh images.list demo                                  #
# Author: Narendranath Panda                                              #
###########################################################################

image_list_file=$1
image_list_file=${image_list_file:-images.txt}

scan_version=$(date +"%d-%m-%Y")
mkdir -p $scan_version

echo
#prom_file=$scan_version/image_scanning_result.prom

reports_dir=$scan_version/reports
mkdir -p $reports_dir

logs_dir=$scan_version/logs
mkdir -p $logs_dir

metrics_dir=$scan_version/metrics
mkdir -p $metrics_dir

echo "" >$logs_dir/failed-images.log
echo "" >$logs_dir/images-exists.log
echo "" >$logs_dir/processed-images.log
metric_prefix=$2
default_value="my_image"
metric_prefix=${metric_prefix:-$default_value}
number=0
if [ -e "$image_list_file" ]; then
    echo "Scanning starts..."
    for image_name in $(cat $image_list_file); do
        ((number++))
        echo $number". "$image_name
        image_report=($(echo $image_name | tr "/" _ | tr ":" _))
        grype_file_name=$reports_dir/$image_report-grype.json
        prom_file_name=$metrics_dir/$image_report.prom
        if [ -e "$grype_file_name" ]; then
            echo "$image_name" >>$logs_dir/images-exists.log
        else
            grype $image_name --quiet --add-cpes-if-none --output json >grype.out 2>&1
            if [ $? -ne 0 ]; then
                echo "$image_name" >>$logs_dir/failed-images.log
            else
                mv grype.out $grype_file_name
                H_vul=$(cat $grype_file_name | grep -i High | wc -l)
                L_vul=$(cat $grype_file_name | grep -i Low | wc -l)
                M_vul=$(cat $grype_file_name | grep -i Medium | wc -l)
                C_vul=$(cat $grype_file_name | grep -i Critical | wc -l)
                N_vul=$(cat $grype_file_name | grep -i Negligible | wc -l)
                digests=$(cat $grype_file_name | jq '.source.target.repoDigests[0]')

                docker images $image_name --digests --format "{{json . }}" >$reports_dir/$image_report-docker.json
                size=$(cat $reports_dir/$image_report-docker.json | jq -sc '.[] | {Repository, Size}' | jq -s 'map(. + {"originalSize": .Size})' | jq -r '
                map(
                    if .Size | endswith("GB") then
                        .Size |= (gsub("GB"; "") | tonumber * 1024 * 1024 * 1024)
                    else
                        if .Size | endswith("MB") then
                            .Size |= (gsub("MB"; "") | tonumber * 1024 * 1024)
                        else
                            if .Size | endswith("KB") then
                                .Size |= (gsub("KB"; "") | tonumber * 1024)
                            else
                                .size | tonumber
                            end
                        end
                    end
                )' | jq .[0].Size)

                repository=$(cat $reports_dir/$image_report-docker.json | jq '.Repository')
                tag=$(cat $reports_dir/$image_report-docker.json | jq '.Tag')
                IMAGE_ID=$(cat $reports_dir/$image_report-docker.json | jq -r ".ID")

                echo "${metric_prefix}_info{image_digest=$digests,image_name=\"$image_name\",image_registry=\"$source\",image_repository=$repository,image_tag=$tag} 1" >>$prom_file_name
                echo "${metric_prefix}_vulnerability_severity_count{image_digest=$digests,severity=\"Critical\"} $C_vul" >>$prom_file_name
                echo "${metric_prefix}_vulnerability_severity_count{image_digest=$digests,severity=\"High\"} $H_vul" >>$prom_file_name
                echo "${metric_prefix}_vulnerability_severity_count{image_digest=$digests,severity=\"Medium\"} $M_vul" >>$prom_file_name
                echo "${metric_prefix}_vulnerability_severity_count{image_digest=$digests,severity=\"Low\"} $L_vul" >>$prom_file_name
                echo "${metric_prefix}_vulnerability_severity_count{image_digest=$digests,severity=\"Negligible\"} $N_vul" >>$prom_file_name
                echo "${metric_prefix}_size_in_bytes{image_digest=$digests} $size" >>$prom_file_name
                docker rmi $IMAGE_ID >/dev/null 2>&1
                echo image_id=$IMAGE_ID, image_digest=$digests,image_name=\"$image_name\",image_registry=\"$source\",image_repository=$repository,image_tag=$tag >>$logs_dir/processed-images.log
            fi
        fi

    done
    echo
    echo
    ls -lrt $metrics_dir
    echo
    echo
    echo "Scanning done..."
    echo
    echo
    echo "execute this command to copy to node_exporter/textfilecollector"
    echo "cp 20-11-2023/metrics/*.prom /var/lib/node-exporter/textfile_collector/"
    echo

else
    echo "File '$image_list_file' does not exist in the directory.!"
fi

```
