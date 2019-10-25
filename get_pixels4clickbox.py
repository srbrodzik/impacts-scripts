#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 13:48:32 2019

@author: broneil

Creates an ascii file defined by 'text_output_name' whose contents can replace
map definitions in /home/disk/funnel/impacts/Home.html

Note for Brodzik - create input params for:
   'size' of box (parameter to 'get_box_crnr')
"""

import numpy as np
import pickle
import cv2

#Global Variable
image_dir = '/home/disk/funnel/impacts'
#image_name = image_dir+'/IMPACTS_precip_map.png'
image_name = image_dir+'/IMPACTS_map.png'
pickle_jar = '/home/disk/bob/impacts/bin/pickle_jar'
html_plots_url = 'http://impacts.atmos.washington.edu/tmp_asos_dir'
text_output_dir = '/home/disk/funnel/impacts'
text_output_name = 'clickable_boxes.txt'

def load_us_asos():
    # add ASOS sites
    infile = open(pickle_jar + "/ASOS_stations.pkl",'rb')
    ASOS_us = pickle.load(infile)
    infile.close()
    return ASOS_us

def load_ca_asos():
    #Candadian Stations
    canadafile = open(pickle_jar + "/ASOS_canada_stations.pkl",'rb')
    ASOS_ca = pickle.load(canadafile)
    canadafile.close()
    return ASOS_ca

def merge_asos_dict(d1,d2):
    d1.update(d2)
    return d1

def get_box_crnr(lon,lat,size):
    '''Takes in the lon and lat of a station and will calculate the upper left corner 
       and lower right corner of the box in pixel coordinates of the Impacts domain based 
       on the size given in long/lat.
    '''
    #Getting box lat and longs from a size parameter
    left_lon = lon - size
    right_lon = lon + size
    upper_lat = lat + size
    lower_lat = lat - size
    
    #converting to pixel space
    left_pix = convert_geo2pixel(left_lon,False)
    right_pix = convert_geo2pixel(right_lon,False)
    upper_pix = convert_geo2pixel(upper_lat)
    lower_pix = convert_geo2pixel(lower_lat)
    
    nw_corner = [left_pix,upper_pix]
    se_corner = [right_pix,lower_pix]
    
    return nw_corner,se_corner
    
def convert_geo2pixel(coord,Latitude=True):
    '''Takes in a coordinate in the geographic space and converts it to pixel space.
       If the latitude flag is set to false, then the pixel will assume a longitude coordinate...
    '''
    #Ranges of long and lat of the figure domain
    lon_ext = 15.5
    lat_ext = 11.8
    
    # Highest Latitude
    high_lat = 48.0
    
    # Westerly Lon
    west_lon = -82.0
    
    #########Getting the corner pixel values of the actual figure rather than of the axis
    l_min, up_min, r_max, low_max = get_corners(image_name)
    # Ranges of pixels in the figure that represent lon/lats
    vert_pixel_ext = low_max - up_min
    horiz_pixel_ext = r_max - l_min
    
    # Pixel coordinate is converted by evaluating how far the coordinate spans the range
    # in GEO space, which translates to pixel space by adding in the extra white space from the figure
    if Latitude == True:
        depth_percentage = (high_lat - coord)/lat_ext
        pixel_coord = int(vert_pixel_ext * depth_percentage)  + up_min
    elif Latitude == False: #Longitude case
        depth_percentage =  (coord - west_lon)/lon_ext
        pixel_coord = int(horiz_pixel_ext * depth_percentage)  + l_min    
    return pixel_coord
    
def get_corners(image_name):
    '''Reads in an image and calculates the pixel positions of figure corners within the whitespace of the axes.
    '''
    im = cv2.imread(image_name,1) #Calculates the pixel values and ignores transperancy 
    black_pixels = np.where(im.sum(2) < 500) #Sums the pixels together, and gets the indices of pixel sum values of less than 500

    ycoords = black_pixels[0] 
    xcoords = black_pixels[1]
    
    #Finding the right most boundry pixel
    r_max = xcoords.max()
    #Gets the indices of the right boundry
    r_bounds = np.where(xcoords == r_max)
    #Gets the y values of the right boundry
    r_ycoords = ycoords[r_bounds]
    #Highest y value of the right boundry (minimum value)
    up_min = r_ycoords.min() 
    #Lowest y value of the right boundry (maximum value)
    low_max = r_ycoords.max() 
    #Gets the x values of the upper boundry
    up_bounds = np.where(ycoords == up_min)
    #Finds the left boundry (minimum x value)
    l_min = xcoords[up_bounds].min()

    return l_min, up_min, r_max, low_max

def write_box2txt(nw_corner,se_corner,station,name):
    '''Uses the coordinates of the box to print out an ascii line to a txt file that 
       will be used to make clickabe boxes.
    '''
    with open(text_output_dir+'/'+text_output_name,'a') as f:

        line = ('                <area shape=\"rect\" coords=\"%s,%s,%s,%s\" alt=\"%s\" href=\"%s/%s.html\" title=\"%s\">\n'
               % (nw_corner[0],nw_corner[1],se_corner[0],se_corner[1],station,html_plots_url,station.lower(),name))
        f.write(line)

def get_box_and_write2txt(ASOS,asos_keys):
    '''Takes in a dictionary of all stations and the keys of the plotted data.
       Outputs a txt file of the box dimensions for the figure and the name of the station and location of the atmospheric field plots.
    '''
    for station in asos_keys:
        lon = ASOS[station][2]
        lat = ASOS[station][3]    
        name = ASOS[station][0]
        nw_corner,se_corner = get_box_crnr(lon,lat,.2)
        write_box2txt(nw_corner,se_corner,station,name)

def main():
    
    ASOS_us = load_us_asos()
    ASOS_ca = load_ca_asos()
    ASOS = merge_asos_dict(ASOS_us,ASOS_ca)
    with open(pickle_jar + "/asos_keys.pkl",'rb') as f:
        asos_keys = pickle.load(f)
    
    get_box_and_write2txt(ASOS,asos_keys)
    
    
main()
    
