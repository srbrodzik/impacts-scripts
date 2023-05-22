#!/usr/bin/python3

import os

indir = '/home/snowband/brodzik/Downloads/IMPACTS/upperair/dropsondes/20230115'

os.chdir(indir)
for file in os.listdir(indir):
    if file.endswith('kml'):
        fileOut = file+'.new'
        #fin = open(file,'r')
        fout = open(fileOut,'w')

        # read input file
        rawfile = open(file, encoding="latin-1").readlines()
        lastLines = rawfile[-24:]
        header = lastLines[0:11]
        footer = lastLines[-2:]
        numLines = len(rawfile)

        for ihead in header:
            fout.write(ihead)

        lookForStart = 1
        for iline in range(0,numLines):
            line = rawfile[iline]
            print(line)

            if lookForStart:
                if '<Placemark>' not in line:
                    print('continue')
                else:
                    fout.write(line)
                    lookForStart = 0
            else:
                if '</Placemark>' not in line:
                    fout.write(line)
                else:
                    fout.write(line)
                    lookForStart = 1

        for iline in footer:
            fout.write(iline)

        #fin.close()
        fout.close()
           

