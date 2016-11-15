"""
Edge Computing Embedded Platform
Developed by Abhishek Gurudutt, Chinmayi Divakara
Praveen Prabhakaran, Tejeshwar Chandra Kamaal

Registers the device with a unique name, periodic 
heartbeat message generation and transmit other 
messages such as logs, etc.
"""

import threading
import time
import sys
from wamp_client import *
import callContainer_api as cca

from ..ecep_docker import cpu_info

ticks = 20 #seconds

client = None
    
def init(device):
    global client
    client = wampserver(device)


# decorator for threads
def threaded(func):
    """
    A wrapper to create a thread.
    Takes function as input.
    Returns a handler for thread.
    """
    def func_wrapper(*args, **kwargs):
        thread = threading.Thread(target = func, args = args, kwargs = kwargs)
        thread.setDaemon(True)
        thread.start()
        return thread
    return func_wrapper


class periodicTransmit(object):
    """
    This class definitions which handle message
    transmission.
    """
    
    def __init__(self, deviceID):
        self._deviceId = deviceID
        self._topic = None
        self._heartbeatData = {}
        self._containerData = {}
        self._cpuInfo = {}
    
    #device registration and heartbeat
    @threaded
    def heartbeat(self):
        while True:
            self._topic = "com.ecep.heartbeat"
            self._heartbeatData['deviceId'] = self._deviceId
            self._heartbeatData['location'] = cpu_info.getDeviceLocation()
            self._heartbeatData['arch'] = cpu_info.getMachineArchitecture()
            sendTo(self._topic, self._heartbeatData)
            time.sleep(ticks)
            
    #Send container status
    @threaded
    def containerStatus(self):
        while True:
            self._topic = "com.ecep.containerStatus"
            self._containerData = cca.getContainerList()
            sendTo(self._topic, self._containerData)
            time.sleep(ticks*5) #  100 seconds
            
            
    #Send CPU information
    @threaded
    def cpuInfo(self):
        while True:
            self._topic = "com.ecep.cpuInfo"
            self._cpuInfo['deviceId'] = self._deviceId
            self._cpuInfo['info'] = cpu_info.getCpuInfo()
            sendTo(self._topic, self._cpuInfo)
            time.sleep(ticks*50) # 1000 seconds
            
            
if __name__ == "__main__":
         
    global client
    
    device = 'falcon'
    init(device)
    
    # params for wampserver
    ip = sys.argv[1]
    port = sys.argv[2]
    realm = unicode(sys.argv[3])
    
    print(ip, port, realm)
    check = client.connect(ip, port, realm)
    
    
    #wait till the connection is established
    time.sleep(5)
    
    #create an instance
    periodicTransmit_I = periodicTransmit(device)
    
    # Launch thread
    handle_heartbeat = periodicTransmit_I.heartbeat()
    handle_containerStatus = periodicTransmit_I.containerStatus()
    handle_cpuInfo = periodicTransmit_I.cpuInfo()
    
    while True:
        time.sleep(2)
        
    handle_heartbeat.join()
    handle_containerStatus.join()
    handle_cpuInfo.join()
