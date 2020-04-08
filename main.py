# @author Jay Kumar

from Document import Document
from Model import Model
import json
import time
import sys

def printExecutionTime(startTime, str=""):
    print(str+ " time elapsed: {:.2f}s".format(time.time() - start_time))
    return time.time()

def outputFileNameFormatter(resultDir, dataset, outputPrefix, ALPHA, BETA, LAMDA, decay):
    output = ""
    if decay == True:
        output = resultDir + "/" + dataset + outputPrefix + "_ALPHA" + str(ALPHA) + "_BETA" + str(
            BETA) + "_LAMDA" + str(LAMDA) + ".txt"
    else:
        output = resultDir + "/" + dataset + outputPrefix + "_ALPHA" + str(ALPHA) + "_BETA" + str(BETA) + ".txt"
    print("ALHA " + str(ALPHA) + " -  BETA " + str(BETA))
    return output


dataDir = "data/"
resultDir = ""

# dataset = "News"
dataset = "Tweets"
# dataset = "reuters21578"


LAMDA = 0.000006
alphas = [0.002]
betas =  [0.0004]

decay = True
applyICF = True
applyCWW = True
start_index = 0

outputPrefix = ""
if applyICF:
    outputPrefix = outputPrefix+"_ICF"
if applyCWW:
    outputPrefix = outputPrefix + "_CWW"
start_time = time.time()
print("Dataset: ",dataset," , Decay:", decay, " , ICF = ", applyICF, " , CWW = ", applyCWW)
listOfObjects = []
with open(dataDir+dataset) as input:  #load all the objects in memory
    line = input.readline()
    while line:
        obj = json.loads(line)  # a line is a document represented in JSON
        listOfObjects.append(obj)
        line = input.readline()

printExecutionTime(start_time)
start_time = time.time()
indexOfAlpha = -1
indexOfBeta = -1
for a in alphas:
    indexOfAlpha += 1
    for b in betas:
        indexOfBeta += 1
        if indexOfAlpha!=indexOfBeta:
            continue
        if a == 0.0 or b == 0.0:
            continue
        ALPHA = a
        BETA = b

        output = outputFileNameFormatter(resultDir, dataset, outputPrefix, ALPHA, BETA, LAMDA, decay)

        model = Model(ALPHA, BETA, LAMDA, applyDecay=decay, applyICF = applyICF, applyCWW=applyCWW)
        iter = 1
        for obj in listOfObjects:
            document = Document(obj, model.word_wid_map, model.wid_word_map,
                                model.wid_docId, model.word_counter)  # creating a document object which will spilt the text and update wordToIdMap, wordList
            if iter%1000 == 0:
                start_time=printExecutionTime(start_time,"Documents "+str(iter))
            model.processDocument(document)
            iter += 1

        # Printing Clusters into File
        f = open(output, "w")
        for d in model.docIdClusId:
            st = ""+str(d)+" "+str(model.docIdClusId[d])+" \n"
            f.write(st)
        for d in model.deletedDocIdClusId:
            st = ""+str(d)+" "+str(model.deletedDocIdClusId[d])+" \n"
            f.write(st)
        f.close()
        print(output)
        printExecutionTime(start_time)
    indexOfBeta = -1
    # end of beta loop
#end of alpha loop

printExecutionTime(start_time)

