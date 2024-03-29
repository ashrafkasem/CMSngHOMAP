#!/usr/bin/env python
import os
import sys
import shutil 
import pandas as pd 
outDir = sys.argv[1]

if os.path.exists(outDir) : shutil.rmtree(outDir)

to_merge = os.path.join(outDir,'text_aligned')

print (10*"======")
print (5*"======","mapping crate 23",5*"======")
print (10*"======")
os.system('python makeMap.py 23 '+outDir+" Y")
print (10*"======")
print (5*"======","mapping crate 26",5*"======")
print (10*"======")
os.system('python makeMap.py 26 '+outDir+" N")
print (10*"======")
print (5*"======","mapping crate 27",5*"======")
print (10*"======")
os.system('python makeMap.py 27 '+outDir+" N")
print (10*"======")
print (5*"======","mapping crate 33/38",5*"======")
print (10*"======")
os.system('python makeMap.py 33 '+outDir+" N")

print (10*"======")
print (5*"======","now to merge all Emaps",5*"======")
print (10*"======")

with open(to_merge+'/ngHO_Emap_allCates_alligned.txt','wb') as wfd:
    for f in [to_merge+'/Emap_ngHO_c23_aligned.txt',to_merge+'/Emap_ngHO_c26_aligned.txt',to_merge+'/Emap_ngHO_c27_aligned.txt',to_merge+'/Emap_ngHO_c33_aligned.txt',to_merge+'/Emap_ngHOCalib_aligned.txt']:
        with open(f,'rb') as fd:
            shutil.copyfileobj(fd, wfd)
print (10*"======")
print (5*"======","now to merge all Trig Lmaps",5*"======")
print (10*"======")

with open(to_merge+'/Trig_LMap_allCates_alligned.txt','wb') as wfd:
    for f in [to_merge+'/Trig_LMap_ngHO_c23_aligned.txt',to_merge+'/Trig_LMap_ngHO_c26_aligned.txt',to_merge+'/Trig_LMap_ngHO_c27_aligned.txt',to_merge+'/Trig_LMap_ngHO_c33_aligned.txt']:
        with open(f,'rb') as fd:
            shutil.copyfileobj(fd, wfd)

print (10*"======")
print (5*"======","now to merge all Lmaps",5*"======")
print (10*"======")

with open(to_merge+'/ngHO_Lmap_allCates_alligned.txt','wb') as wfd:
    for f in [to_merge+'/Lmap_c23_aligned.txt',to_merge+'/Lmap_c26_aligned.txt',to_merge+'/Lmap_c27_aligned.txt',to_merge+'/Lmap_c33_aligned.txt',to_merge+'/Lmap_ngHOCalib_aligned.txt']:
        with open(f,'rb') as fd:
            shutil.copyfileobj(fd, wfd)

lines_seen = set() # holds lines already seen
outfile = open(to_merge+'/ngHO_Lmap_allCates_alligned_.txt', "w")
for line in open(to_merge+'/ngHO_Lmap_allCates_alligned.txt', "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

lines_seen = set() # holds lines already seen
outfile = open(to_merge+'/Trig_LMap_allCates_alligned_.txt', "w")
for line in open(to_merge+'/Trig_LMap_allCates_alligned.txt', "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()

lines_seen = set() # holds lines already seen
outfile = open(to_merge+'/ngHO_Emap_allCates_alligned_.txt', "w")
for line in open(to_merge+'/ngHO_Emap_allCates_alligned.txt', "r"):
    if line not in lines_seen: # not a duplicate
        outfile.write(line)
        lines_seen.add(line)
outfile.close()


os.system("mv "+to_merge+'/ngHO_Emap_allCates_alligned_.txt '+to_merge+'/ngHO_Emap_allCates_alligned.txt')
os.system("mv "+to_merge+'/ngHO_Lmap_allCates_alligned_.txt '+to_merge+'/ngHO_Lmap_allCates_alligned.txt')
os.system("mv "+to_merge+'/Trig_LMap_allCates_alligned_.txt '+to_merge+'/Trig_LMap_allCates_alligned.txt')
