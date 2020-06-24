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
    # print(targetpoint)
    kmp = findclosepoint(kmpoints, targetpoint)
    if(not hasattr(kmp, 'name')):
        kmp.name = "KFFF+000"
        kmp.meter = 0
    # print("kmp:" + str(kmp))
    kmfo = kmp.name.split("+")
    kmp.kmfo = kmfo[0] + "+" + (str)(round((float)(kmfo[1]) + kmp.meter, 2))
    return kmp

def findclosepoint(points, targetpoint, thresh=0.1, debug=False):
    lpoint = points[0]
    rpoint = points[1]
    curdiff = geopy.distance.geodesic((lpoint.lat, lpoint.lon),(targetpoint.lat,targetpoint.lon)).km
    nxtdiff = geopy.distance.geodesic((rpoint.lat, rpoint.lon),(targetpoint.lat,targetpoint.lon)).km
    kmp = SimpleNamespace()
    if(debug):print("distance thresh = {0}".format(thresh))
    for i in range(2,len(points)):
        if(curdiff < nxtdiff and curdiff <= thresh):
            mdiff = geopy.distance.geodesic((lpoint.lat, lpoint.lon),(targetpoint.lat, targetpoint.lon)).km*1000
            if(debug):print("mdiff = {0}".format(mdiff))
            if(nxtdiff >= 0.1):
                kmp.name = points[lpoint.index - 1].name
                kmp.meter = thresh*1000 - mdiff
            else:
                kmp.name = lpoint.name
                kmp.meter = mdiff
            break
        else:
            lpoint = rpoint
            rpoint = points[i]
            curdiff = nxtdiff
            nxtdiff = geopy.distance.geodesic((rpoint.lat, rpoint.lon),(targetpoint.lat, targetpoint.lon)).km
            if(debug):print(lpoint.name,"curdiff",curdiff,rpoint.name,"nxtdiff",nxtdiff)
    if(debug):print("most close point at " + str(lpoint))
    return kmp

if __name__ == "__main__":
    kmpoints = getkmpoints()
    p = SimpleNamespace(lat = 24.3392393, lon = 120.6249646)
    kmp = kmplush(kmpoints, p)
    print(kmp)
    pass