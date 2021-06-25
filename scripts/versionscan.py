import json
from datetime import datetime

import remotezip
import requests

versionList = []
versions = {
    "ktp": [],
    "koe": []
}

knownOldestVersion = 217
latestUrl = "https://static.abitti.fi/usbimg/prod/latest.txt"
filePath = "../versions.json"


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def getLatestVersion():
    version = requests.get(latestUrl)
    return int(version.text)


def extractMetaData(zip_url, code):
    zipFile = remotezip.RemoteZip(zip_url)
    metadata = zipFile.read('ytl/.meta/manifest.json').decode('utf-8')
    creationDate = datetime(*zipFile.getinfo('ytl/.meta/manifest.json').date_time)
    metaJSON = json.loads(metadata)
    return {"versionName": metaJSON['name'], "versionCode": code, "releaseDate": creationDate, "url": zip_url}


latestVersion = getLatestVersion()
print("Latest version: " + str(latestVersion))

for i in range(knownOldestVersion, latestVersion + 5):
    try:
        url = "https://static.abitti.fi/etcher-usb/releases/" + str(i) + "/koe-etcher.zip"
        meta = extractMetaData(url, i)
        if len(versions['koe']) < 1 or (
                meta.get('versionName') != versions['koe'][len(versions['koe']) - 1].get('versionName') and meta.get(
                'releaseDate') != versions['koe'][len(versions['koe']) - 1].get('releaseDate')):
            versions['koe'].append(meta)
            print(str(meta['versionCode']) + ": " + meta['versionName'])
        try:
            url = "https://static.abitti.fi/etcher-usb/releases/" + str(i) + "/ktp-etcher.zip"
            meta = extractMetaData(url, i)
            if len(versions['ktp']) < 1 or (meta.get('versionName') != versions['ktp'][len(versions['ktp'])-1].get('versionName') and meta.get('releaseDate') != versions['ktp'][len(versions['ktp'])-1].get('releaseDate')):
                versions['ktp'].append(meta)
                print(str(meta['versionCode']) + ": " + meta['versionName'])
        except:
            print(str(i) + "_ktp: Failed!")
    except:
        print(str(i) + ": Failed!")

jsonString = json.dumps(versions, cls=DateTimeEncoder)
print(jsonString)

print("Writing to "+filePath)
jsonDump = open(filePath, "w")
jsonDump.write(jsonString)
jsonDump.close()
