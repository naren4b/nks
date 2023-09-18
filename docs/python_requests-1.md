# Extract, transform, and load (ETL) of the data using python(1/n)

## - Extract, transform, and load (ETL) of the data
- Learn how to pull data from a REST endpoint
- Data Handling (Json/Yaml)
- Filter the data (Extraction ) from a Json file
- Transform the data to String (Transformation)
- Store the data in a CSV file (Load)

## Python program for pulling a REST API data
```python
# python get_json_data.py
import requests;

def getData(url):
      response=requests.get(url)
      print(response)
      return response.text

if __name__ == "__main__":
    data=getData('https://swapi.dev/api/planets/1/')
    print(data)
```
## Python program for pulling a REST API endpoint and extract json data
```get_json_data.py
# python get_json_data.py
import requests;
import json;

def getData(url):
      response=requests.get(url)
      print(response)
      return response.json()

if __name__ == "__main__":
    data=getData('https://swapi.dev/api/planets/1/')
    print(json.dumps(data, indent=4, sort_keys=True))

```
## Python program to store the json payload in a json file

```store_json_data.py
# mkdir -p out && python store_json_data.py

import requests;
import json;
import time;

def save_to_file(file_name,data):   
   try:
      data_file=open(file_name,"x+")
   except Exception as err:    
      print(err)       
   str=json.dumps(data, indent=4, sort_keys=True)   
   data_file.write(str)
   print('Data saved to file: ',file_name)
   data_file.close

def getData(url):
      response=requests.get(url)
      print('Data collected from ',url)
      return response.json()

if __name__ == "__main__":
    print('*** Start ***')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    json_file_name ="out/swapi-planets" + "_"+ timestr + ".json"
    data=getData('https://swapi.dev/api/planets/1/')      
    save_to_file(json_file_name,data)  
    print('*** end ***')
```
## Python program to read REST API with multiple pages of json data and transform it to a csv file
```write_json_data_to_csv.py
# mkdir -p out && python write_json_data_to_csv.py

import requests;
import json;
import time;

 
def write_to_csv(json_file_name,csv_file_name):
    print("JSON File: ",json_file_name)
    json_file=open(json_file_name)
    data=json.load(json_file)
    csv_file=open(csv_file_name,"w")
    csv_file.write('name,url'+'\n')
    for d in data:
       csv_file.write(d['name']+","+d['url']+"\n")
    print('Data saved to file: ',csv_file_name)


def save_to_file(file_name,data):   
   try:
      data_file=open(file_name,"x+")
   except Exception as err:    
      print(err)       
   str=json.dumps(data['results'], indent=4, sort_keys=True)   
   data_file.write(str)
   print('Data saved to file: ',file_name)
   data_file.close

def getData(url):
      response=requests.get(url)
      print('Data collected from ',url)
      return response.json()

if __name__ == "__main__":
    print('*** Start ***')
    timestr = time.strftime("%Y%m%d-%H%M%S")
    json_file_name ="out/pokemon-data" + "_"+ timestr + ".json"
    csv_file_name ="out/pokemon-data" + "_"+ timestr + ".csv"
    data=getData('https://pokeapi.co/api/v2/pokemon')      
    save_to_file(json_file_name,data)  
    write_to_csv(json_file_name,csv_file_name)
    print('*** end ***') 
```

## Python program to read REST API with basic authentication
Create the access token : Go this site and get an access token [https://github.com/settings/tokens](https://github.com/settings/tokens)
click on generate token 
![image](https://github.com/naren4b/nks/assets/3488520/4b93a4dc-9060-464e-b3d0-ead796f3a69e)
![image](https://github.com/naren4b/nks/assets/3488520/4abfbd89-d966-4110-8496-ab525335dac5)
![image](https://github.com/naren4b/nks/assets/3488520/83ed34ef-6924-4b32-b449-223da5c2293a)

```test_basic_authentication.py
# python test_basic_authentication.py
import requests;

response = requests.get('https://api.github.com/users/naren4b/repos', auth=('naren4b', 'grA_FJ4lN5LAgXXXXXXXXjxS07Rdv&&&&&&sdadad'))
print(response.text)

```


## ref: 
- https://www.scrapingbee.com/blog/best-python-http-clients/
- https://youtu.be/XtwK8Dq0ZiU
- https://requests.readthedocs.io/en/latest/
- https://requests.readthedocs.io/en/latest/user/quickstart/#make-a-request
- https://swapi.dev/


