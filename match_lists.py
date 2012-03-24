#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################################
## This file matches the OSM and Metropotam files agains each other      ##
## following some criteria                                               ##
##                                                                       ##
## Copyright Strainu <strainu@strainu.ro> 2012                           ##
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

class MatchOSMMetroData:

    def __init__(self):
	pass

    def compare(self):
        f = open("centru_vechi_osm.json", "r")
        osm_data = json.load(f)
        f.close()
        
        f = open("metropotam.json", "r")
        metro_data = json.load(f)
        f.close();
        
        amenity_coresp = {
        'Restaurante': 'restaurant',
        'Cluburi': 'nightclub',
        'Baruri': 'bar',
        'Cafenele': 'cafe',
        'Terase': 'cafe',#FIXME
        'Magazine': 'shop',
        'Hoteluri': 'hotel',
        'Galerii': 'gallery',
        'Muzee': 'museum',
        'Ceainarii': 'teahouse',#TODO
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
                    if not place['type'] in stuff['type']:
                        # TODO: these probably need to be updated from Metropotam, but keeping the OSM coords
                        print 'Types do not match for %s/%s: %s vs %s' % (place['name'], stuff['name'], place['type'], str(stuff['type']))
                        continue
                    lat_diff = math.fabs(place['lat'] - stuff['lat']) * 111000 #in m
                    lon_diff = math.fabs(place['lon'] - stuff['lon']) * 70000  #in m
                    distance = math.sqrt(lat_diff * lat_diff + lon_diff * lon_diff)
                    if distance > 100:
                        #TODO: not sure about these; they could well be the same
                        print '%s is too far away from %s' % (place['name'], stuff['name'])
                        continue
                    count += 1
                    #TODO: these can be safely ignored
                    print "%d. OSM: %s(%f,%f), Metropotam: %s(%f,%f); type: %s; distance: %f" % (count, place['name'], place['lat'], place['lon'], stuff['name'], stuff['lat'], stuff['lon'], place['type'], distance)
                    #print stuff['id']

if __name__ == "__main__":
    acceptall = False
    for args in sys.argv[1:]:
        if arg == "-always":
            acceptall = True
    robot = MatchOSMMetroData()
    robot.compare()
