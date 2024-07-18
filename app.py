from dotenv import load_dotenv
load_dotenv()

import os
import time
from PLH_API import *

client = PLHClient()

# 気圧の測定データ ※ hPa ではなくPaなので注意
values = [ 99784.00, 99786.00, 99784.00, 99786.00, 99788.00, 99788.00, 99788.00 ]

# 位置情報
location = {'latitude': 35.68021168333, 'longitude': 139.7576692371 }

req_data = PLHAltitudeRequest(
    pressure=DevicePressure(values),
    xyLocation=XYLocation(**location)
)

print('>>>>> REQUEST >>>>>')
print(req_data.model_dump_json(indent=2, exclude_none=True))

res_data = client.get(req_data)

print('<<<<< RESPONSE <<<<<')
print(res_data.model_dump_json(indent=2, exclude_defaults=True))
