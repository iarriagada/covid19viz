#!/usr/bin/env python3.5

import re
import csv
import h5py
import numpy as np
import os.path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import http.client
import collections
import json
# import matplotlib.animation as animation


def diffData(dataA):
    '''
    This function is used to calculate the differential of the values of an
    array between consecutive samples
    '''
    diffPV = [y - x \
               for x,y in np.array([dataA[:-1],
                                    dataA[1:]]).T]
    return diffPV

def WeekAve(dct):
    for r in dct:
        weekv = []
        weekd = []
        i = 0
        dct[r]['weekd'] = []
        dct[r]['weeknc'] = []
        print(r)
        lnc = len(dct[r]['newcases'])
        ld = len(dct[r]['dates'])
        # print(lnc)
        # print(ld)
        for d in dct[r]['dates'][(ld-lnc):]:
            dt = datetime.strptime(d, '%m/%d/%Y')
            ds = datetime.strftime(dt, '%A')
            # print(ds)
            if ds == 'Monday':
                if weekd:
                    dct[r]['weekd'].append(weekd[0])
                    dct[r]['weeknc'].append(np.average(weekv))
                    # print(weekv)
                    weekd = []
                    weekv = []
            weekd.append(d)
            weekv.append(dct[r]['newcases'][i])
            i += 1
        dct[r]['weekd'].append(weekd[0])
        dct[r]['weeknc'].append(np.average(weekv))

colorarray = ['xkcd:azure',
            'xkcd:powder blue',
            'xkcd:off white',
            'xkcd:yellowish',
            'xkcd:golden',
            'xkcd:deep orange']

colormap = {'-100->-50%':colorarray[0],
            '-50->-5%':colorarray[1],
            '-5->5%':colorarray[2],
            '5->50%':colorarray[3],
            '50->100%':colorarray[4],
            '+100%':colorarray[5]}

conncl = http.client.HTTPSConnection("chile-coronapi.herokuapp.com")
conncl.request('GET', '/api/v3/historical/regions')
rescl = conncl.getresponse()
datacl = rescl.read().decode('utf-8')

dictcl = json.loads(datacl, object_pairs_hook=collections.OrderedDict)

# state = 'MD'
state = 'CA'
connus = http.client.HTTPSConnection("covidtracking.com")
# connus.request('GET', '/api/v1/states/md/daily.json')
connus.request('GET', '/api/v1/states/ca/daily.json')
resus = connus.getresponse()
dataus = resus.read().decode('utf-8')

dictus = json.loads(dataus, object_pairs_hook=collections.OrderedDict)

pltdatacl = {}
for r in dictcl:
    region = dictcl[r]['region']
    pltdatacl[region]={}
    pltdatacl[region]['dates'] = []
    pltdatacl[region]['totcases'] = []
    for d in dictcl[r]['regionData']:
        val = dictcl[r]['regionData'][d]['confirmed']
        pltdatacl[region]['dates'].append(d)
        pltdatacl[region]['totcases'].append(val)
    pltdatacl[region]['newcases'] = diffData(pltdatacl[region]['totcases'])
    # print(pltdatacl[region]['newcases'])

pltdataus = {}
pltdataus[state]={}
dus = []
tcus = []
ncus = []
for d in dictus:
    dt = datetime.strptime(str(d['date']), '%Y%m%d')
    ds = datetime.strftime(dt, '%m/%d/%Y')
    dus.append(ds)
    tcus.append(d['positive'])
    ncus.append(d['positiveIncrease'])
dus.reverse()
tcus.reverse()
ncus.reverse()
pltdataus[state]['dates']=dus
pltdataus[state]['totcases']=tcus
pltdataus[state]['newcases']=ncus

WeekAve(pltdatacl)
WeekAve(pltdataus)

dc = [pltdatacl['Coquimbo']['weekd'], pltdatacl['Coquimbo']['weeknc']]
# dmd = [pltdataus['MD']['weekd'], pltdataus['MD']['weeknc']]
dmd = [pltdataus['CA']['weekd'], pltdataus['CA']['weeknc']]
print(pltdatacl['Coquimbo']['weeknc'])
# print(pltdataus['MD']['weeknc'])
print(pltdataus['CA']['weeknc'])

cmapaux = [colormap['-100->-50%'] if ((x-y)/y) < -0.5 else
        colormap['-50->-5%'] if ((x-y)/y) >= -0.5 and ((x-y)/y) < -0.05 else
        colormap['-5->5%'] if ((x-y)/y) >= -0.05 and ((x-y)/y) < 0.05 else
        colormap['5->50%'] if ((x-y)/y) >= 0.05 and ((x-y)/y) < 0.5 else
        colormap['50->100%'] if ((x-y)/y) >= 0.5 and ((x-y)/y) < 1.0 else
        colormap['+100%'] for x,y in np.array([dmd[1][1:], dmd[1][:-1]]).T]
        # colormap['+100%'] for x,y in np.array([dc[1][1:], dc[1][:-1]]).T]

cmap = ['xkcd:off white'] + cmapaux


print(cmap)



fig = plt.figure()
ax = plt.subplot()
ax.bar(dmd[0], dmd[1], color=cmap)
# ax.bar(dc[0], dc[1], color=cmap)
cmpl = mpl.colors.ListedColormap(colorarray)
bounds = [-100,-50,-5,5,50,100,150]
tlabels = ['-100%','-50%','-5%','5%','50%','100%','>100%']
norm = mpl.colors.BoundaryNorm(bounds, cmpl.N)
cb = plt.cm.ScalarMappable(cmap=cmpl, norm=norm)
cb.set_array([])
# plt.yscale('log')
plt.setp(ax.get_xticklabels(), fontsize=9,
                        rotation=30, ha='right')
cmplt = fig.colorbar(cb, boundaries=bounds)
cmplt.ax.set_yticklabels(tlabels)
# plt.setp(ax.get_xticklabels()[::2], visible=False)
plt.show()
