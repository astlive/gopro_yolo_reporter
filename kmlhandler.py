import os
import glob
from types import SimpleNamespace
from lxml import etree
import geopy.distance

def getkmpoints(kmldir="./kmls/"):
    kmlfiles = glob.glob(kmldir + "*.kml")
    points = []
    count = 0
    for kf in kmlfiles:
        try:
            doc = etree.parse(kf)
            rr = doc.xpath('//kml:Placemark/kml:name/text()|//kml:Placemark/kml:Point/kml:coordinates/text()', namespaces={"kml":"http://www.opengis.net/kml/2.2"})
            for i in range(0,len(rr),2):
                name = rr[i]
                x,y,z = str(rr[i+1]).split(',')
                # point = {'name':name,'lon':x,'lat':y,'alt':z, 'index':count}
                point = SimpleNamespace(name=name, lon=x, lat=y, alt=z, index=count)
                count = count + 1
                points.append(point)
        except Exception as err:
            raise err
    return points

def kmplush(kmpoints, targetpoint):
    lpoint = kmpoints[0]
    rpoint = kmpoints[1]
    curdiff = geopy.distance.vincenty((lpoint.lat, lpoint.lon),(targetpoint.lat,targetpoint.lon)).km
    nxtdiff = geopy.distance.vincenty((rpoint.lat, rpoint.lon),(targetpoint.lat,targetpoint.lon)).km
    kmp = SimpleNamespace()
    for i in range(2,len(kmpoints)):
        if(curdiff<nxtdiff and curdiff<0.1):
            mdiff = geopy.distance.vincenty((lpoint.lat, lpoint.lon),(targetpoint.lat, targetpoint.lon)).km*1000
            if(nxtdiff>=0.1):
                kmp.name = kmpoints[lpoint.index - 1].name
                kmp.meter = 100 - mdiff
            else:
                kmp.name = lpoint.name
                kmp.meter = mdiff
            break
        else:
            lpoint = rpoint
            rpoint = kmpoints[i]
            curdiff = nxtdiff
            nxtdiff = geopy.distance.vincenty((rpoint.lat, rpoint.lon),(targetpoint.lat, targetpoint.lon)).km
            # print(lpoint['name'],"curdiff",curdiff,rpoint['name'],"nxtdiff",nxtdiff)
    # print("most close point at " + str(lpoint))
    # print("kmp:" + str(kmp))
    return kmp
