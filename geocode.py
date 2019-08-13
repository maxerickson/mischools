import shutil
import csv
import time
import datetime
import requests

stamp=datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
shutil.copy('geocodes.csv', './.backups/geocodes-{}.csv'.format(stamp))

TIMEOUT=300
nominatim_endpoint='https://nominatim.openstreetmap.org/search'
session=requests.Session()
session.headers['User-Agent'] = 'https://github.com/maxerickson/mischools'

data=dict()
with open("geocodes.csv") as infile:
    csvin=csv.reader(infile)
    for row in csvin:
        data[row[0]]=(row[1],row[2],row[3])

with open("formatted.csv") as infile:
    csvin=csv.DictReader(infile)
    count=0
    for row in csvin:
        try:
            params=dict()
            params['street']=row['addr:housenumber']+' '+row['addr:street']
            params['city']=row['addr:city']
            params['state']=row['addr:state']
            params['postalcode']=row['addr:postcode']
            params['format']='jsonv2'
            params['countrycodes']='us'
            # prepare request to get url
            req=requests.Request('GET', nominatim_endpoint, params=params)
            prepped = session.prepare_request(req)
            # retrieve result if it isn't in the cache
            if prepped.url not in data:
                print(prepped.url)
                response=session.send(prepped, timeout=TIMEOUT)
                data[prepped.url]=row['name'],row['addr:city'],response.text
                time.sleep(3)
                count+=1
                if count==1000:
                    break
        except Exception as e:
            print(e)
            break

with open("geocodes.csv", 'w') as outfile:
    csvout=csv.writer(outfile)
    for key,item in data.items():
        csvout.writerow([key]+list(item))