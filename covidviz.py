#!/usr/bin/env python3.5

import re
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import http.client
import collections
import requests
import csv
import json
from datetime import datetime


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
        dct[r]['barw'] = []
        print(r)
        lnc = len(dct[r]['newcases'])
        ld = len(dct[r]['dates'])
        for d in dct[r]['dates'][(ld-lnc):]:
            dt = datetime.strptime(d, '%m/%d/%Y')
            ds = datetime.strftime(dt, '%A')
            # print(ds)
            if ds == 'Monday':
                if weekd:
                    dct[r]['weekd'].append(weekd[0])
                    dct[r]['weeknc'].append(np.average(weekv))
                    dct[r]['barw'].append(len(weekv)-0.2)
                    # print(weekv)
                    weekd = []
                    weekv = []
            weekd.append(d)
            weekv.append(dct[r]['newcases'][i])
            i += 1
        dct[r]['weekd'].append(weekd[0])
        dct[r]['weeknc'].append(np.average(weekv))
        dct[r]['barw'].append(len(weekv)-0.2)

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

chilehttp = 'https://raw.githubusercontent.com/jorgeperezrojas/covid19-data/master/csv/confirmados.csv'
# conncl = http.client.HTTPSConnection("chile-coronapi.herokuapp.com")
# conncl.request('GET', '/api/v3/historical/regions')
# rescl = conncl.getresponse()
# datacl = rescl.read().decode('utf-8')
# print(datacl)

# dictcl = json.loads(datacl, object_pairs_hook=collections.OrderedDict)

rawcl = requests.request('GET', chilehttp)
rawreader = csv.reader((io.StringIO(rawcl.content.decode('utf-8'))), delimiter=',')

dataclArray = []
for r in rawreader:
    dataclArray.append(r)

state = 'MD'
# state = 'CA'
connus = http.client.HTTPSConnection("covidtracking.com")
connus.request('GET', '/api/v1/states/md/daily.json')
# connus.request('GET', '/api/v1/states/ca/daily.json')
resus = connus.getresponse()
dataus = resus.read().decode('utf-8')

dictus = json.loads(dataus, object_pairs_hook=collections.OrderedDict)

pltdatacl = {}

for row in dataclArray:
    if 'codigo' in row:
        dates = [dt+'0' if re.search(r'202\b',dt) else dt for dt in row[2:]]
        continue
    if row[0] == '0':
        continue
    pltdatacl[row[1]] = {}
    pltdatacl[row[1]]['totcases'] = [int(x) for x in row[2:]]
    pltdatacl[row[1]]['dates'] = dates
    pltdatacl[row[1]]['newcases'] = diffData(pltdatacl[row[1]]['totcases'])


# for r in dictcl:
    # region = dictcl[r]['region']
    # pltdatacl[region]={}
    # pltdatacl[region]['dates'] = []
    # pltdatacl[region]['totcases'] = []
    # for d in dictcl[r]['regionData']:
        # val = dictcl[r]['regionData'][d]['confirmed']
        # pltdatacl[region]['dates'].append(d)
        # pltdatacl[region]['totcases'].append(val)
    # pltdatacl[region]['newcases'] = diffData(pltdatacl[region]['totcases'])
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
dmd = [pltdataus['MD']['weekd'], pltdataus['MD']['weeknc']]
# dmd = [pltdataus['CA']['weekd'], pltdataus['CA']['weeknc']]
print(pltdatacl['Coquimbo']['weeknc'])
print(pltdataus['MD']['weeknc'])
# print(pltdataus['CA']['weeknc'])
print(pltdataus['MD']['barw'])

cmapaux = [colormap['-100->-50%'] if ((x-y)/y) < -0.5 else
        colormap['-50->-5%'] if ((x-y)/y) >= -0.5 and ((x-y)/y) < -0.05 else
        colormap['-5->5%'] if ((x-y)/y) >= -0.05 and ((x-y)/y) < 0.05 else
        colormap['5->50%'] if ((x-y)/y) >= 0.05 and ((x-y)/y) < 0.5 else
        colormap['50->100%'] if ((x-y)/y) >= 0.5 and ((x-y)/y) < 1.0 else
        colormap['+100%'] for x,y in np.array([dmd[1][1:], dmd[1][:-1]]).T]
        # colormap['+100%'] for x,y in np.array([dc[1][1:], dc[1][:-1]]).T]

cmapmd = ['xkcd:off white'] + cmapaux

cmapauxc = [colormap['+100%'] if y == 0.0 else
        colormap['-100->-50%'] if ((x-y)/y) < -0.5 else
        colormap['-50->-5%'] if ((x-y)/y) >= -0.5 and ((x-y)/y) < -0.05 else
        colormap['-5->5%'] if ((x-y)/y) >= -0.05 and ((x-y)/y) < 0.05 else
        colormap['5->50%'] if ((x-y)/y) >= 0.05 and ((x-y)/y) < 0.5 else
        colormap['50->100%'] if ((x-y)/y) >= 0.5 and ((x-y)/y) < 1.0 else
        colormap['+100%'] for x,y in np.array([dc[1][1:], dc[1][:-1]]).T]

cmapc = ['xkcd:off white'] + cmapauxc

dlabels = [x if datetime.strftime(datetime.strptime(x,'%m/%d/%Y'), '%A') == 'Monday' else
          '' for x in pltdataus['MD']['dates']]
dlabelscl = [x if datetime.strftime(datetime.strptime(x,'%m/%d/%Y'), '%A') == 'Monday' else
             '' for x in pltdatacl['Coquimbo']['dates'][1:]]

print(len(pltdataus['MD']['dates']), pltdataus['MD']['dates'][0], pltdataus['MD']['dates'][-1])
print(len(pltdatacl['Coquimbo']['dates']), pltdatacl['Coquimbo']['dates'][0], pltdatacl['Coquimbo']['dates'][-1])
xlimcl = len(pltdatacl['Coquimbo']['dates'])
xlimus = len(pltdataus['MD']['dates'])
# xlim = np.max([xlimcl, xlimus])

fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
ax1 = fig.add_subplot(2,1,1)
ax2 = fig.add_subplot(2,1,2)
fig.subplots_adjust(right=0.8, top=0.9, bottom=0.1)
cbax = fig.add_axes([0.8125,0.1,0.0175,0.8])
title = 'Covid daily new cases\n' + 'bar: week average\n' + 'line: daily'
fig.suptitle(title)

ax1.plot(pltdataus['MD']['dates'],
         pltdataus['MD']['newcases'],
         '.b--')
ax1.bar(dmd[0], dmd[1], color=cmapmd, width=pltdataus['MD']['barw'], align='edge')
ax2.plot(pltdatacl['Coquimbo']['dates'][1:],
         pltdatacl['Coquimbo']['newcases'],
         '.b--')
ax2.bar(dc[0], dc[1], color=cmapc, width=pltdatacl['Coquimbo']['barw'], align='edge')
# ax2.bar(dc[0], dc[1], color=cmapc)

cmpl = mpl.colors.ListedColormap(colorarray)
bounds = [-100,-50,-5,5,50,100,150]
# tlabels = ['-100%','-50%','-5%','5%','50%','100%','>100%']
tlabels = ['x0.0','x0.5','x0.95','x1.05','x1.5','>x2.0','']
norm = mpl.colors.BoundaryNorm(bounds, cmpl.N)
cb = plt.cm.ScalarMappable(cmap=cmpl, norm=norm)
cb.set_array([])

# plt.yscale('log')
ax1.set_xticklabels(dlabels)
ax1.set_ylabel('New Cases per day\nMaryland')
ax1.grid(axis='y')
ax2.set_xticklabels(dlabelscl)
ax2.set_ylabel('New Cases per day\nCoquimbo')
ax2.grid(axis='y')
# plt.setp(ax1.get_xticklabels(), visible=False)
plt.setp(ax1.get_xticklabels(), fontsize=9,
                        rotation=30, ha='right')
plt.setp(ax2.get_xticklabels(), fontsize=9,
                        rotation=30, ha='right')
# ax1.set_xlim(0, xlimus)
ax1.set_xlim(3, xlimus+(3-(xlimus-xlimcl)))
ax2.set_xlim(0, xlimcl)
cmplt = fig.colorbar(cb, cax=cbax, boundaries=bounds)
cmplt.ax.set_yticklabels(tlabels)
# plt.setp(ax1.get_xticklabels()[::2], visible=False)
plt.show()
