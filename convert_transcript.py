#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 09:07:47 2018

@author: lucalugini
"""

import  pandas as pd
import numpy as np
import re
import json
import requests
import os
import shutil
import re
from collections import Counter, defaultdict
from graphviz import Digraph, Graph
import collaboration_map_v2 as cm2

api_endpoint='http://0.0.0.0:34185/classify'

skipClassifier = False

def collaboration_converter(a):
    a = a.strip().upper()
    if a == 'N':
        return 'new'
    elif a == 'C':
        return 'challenge'
    elif a == 'E':
        return 'extension'
    elif a == 'A':
        return 'agree'
    elif a == 'NON':
        return 'Non'
    else:
        print("Got a weird collaboration code")
        print("***\n"+a+"***")
        raise SystemExit

def student_converter(a):
    a = a.strip()
    if len (a) > 0:
        if a[0].lower() == 't' or 'teacher' in a.lower():
            return 'teacher'
        elif "?" in a:
            return ""
        else:
            return re.sub("[^0-9]","",a)
    else:
        return ''

def turn_converter(a):
    if len(a.split(' ')) > 1:
        a = a.split(' ')[0]
    if len(a.split(',')) > 1:
        a = a.split(',')[0]
    return a.split('.')[-1].strip()

def talk_converter(a):
    if isinstance(a, str):
        return a.strip()
    else:
        return str(a).strip()

# json_data = json.load(open('data_api_test.json'))
# r = requests.post(url=api_endpoint, data={}, json=json_data)
# print(r.json())

# {"argmoves": ["I believe the main characters did not care about the others", "because at page 15 the main characters ran away",
#             "I also believe they did not care about the others and only cared about themselves",
#             "I don't agree, I believe they cared about the others because in the end they saved everyone"],
#     "turns": ["I believe the main characters did not care about the others because at page 15 the main characters ran away",
#             "I also believe they did not care about the others and only cared about themselves",
#             "I don't agree, I believe they cared about the others because in the end they saved everyone"],
#     "references": ["I believe the main characters did not care about the others because at page 15 the main characters ran away",
#             "I believe the main characters did not care about the others because at page 15 the main characters ran away",
#             "I also believe they did not care about the others and only cared about themselves"]
# }
def convert_transcript(f_str, useClassifier=False):
    print("Processing: ", f_str)

    converter = {'Disc id': turn_converter,
                 'Turn of Reference': turn_converter,
                 'Argument Segmentation': talk_converter,
                 'Talk': talk_converter,
                 'Sp id': student_converter,
                 }

    #if(not useClassifier):
    converter.update({'Claim': (lambda x: 'claim' if x else ''),
                'Evidence': (lambda x: 'evidence' if x else ''),
                'Warrant': (lambda x: 'explanation' if x else ''),
                'Low': (lambda x: 'low' if x else ''),
                'Med': (lambda x: 'med' if x else ''),
                'High': (lambda x: 'high' if x else ''),
                'Collaboration Code': (lambda x: collaboration_converter(x) if x else ''),
                })

    d = pd.read_excel(f_str, header=0, usecols=range(23), keep_default_na=False,
                      converters=converter)

    #if(not useClassifier):
    d['Argmove'] = d.Claim.str.cat(d.Evidence).str.cat(d.Warrant)
    d['Specificity'] = d['Low'].str.cat(d['Med']).str.cat(d['High'])

    #these are the expected columns 
    cols = ['Disc id', 'Sp id', 'Talk', 'Turn of Reference', 'Argument Segmentation']
    #if(not useClassifier):
    cols += ['Collaboration Code',  'Argmove', 'Specificity']


    data = pd.DataFrame.copy(d)
    data = data[cols]
    data = data.replace('', np.nan)
    data = data.dropna(axis=0, how='all').replace(np.nan, '')
    colConvert = {'Disc id': 'Turn', 'Sp id':'Student','Talk':'Talk', 'Argument Segmentation':'Talk2', 'Turn of Reference':'Reference'}
    #if(not useClassifier):
    colConvert.update({'Argmove':'ArgMove', 'Specificity':'Specificity', 'Collaboration Code':'Collaboration'})

    data.rename(index=str, columns=colConvert, inplace=True)

    turnList = []
    lastTurn = -1
    for idx, row in data.iterrows():
        if(row['Turn'] != lastTurn and row['Turn'] != ''):
            lastTurn = row['Turn']
            turnList.append({'TurnNum':lastTurn})
            turnList[-1]['Student'] = row['Student']
            turnList[-1]['RawText'] = row['Talk']
            turnList[-1]['Collaboration'] = row['Collaboration']
            turnList[-1]['Reference'] = row['Reference']
            #we assume that new ideas are linked to themselves
            if(row['Reference'] == '' and row['Collaboration'] == 'new'):
                turnList[-1]['Reference'] = lastTurn
            # turnList[-1]['RefText'] = row['RefText']
            turnList[-1]['Argumentation'] = [ {'Text':row['Talk2'], 'Specificity':row['Specificity'] , 'ArgMove':row['ArgMove']} ]
        else:
            turnList[-1]['Argumentation'].append( {'Text':row['Talk2'], 'Specificity':row['Specificity'] , 'ArgMove':row['ArgMove']} )


    if(useClassifier):
        print("using the classifier")
        #this is an associated list to put the
        #classified results back in
        assoc_list = {"arg_idx": [],
                    "turn_idx": []}
        #
        sent_data = {"argmoves": [],
                    "turns": [],
                    "references": []}

        #collect the turns that we can classify (not teacher turns and not non turns.
        for i in range(len(turnList)):
            turn = turnList[i]
            if(turn['Student'] != 'teacher' and turn['Collaboration'] != 'Non'):
                sent_data['turns'].append(turn['RawText'])
                for refTurn in turnList:
                    if(refTurn['TurnNum'] == turn['Reference']):
                        sent_data['references'].append(refTurn['RawText'])
                        break
                assoc_list['turn_idx'].append(i)
                for j in range(len(turn['Argumentation'])):
                    arg = turn['Argumentation'][j]
                    sent_data['argmoves'].append(arg['Text'])
                    assoc_list['arg_idx'].append((i,j))

        #print(json.dumps(assoc_list, indent = 2))
        #print(json.dumps(sent_data, indent=2))
        #expected response
        #{'argumentation': ['claim', 'evidence', 'explanation', 'claim'],
        # 'collaboration': ['new', 'extension', 'challenge'],
        # 'specificity': ['low', 'low', 'low', 'low']}
        try:
            r = requests.post(url=api_endpoint, data={}, json=sent_data)
            parse = r.json()
        except Exception as e:
            print(e)
            print("Something is not right. Check the if Classifer API is running well or not. ")
            if(skipClassifier):
                import random

                print("Temp override to test later functionality")
                parse ={
                    'argumentation': random.choices(
                        ['claim', 'evidence', 'explanation'], k = len(sent_data['argmoves'])),
                    'collaboration': random.choices(
                        ['new', 'extension', 'challenge', 'agree'], k = len(sent_data['turns'])),
                    'specificity':random.choices(
                        ['low', 'med', 'high'], k = len(sent_data['argmoves']))
                    }
            else:
                raise SystemExit
        cnt = 0
        for idx in assoc_list['turn_idx']:
            turnList[idx]['Collaboration'] = parse['collaboration'][cnt]
            cnt += 1

        assert cnt == len(assoc_list['turn_idx'])

        cnt = 0
        for idx, inx in assoc_list['arg_idx']:
            turnList[idx]['Argumentation'][inx]['ArgMove'] = parse['argumentation'][cnt]
            turnList[idx]['Argumentation'][inx]['Specificity'] = parse['specificity'][cnt]
            cnt += 1
        assert cnt == len(assoc_list['arg_idx'])

    #return a dictionary that contains the transcript name and
    #some summary statistics on the data
    
    retval = {}
    retval['TranscriptName'] = os.path.splitext(os.path.basename(f_str))[0]
    retval['turnList'] = turnList
    
    return retval

def gen_stats(transcriptDict, fName, teacherInfo, discussionInfo):
    """
    This will generate some statistics that it can find
    None if it doesn't know just yet
    """
    #discussion info and teacher info rows
    tRow = teacherInfo.loc[ teacherInfo['Teacher ID'] == fName[0] ]
    dRow = discussionInfo.loc[
        (discussionInfo['Teacher ID'] == fName[0]) &
        (discussionInfo['Discussion Number'] == int(fName[2])) &
        (discussionInfo['Discussion Session']==fName[1])
    ]
    #if the data found is empty then get the default row of T000 and named unknown
    if(tRow.empty):
        tRow = teacherInfo.loc[ teacherInfo['Teacher ID'] == 'T000']
    if(dRow.empty):
        dRow = discussionInfo.loc[discussionInfo['Teacher ID'] == 'T000']
    #some base counting
    retval = {}
    retval['NumTurns'] = len(transcriptDict['turnList'])
    retval['Date'] = dRow['Date'].values[0]
    retval['Teacher'] = tRow['Teacher Name'].values[0]
    retval['NumStudents'] = int(dRow['Number Students Present'].values[0])
    retval['Topic'] = dRow['Topic'].values[0]
    
    turnCounts = Counter( [turn['Student'] for turn in transcriptDict['turnList']] )
    retval['NumStudentSpeakers'] = len(turnCounts)-1
    
    s = 0 - turnCounts['teacher']
    for k in sorted(turnCounts):
        s += turnCounts[k]
        
    retval['AvgNumStudentTurns'] = s/retval['NumStudentSpeakers']
    retval['TeacherPercentage'] = turnCounts['teacher']/(s+turnCounts['teacher'])
    
    #some more complicated counting
    
    retval['graphData'] = {}
    retval['graphData'].update(labelCounts(transcriptDict['turnList']))

    #get strengths and weaknesses
    strength, weakness = compute_strengths_weaknesses(turnCounts, retval)
    retval['strengths'] = strength
    retval['weaknesses'] = weakness

    #construct the collaboration map and save the dot string
    dot = cm2.create_collaboration_map(transcriptDict['turnList'])
    retval['collabMap'] = {'source': dot.source}
    #retval['collabMap'] = dot.source
    dot.render("out", directory="img", format="svg")
    with open("img/out.svg", "r") as f:
        retval['collabMap']['svg'] = postProcessSVG(f.read())
        
    retval.update(transcriptDict)

    return retval


def postProcessSVG(svg):
    """
    Currently Does nothing
    """
    #print(svg)
    #print("======================================")
    #isolate the width, height, and viewbox attributes and maniputlate with string manip
    svg = re.sub("<svg", "<svg id=\"svg-id\"", svg)
    svg = re.sub("width=.* ", "width=\"100%\" ", svg)
    #print("\n".join(svg.split("\n")[6:10]))
    #print("======================================")
    svg = re.sub("height=.*", "height=\"840\" ", svg)
    #print("\n".join(svg.split("\n")[6:10]))
    #print("======================================")
    viewBox = re.findall("viewBox=\\\".+?\\\"", svg)
    #print("\n".join(svg.split("\n")[6:10]))
    #print("======================================")
    #print(viewBox)
    return svg
     

def labelCounts(turnList):
    
    collabCounts = {'new':0, 'challenge':0, 'agree':0, 'Non':0, '':0, 'extension':0}
    argMoveCount = {'claim':0, 'evidence':0, 'explanation':0, '':0}
    specifiCount = {'low':0, 'med':0, 'high':0, '':0}

    try:
        for turn in turnList:
            collabCounts[turn['Collaboration']] +=1
            for arg in turn['Argumentation']:
                argMoveCount[arg['ArgMove']] +=1
                specifiCount[arg['Specificity']] +=1
                # if((arg['Specificity'] =='' and arg['ArgMove']!='') or (arg['Specificity']!='' and arg['ArgMove']=='')):
                #     print("I got either an empty Specificity or Argumentation:\nSpecificity %s\nArgmove %s" %(arg['Specificity'], arg['ArgMove']))
                #     print("Turn: ", turn['TurnNum'], "\n")
                # if( turn['Collaboration']!='' and turn['Collaboration']!='Non' and arg['Specificity'] =='' and arg['ArgMove']==''):
                #     print("I got a Collaboration Code with no Argument move labels (Specificity or Argumentation)")
                #     print("Collaboration Code: ", turn['Collaboration'])
                #     print("Turn: ", turn['TurnNum'])
                #     print()
    except Exception as e:
        print(e)
        print("\n\nSome details: TurnNum ", turn['TurnNum'] )
            
    del collabCounts['']
    del collabCounts['Non']
    del argMoveCount['']
    del specifiCount['']
    
    return {'collabCount':dict(collabCounts), 'argMoveCount':dict(argMoveCount), 'specifiCount':dict(specifiCount)}

def compute_strengths_weaknesses(turnCounts, stats):
    # compute strengths and weaknesses for the discussion
    #arg_data = metadata['argumentation']
    #spec_data = metadata['specificity']
    #col_data = metadata['collaboration']
    #student_turns = stats['turns']*(100-stats['teacher_turns'])

    #these lists will fill with indexes for the messages they correspond to lists down the line
    strengths = []
    weaknesses = []
    #compute if teacher talked too much
    if stats['TeacherPercentage'] >  0.25:
        weaknesses.append(0)
    else:
        strengths.append(0)
    #ratio of claims to evidence is below 2:1 (said enough evidence to support)
    if (stats['graphData']['argMoveCount']['claim']/stats['graphData']['argMoveCount']['evidence']) > 2:
        weaknesses.append(1)
    else:
        strengths.append(1)
    #The students said enough supporting turns (enough extension)
    #compute sum of collaborative moves because it does not include teacher talk as the 'NumTurns' field does
    collabMoves = sum(stats['graphData']['collabCount'].values())
    if stats['graphData']['collabCount']['extension']/collabMoves < 0.5:
        weaknesses.append(2)
    else:
        strengths.append(2)
    #ratio of evidence to explanation is below 2:1 (said enough explanation to support evidence)
    if (stats['graphData']['argMoveCount']['evidence']/max(stats['graphData']['argMoveCount']['explanation'], 1)) > 2:
        weaknesses.append(3)
    else:
        strengths.append(3)
    # More than two-thirds of the students spoke
    if  stats['NumStudentSpeakers']/stats['NumStudents'] < 0.67:
        weaknesses.append(4)
    else:
        strengths.append(4)
    # There is enough high specificity talk
    if stats['graphData']['specifiCount']['low'] + stats['graphData']['specifiCount']['med']*2 + stats['graphData']['specifiCount']['high']*2 < 2.2:
        weaknesses.append(5)
    else:
        strengths.append(5)
    #
    if stats['graphData']['collabCount']['challenge']/collabMoves < 0.1:
        weaknesses.append(6)
    else:
        strengths.append(6)
    
    return strengths, weaknesses

def readMetaData(f_str):
    teacherInfo = pd.read_excel(f_str, sheet_name="TeacherInfo")
    discussionInfo = pd.read_excel(f_str, sheet_name="DiscussionInfo")

    teacherInfo.fillna(value=dict(teacherInfo.iloc[0]), inplace=True)
    discussionInfo.fillna(value=dict(discussionInfo.iloc[0]), inplace=True)

    #print(teacherInfo.loc[teacherInfo['Teacher ID'] == "T124"])
    #print(discussionInfo.loc[(discussionInfo['Teacher ID']=='T124') & (discussionInfo['Discussion Number'] == 2)])

    return teacherInfo, discussionInfo


def batchProcessTranscripts(basepath, metadaPath, useClassifier=False):

    teacherInfo, discussionInfo = readMetaData(os.path.join(metadaPath, "Teacher Discussion Metadata.xlsx"))
    toProcess = sorted([ x for x in os.listdir(basepath) if x.endswith("xlsx")])

    for x in toProcess:
        #print(x)
        split = x.split(".")

        #make a folder for each teacher
        if(not os.path.exists(os.path.join(basepath,split[0])) ):
            os.mkdir( os.path.join(basepath,split[0]) )

        #process the transcript raw
        data = convert_transcript(os.path.join(basepath,x))
        data = gen_stats(data, split, teacherInfo, discussionInfo)
        #print(json.dumps({x:data[x] for x in data if x != 'turnList'}, indent=2))

        # save the processed data raw
        print(data)
        for k in data:
            print(k, type(data[k]))
        json.dump(data, open( os.path.join(basepath, split[0], ".".join(split[:-1]+["json"])), 'w', encoding="utf-8"))

        #process the transcript with classifier if desired
        if(useClassifier):
            data = convert_transcript(os.path.join(basepath, x), useClassifier)
            data = gen_stats(data, split, teacherInfo, discussionInfo)

            #save the classifier data

            json.dump(data, open( os.path.join(basepath, split[0],
                        ".".join(split[:-1]+["classifier", "json"])), 'w', encoding="utf-8"))
        #move the processed transcript
        shutil.move(os.path.join(basepath,x), os.path.join(basepath, split[0], x))


    toProcess = sorted([x for x in os.listdir(basepath) if x.endswith("goal")])
    for x in toProcess:
        print(x)
        split = x.split(".")
        shutil.move(os.path.join(basepath,x), os.path.join(basepath, split[0], x))


        # print("Num Turns,", len(data['turnList']))

        #temporary print statistics
        #print(x)
        # for k in sorted(data['graphData']['collabCount'].keys()):
        #     print(k, end = ",")
        # for k in sorted(data['graphData']['argMoveCount'].keys()):
        #     print(k, end = ",")
        # for k in sorted(data['graphData']['specifiCount'].keys()):
        #     print(k, end = ",")
        # print()
        # for k in sorted(data['graphData']['collabCount'].keys()):
        #     print(data['graphData']['collabCount'][k], end = ",")
        # for k in sorted(data['graphData']['argMoveCount'].keys()):
        #     print(data['graphData']['argMoveCount'][k], end = ",")
        # for k in sorted(data['graphData']['specifiCount'].keys()):
        #     print(data['graphData']['specifiCount'][k], end = ",")
        # print()
def to_Collaboration(turnList):
    """
    Converts a turn list into a dictionary of lists for Collaboration
    Incomplete!
    """
    toConvert = []
    for x in turnList:
        if(x['Student'] != 'teacher'):
            toConvert.append(x)


if __name__ == "__main__":
    #out = convert_transcript("/home/rav/ResearchNotes/TE-DT/Share/Data/EAGER/T124.EAGER.1.Ivan.Final.xlsx", useClassifier=True)

    #for i in [4,5,6]:
    #    print(json.dumps(out['turnList'][i], indent = 2))
    #dot = cm2.create_collaboration_map(out['turnList'])
    #print(dot)
    #print(type(dot))
    #ddprint(json.dumps({'a':dot.source}))
    # from graphviz import Source
    # src = Source(dot.source)
    # done = False
    # while not done:
    #     try:
    #         src.render(directory="img", format)
    #         dot.render(directory="img")
    #         done=True
    #     except:
    #         print("retrying")
    # with open("img/map.dot", "w") as f:
    #     f.write(dot.source)
    batchProcessTranscripts("transcripts", "metadata", True)
    #for k in out:
    #    print(k)
    #    if(type(out[k]) == list):
    #        print(out[k][0:3])
    #    else:
    #        print(out[k])

