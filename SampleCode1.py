'''
This sample code is meant to track the history of multiple mac addresses using CMX.
To run this code you need to make certain environment changes. The configuration changes are listed below in the configuration
section such as mseIp, macs, username, password.
mseIp is the IP of the MSE() in the CMX
mac is the mac addresses which is to be tracked
username/password are the credentials to access the apis of the CMX
you don't need to change urlPrefix and urlSuffix but still just verify them according to your environment.
If you have any issues in running this code
you can issue a bug in the github repository giving all the details of your environment
'''
__author__ = "Ronak Lakhwani"

#============ General Imports 
from datetime import datetime

#==========Imports for calling the CMX Rest API 
import urllib2
from urllib2 import URLError

#=========== Imports for reading the xml response
from bs4 import BeautifulSoup

# ========== Imports for reading the json response
import json


# ================= Imports for plotting the graph
import plotly.plotly as py
import plotly.tools as tls
from plotly.graph_objs import Layout,Marker,Scatter,XAxis,YAxis,Data,Figure


# ================ CONFIGURATION STARTS
# ================ Change it according to your local environment.
version = "MSE8.0"
urlPrefix = "https://"
mseIp = "128.107.125.15"
urlSuffix = "/api/contextaware/v1/location/history/clients/"
mac = "3c:a9:f4:33:66:40"
username = "learning"
password = "learning"
responseFormat = "xml" # Could be xml or json
# ================CONFIGURATION ENDS


def getResponse(URL, username, password,responseFormat):
    '''
     Returns the response in the form of dict where keys are isError and others.
     if isError is True then dict contains the other keys such as data which contains the description of the message
     if isError is False then dict contains the other keys such as width,length,data.
    '''
    responseDict = {}
    try :
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, URL, username, password)
        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        opener.addheaders = [('Accept', 'application/' + responseFormat)]
        urllib2.install_opener(opener)
        page = urllib2.urlopen(URL).read()
        
        if responseFormat == "xml" :
            dataDict = getUsefulDataFromXML(page)
        elif responseFormat == "json":
            dataDict = getUsefulDataFromJson(page)
        dataDict['isError'] = False
        return dataDict
    except URLError, e:
        responseDict['data'] = e
        responseDict['isError'] = True
        return responseDict
    
    

def parseDate(stringDate):
    '''
    Gets the date in the string format 2015-03-17T00:27:33.437+0000 and converts it into 2015-03-17 00:27:33 and then returns the date_object
    '''
    stringDate = stringDate[0:10] + " " + stringDate[11:19]
    date_object = datetime.strptime(stringDate, "%Y-%m-%d %H:%M:%S")
    return date_object

def getUsefulDataFromJson(jsonResponse):
    '''
    Parses the jsonResponse and returns the dict with keys as width, length and the data 
    1. width contains the value of the width
    2. length contains the value of the length
    3. data contains the list of tuples where tuples are in the format (lastlocatedtime,x,y)
    All the above three are returned only when you get location from the jsonResponse otherwise an empty dict is returned
    
    '''
    data = []
    jsonDict = json.loads(jsonResponse)
    if len(jsonDict['Locations']['entries']) > 0:
        width = jsonDict['Locations']['entries'][0]['MapInfo']['Dimension']['width']
        length = jsonDict['Locations']['entries'][0]['MapInfo']['Dimension']['length']
        
        for wirelessclientlocation in jsonDict['Locations']['entries']:
            x = wirelessclientlocation["MapCoordinate"]["x"]
            y = wirelessclientlocation["MapCoordinate"]["y"]
            lastlocatedtime = parseDate(wirelessclientlocation["Statistics"]["lastLocatedTime"])
            data.append((lastlocatedtime, x, y))
        return {"width" : width, "length":length, "data":data}
    else :
        return {}

def getUsefulDataFromXML(xml):
    '''
    Parses the xml and returns the dict with keys as width, length and the data 
    1. width contains the value of the width
    2. length contains the value of the length
    3. data contains the list of tuples where tuples are in the format (lastlocatedtime,x,y)
    All the above three are returned only when you get location from the jsonResponse otherwise an empty dict is returned
    
    '''
    data = []
    xmlFormat = BeautifulSoup(xml)
    wirelessclientlocations = xmlFormat.find_all("wirelessclientlocation")
    if len(wirelessclientlocations) > 0:
        width = xmlFormat.locations.wirelessclientlocation.mapinfo.dimension['width']
        length = xmlFormat.locations.wirelessclientlocation.mapinfo.dimension['length']
        for wirelessclientlocation in wirelessclientlocations:
            x = wirelessclientlocation.mapcoordinate['x']
            y = wirelessclientlocation.mapcoordinate['y']
            lastlocatedtime = parseDate(wirelessclientlocation.statistics['lastlocatedtime'])
            data.append((lastlocatedtime, x, y))
        return {"width" : width, "length":length, "data":data}
    else:
        return {}



def plotData(dataDict):
    '''
    Plots the data on the Plotly Framework.
    '''
    pData = dataDict['data']
    pData = sorted(pData, key=lambda x:x[0])
    
    
    processedData = Scatter(
        x=[x[1] for x in pData],
        y=[y[2] for y in pData],
        mode='lines + text',
        text = range(1,len(pData) + 1),
        name=mac,
        marker=Marker(color="red")
    )
    
    
    py.sign_in('raunaklakhwani', 'b3fga1fz2k')
    tls.set_credentials_file(username="raunaklakhwani",
                                 api_key="b3fga1fz2k")
    
    layout = Layout(
                showlegend=True,
                autosize=True,
                height=800,
                width=800,
                title="MAP",
                xaxis=XAxis(
                    zerolinewidth=4,
                    gridwidth=1,
                    showgrid=True,
                    zerolinecolor="#969696",
                    gridcolor="#bdbdbd",
                    linecolor="#636363",
                    mirror=True,
                    zeroline=False,
                    showline=True,
                    linewidth=6,
                    type="linear",
                    range=[0, dataDict["length"]],
                    autorange=False,
                    autotick=False,
                    dtick=15,
                    tickangle=-45,
                    title="X co-ordinate"
                    ),
                yaxis=YAxis(
                    zerolinewidth=4,
                    gridwidth=1,
                    showgrid=True,
                    zerolinecolor="#969696",
                    gridcolor="#bdbdbd",
                    linecolor="#636363",
                    mirror=True,
                    zeroline=False,
                    showline=True,
                    linewidth=6,
                    type="linear",
                    range=[dataDict["width"], 0],
                    autorange=False,
                    autotick=False,
                    dtick=15,
                    tickangle=-45,
                    title="Y co-ordinate"    
                    )
                )
    data = Data([processedData])
    fig = Figure(data=data, layout=layout)
    py.plot(fig, filename='Sample Code For History Of Clients ')
    
    
    

if __name__ == '__main__':
    URL = urlPrefix + mseIp + urlSuffix + mac
    dataDict = getResponse(URL, username, password,responseFormat)
    if dataDict['isError'] ==  False:
        if len(dataDict['data']) > 0:
            plotData(dataDict)
        else:
            print 'No clients found'
    else:
        print "Error = ", dataDict['data']
    
