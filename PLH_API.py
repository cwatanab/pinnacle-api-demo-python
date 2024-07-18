import requests
import numpy as np
import os
import time
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional, Any


class ServiceType(str, Enum):
    BAROCAL_ONLY = 'BAROCAL_ONLY'
    ALT_BAROCAL = 'ALT_BAROCAL'
    ALT_ONLY = 'ALT_ONLY'


class XYLocation(BaseModel):
    latitude: float
    longitude: float
    accuracy: float = 100


class DevicePressure(BaseModel):
    average: float = 0
    variance: float = 0
    count: int = 0
    min: float = 0
    max: float = 0

    def __init__(self, values:np.ndarray|List):
        super().__init__()        
        if type(values) != np.ndarray:
           values = np.array(values)
        self.average = np.mean(values)
        self.variance = np.var(values)
        self.count = int(np.size(values))
        self.min = np.min(values)
        self.max = np.max(values)


class ActivityType(str, Enum):
    STILL = 'STILL'
    WALKING = 'WALKING'
    TILTING = 'TILTING'
    ON_FOOT = 'ON_FOOT'
    RUNNING = 'RUNNING'
    IN_VEHICLE = 'IN_VEHICLE'
    AUTOMOBILE = 'AUTOMOBILE'
    ON_BYCYCLE = 'ON_BYCYCLE'
    CYCLING = 'CYCLING'
    UNKNOWN = 'UNKNOWN'


class YesOrNo(str, Enum):
    YES = 'Y'
    NO = 'N'


class DeviceActivity(BaseModel):
    activity: ActivityType
    confidence: int


class PLHAltitudeRequest(BaseModel):
    appId: str = os.environ.get('APP_ID')
    deviceId: str = os.environ.get('DEVICE_ID')
    appVerion: Optional[str] = None
    serviceType: Optional[ServiceType] = None
    phoneModel: Optional[str] = None
    baroModel: Optional[str] = None
    xyLocation: XYLocation
    pressure: DevicePressure
    batteryTemperature: Optional[float] = None
    activity: Optional[List[DeviceActivity]] = None
    timestamp: int = int(time.time() * 1000)


class ZHeight(BaseModel):
    value: float
    accuracy: float
    accuracy68: float
    accuracy90: float
    accuracy95: float


class PLHResult(BaseModel):
    xyLocation: XYLocation
    hae: Optional[ZHeight]
    hat: Optional[ZHeight]
    barocalNeeded: YesOrNo
    timestamp: int


class Status(Enum):
    SUCCESS = 200
    GENERAL_ERROR = 400
    OUT_OF_AREA = 600
    NO_REF_DATA = 610
    NO_BAROCAL_DATA = 620
    NO_DATA = 630


class PLHAltitudeResponse(BaseModel):
    status: Status
    result: Optional[PLHResult]


class PLHClient(object):

    def __init__(self, 
       base_url='https://api.nextnav.io/plh',
       api_key=os.environ.get('API_KEY')
    ) -> None:
       self.session = requests.session()
       self.base_url = base_url
       self.api_key = api_key

    def get(self, req_data: PLHAltitudeRequest) -> PLHResult:
    
        api_url = self.base_url + '/v1/get-live-height'
        headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                api_url, 
                headers=headers, 
                data=req_data.model_dump_json(exclude_none=True)
            )
            response.raise_for_status()
            res_data = response.json()
            result = PLHAltitudeResponse(**res_data)
            if result.status != Status.SUCCESS:
                raise(result.status)
            return result.result

        except requests.exceptions.RequestException as e:
            raise(e)
