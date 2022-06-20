import json
import re
from datetime import datetime
from dateutil import relativedelta

import remotezip
import requests

versionList = []
versions = {
    "ktp": [],
    "koe": []
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/5320 (KHTML, like Gecko) Chrome/39.0.843.0 Mobile '
                  'Safari/5320',
}

knownOldestVersion = 217
#latestUrl = "https://static.abitti.fi/usbimg/prod/latest.txt"
releaseNotesUrl = "https://www.abitti.fi/fi/paivitykset/parannukset/digabios-palvelintikku-opiskelijan-tikku/"
filePath = "docs/versions.json"
filePathIndented = "docs/versions.pretty.json"

releasePattern = re.compile("((ABITTI|SERVER)[0-9]{4}[A-Z0-9])")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def getLatestVersion():
    # Because abitti's old latest version endpoint is now unavailable, and updates
    # usually come within a month or two, just iterate the number every month.
    base_ver = 245
    last_scan = datetime.strptime('Jun 20 2022', '%b %d %Y')
    delta = relativedelta.relativedelta(datetime.now().date(), last_scan.date())
    return base_ver + delta.months


releaseNotes = requests.get(releaseNotesUrl, headers=headers)
if releaseNotes.status_code != 200:
    print("Release notes returned error code "+str(releaseNotes.status_code))
    exit(-1)

productionTable = [(x[0] if len(x) > 0 else None) for x in releasePattern.findall(releaseNotes.text)]
print("Production releases: "+str(len(productionTable)))

def extractMetaData(zip_url, code):
    zipFile = remotezip.RemoteZip(zip_url)
    metadata = zipFile.read('ytl/.meta/manifest.json').decode('utf-8')
    creationDate = datetime(*zipFile.getinfo('ytl/.meta/manifest.json').date_time)
    metaJSON = json.loads(metadata)
    return {"versionName": metaJSON['name'], "versionCode": code, "releaseDate": creationDate, "url": zip_url,
            "beta": (code > latestVersion or metaJSON["name"] not in productionTable)}


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
            print(str(meta['versionCode']) + ": " + meta['versionName'] + (" (BETA)" if meta["beta"] else ""))
        try:
            url = "https://static.abitti.fi/etcher-usb/releases/" + str(i) + "/ktp-etcher.zip"
            meta = extractMetaData(url, i)
            if len(versions['ktp']) < 1 or (meta.get('versionName') != versions['ktp'][len(versions['ktp']) - 1].get(
                    'versionName') and meta.get('releaseDate') != versions['ktp'][len(versions['ktp']) - 1].get(
                'releaseDate')):
                versions['ktp'].append(meta)
                print(str(meta['versionCode']) + ": " + meta['versionName'] + (" (BETA)" if meta["beta"] else ""))
        except:
            print(str(i) + "_ktp: Failed!")
    except:
        print(str(i) + ": Failed!")

jsonStringIndented = json.dumps(versions, cls=DateTimeEncoder, indent=4)
jsonString = json.dumps(versions, cls=DateTimeEncoder)

print(jsonString)

print("Writing to " + filePath)
jsonDump = open(filePath, "w")
jsonDump.write(jsonString)
jsonDump.close()

print("Writing to " + filePathIndented)
jsonDump = open(filePathIndented, "w")
jsonDump.write(jsonStringIndented)
jsonDump.close()
