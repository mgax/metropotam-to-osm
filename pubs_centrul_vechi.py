﻿#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################################
## Bla blab blb                                                          ##
##                                                                       ##
## Copyright Strainu <strainu@strainu.ro> 2010                           ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, version 2.                              ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import OsmApi, xml.dom.minidom, csv, urllib2, urllib, string, time, sys, json, math

class ExtractPubData:

    def __init__(self):
        self._passfile = "osmpasswd"
        self._log = "pubs_export.log"
        self._area = "26.0965,44.43,26.1075,44.4347"
        self._comment = "Automated postcode import from SIRUTA 2008 (batch %d). Source: http://www.insse.ro/cms/rw/pages/siruta.ro.do "
        self._batch = 0
        self._record_count = 0
        self._always = all

    def log(self, header, string):
        f = open(self._log, 'a+')
        #f.write(header.encode( "utf-8" ) + string.encode( "utf-8" ))
        print header.encode( "utf-8" ) + string.encode( "utf-8" )
        f.write("\n")
        f.close()

    def logi(self, string):
        self.log("* Info (%s): " % time.strftime("%Y-%m-%d %H:%M:%S"), string)

    def loge(self, string):
        self.log("* Error (%s): " % time.strftime("%Y-%m-%d %H:%M:%S"), string)

    def logd(self, string):
        self.log("* Debug (%s): " % time.strftime("%Y-%m-%d %H:%M:%S"), string)

    def pageText(self, url):
        """ Function to load HTML text of a URL """
        try:
            request = urllib2.Request(url)
            request.add_header("User-Agent", "siruta_postcodes.py 1.0")
            response = urllib2.urlopen(request)
            text = response.read()
            response.close()
            # When you load to many users, urllib2 can give this error.
        except urllib2.HTTPError, urllib2.URLError:
            self.loge(u"Server or connection error. Pausing for 10 seconds... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
            response.close()
            time.sleep(10)
            return pageText(url)
        return text

    def searchAmenities(self):
        #urlHead = "http://osmxapi.hypercube.telascience.org/api/0.6/node[amenity="
        urlHead = "http://open.mapquestapi.com/xapi/api/0.6/node[amenity="
        data = []
        for amenity in ['drinking_water', 'bar', 'bbq', 'biergarten', 'cafe', 'fast_food', 'food_court', 'ice_cream', 'pub', 'restaurant', 'nightclub', 'cinema', 'theatre']:
            url = urlHead + amenity + "][bbox=" + self._area + "]"
            print url
            xmlText = self.pageText(url)

            try:
                document = xml.dom.minidom.parseString(xmlText)
                nodes = document.getElementsByTagName("node")
                #if len(nodes) > 0:
                #    print nodes[0].__class__
                #import pdb;
                #pdb.set_trace()
                for node in nodes:
                    place = {}
                    place['type'] = amenity
                    place['id'] = node.getAttribute('id')
                    place['lat'] = float(node.getAttribute('lat'))
                    place['lon'] = float(node.getAttribute('lon'))
                    print place
                    for tag in node.childNodes:
                        if tag.nodeType != tag.ELEMENT_NODE:
                            continue
                        if tag.tagName != "tag" or tag.hasAttribute('k') == False or tag.hasAttribute('v') == False:
                            continue
                        if tag.getAttribute('k') == "name":
                            xml_name = string.lower(tag.getAttribute('v'))
                            xml_name = string.replace(xml_name, u'ă', u'a')
                            xml_name = string.replace(xml_name, u'â', u'a')
                            xml_name = string.replace(xml_name, u'î', u'i')
                            xml_name = string.replace(xml_name, u'ş', u's')
                            xml_name = string.replace(xml_name, u'ș', u's')
                            xml_name = string.replace(xml_name, u'ţ', u't')
                            xml_name = string.replace(xml_name, u'ț', u't')
                            xml_name = string.replace(xml_name, u'—', u'-')
                            xml_name = string.replace(xml_name, u'–', u'-')

                            place['name'] = xml_name
                    #print place
                    data.append(place)
            except Exception as inst:
                self.loge("Generic error: " + str(inst))
                return 0
             
        #print data
        f = open("centru_vechi_osm.json", "w+")
        json.dump(data, f, indent=True)
        f.close()

    def compare(self):
        f = open("centru_vechi_osm.json", "r")
        osm_data = json.load(f)
        f.close()
        
        f = open("metropotam.json", "r")
        metro_data = json.load(f)
        f.close();
        
        amenity_coresp = {
        'Restaurante': 'restaurant',
        'Cluburi': 'club',
        'Baruri': 'bar',
        'Cafenele': 'cafe',
        'Terase': 'cafe',#FIXME
        'Magazine': 'shop',
        'Hoteluri': 'hotel',#TODO
        'Galerii': 'gallery',
        'Muzee': 'museum',#TODO
        'Ceainarii': 'tea_house',#TODO
        'Teatre': 'theatre',
        'Alte-locuri': 'other',#FIXME
        'Cinematografe': 'cinema',
        }
        
        new_metro_data = []
        for stuff in metro_data:
            new_stuff = stuff
            new_stuff['name'] = string.lower(stuff['name'])
            types = stuff['type'].split(', ')
            new_types = []
            for tip in types:
                new_types.append(amenity_coresp[tip])
            new_stuff['type'] = new_types
            new_metro_data.append(new_stuff)
        
        count = 0
        for place in osm_data:
            for stuff in new_metro_data:
                if place['name'].find(stuff['name']) > -1 or \
                    stuff['name'].find(place['name']) > -1: #TODO: use Levenshtein_distance
                    lat_diff = math.fabs(place['lat'] - stuff['lat']) * 111000 #in m
                    lon_diff = math.fabs(place['lon'] - stuff['lon']) * 70000  #in m
                    distance = math.sqrt(lat_diff * lat_diff + lon_diff * lon_diff)
                    if distance > 100:
                        continue
                    count += 1
                    #print "%d. OSM: %s(%f,%f), Metropotam: %s(%f,%f); type: %s, %s; distance: %f" % (count, place['name'], place['lat'], place['lon'], stuff['name'], stuff['lat'], stuff['lon'], place['type'], str(stuff['type']), distance)
                    print stuff['id']

if __name__ == "__main__":
    acceptall = False
    for args in sys.argv[1:]:
        if arg == "-always":
            acceptall = True
    robot = ExtractPubData()
    #robot.searchAmenities()
    robot.compare()