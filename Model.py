# @author Jay Kumar

from Document import Document
import Contant as con
import math

class Model:

    def __init__(self, ALPHA, BETA, LAMDA, applyDecay=True, applyICF = True, applyCWW = True):
        self.alpha = ALPHA
        self.beta = BETA
        self.applyDecay = applyDecay
        self.applyICF = applyICF
        self.applyCWW = applyCWW
        self.word_wid_map = {}   # word, Assigned ID :    updated by Document
        self.wid_word_map = {}  # Assigned ID, word:    updated by Document
        self.wid_docId = {}      # wordID, documentId:    updated by Document
        self.clusters = {}   #   clusterID -> [ cn, cw, cwf, cww, cd, csw]
        self.documents = {}   # {documentId, Document}
        self.widClusid = {}   # {wordID ,clusterID }: to know that how many cluster this word has occured
        self.docIdClusId = {}  # {documentID , clusterID} Cluster assignments of each document
        self.deletedDocIdClusId = {} # those documents which are deleted while deleting the cluster, #this DS will be utilized to print output
        self.lamda = LAMDA

        self.word_counter = {0:0}
        self.cluster_counter = {0:0}

        self.currentTimestamp = 0


    def processDocument(self, document):
        self.documents[document.docId] = document
        self.currentTimestamp+=1
        self.sampleCluster(document)


    def sampleCluster(self, document):
        if(self.applyDecay == True):
            self.checkOldClusters(self.lamda)
        clusIdOfMaxProb = -1
        clusMaxProb = 0.0

        N = self.documents.__len__()  # number of maintained documents, some documents might be deleted from cluster
        VintoBETA = self.getVocabularyIntoBeta()

        # need to calculate probablity of existing clusters, if no existing cluster this loop will be skipped
        for clusId in self.clusters:
            CF = self.clusters[clusId]

            numOfDocInClus = CF[con.I_cn].__len__()
            eqPart1 = float(numOfDocInClus) / float(( N-1 + self.alpha*N))
            eqPart2Nominator = 1.0
            eqPart2Denominator = 1.0
            numOfWordsInClus = CF[con.I_csw]
            i = 0  # represent word count in document
            for w in document.widFreq:
                widFreqInClus = 0
                if w in CF[con.I_cwf]: #if the word of the document exists in cluster
                    widFreqInClus = CF[con.I_cwf][w]

                icf = 1.0
                if (self.applyICF == True):  # This condition is used to control parameters by main method
                    icf = self.ICF(w)

                freq = document.widFreq[w]
                for j in range(freq):
                    i+=1
                    eqPart2Nominator *= ( widFreqInClus*icf + self.beta+j )
                    eqPart2Denominator *= (numOfWordsInClus * VintoBETA + i)

            eqPart2 = eqPart2Nominator / eqPart2Denominator
            if (self.applyCWW == True): # to control applying CWW from main method
                eqPart2 = eqPart2 * self.addingWidToWidWeightInEqPart2(document,CF,eqPart2)

            clusProb = eqPart1 * eqPart2
            if clusProb > clusMaxProb:
                clusMaxProb = clusProb
                clusIdOfMaxProb = clusId
        # end for , all probablities of existing clusters have been calculated

        # need to calculate probablity of creating a new cluster
        eqPart1 = (self.alpha * N) / (N - 1 + self.alpha * N)
        eqPart2Nominator = 1.0
        eqPart2Denominator = 1.0
        i = 0 # represent word count in document
        for w in document.widFreq:
            freq = document.widFreq[w]

            for j in range(freq):
                i += 1
                eqPart2Nominator*= (self.beta+j)
                eqPart2Denominator*= (VintoBETA+i)
        probNewCluster = eqPart1*(eqPart2Nominator/eqPart2Denominator)
        if probNewCluster < clusMaxProb:
            self.addDocumentIntoClusterFeature(document, clusIdOfMaxProb)
        else:
            self.createNewCluster(document)



    def getVocabularyIntoBeta(self):
        temp = float(self.beta)*float(self.wid_docId.__len__())
        return temp

    def createNewCluster(self,document):
        #create new cluster
        self.cluster_counter[0] = self.cluster_counter[0]+1
        newIndexOfClus = self.cluster_counter[0] # = {}   clusterID -> [ cn, cw, cwf, cww, cd, csw]

        self.clusters[newIndexOfClus]={}
        self.clusters[newIndexOfClus][con.I_cn]=[]
        self.clusters[newIndexOfClus][con.I_cwf] = {}
        self.clusters[newIndexOfClus][con.I_cww] = {}
        self.clusters[newIndexOfClus][con.I_cd] = 1.0
        self.clusters[newIndexOfClus][con.I_csw] = 0
        self.addDocumentIntoClusterFeature(document,newIndexOfClus)

    def addDocumentIntoClusterFeature(self,document, clusterId):
        CF = self.clusters[clusterId]
        CF[con.I_cl] = self.currentTimestamp
        CF[con.I_cd] = 1.0
        self.docIdClusId[document.docId] = clusterId
        CF[con.I_cn].append(document.docId)
        # update feature of cluster
        for w in document.widFreq:
            self.updateWidClusid(w, clusterId)   #helps to calculate ICF, if this word is not contained by widClusMap then add it

            if w not in CF[con.I_cwf]:
                CF[con.I_cwf][w]=0
                CF[con.I_cww][w]={}
            CF[con.I_cwf][w] = CF[con.I_cwf][w] + document.widFreq[w]   #update word frequency in cluster
            CF[con.I_csw] = CF[con.I_csw]+document.widFreq[w]           # increasing number of words in cluster

            for w2 in document.widFreq: #updating CF[cww] word to word frequency
                if w!=w2:
                    if w2 not in CF[con.I_cww][w]:
                        CF[con.I_cww][w][w2] = document.widToWidFreq[w][w2]
                    else:
                        CF[con.I_cww][w][w2] = CF[con.I_cww][w][w2]+document.widToWidFreq[w][w2]

    def updateWidClusid(self, wid, clusterId):
        if wid not in self.widClusid:  # updating widClusid
            self.widClusid[wid] = []
            self.widClusid[wid].append(clusterId)
        else:
            if clusterId not in self.widClusid[wid]:
                self.widClusid[wid].append(clusterId)


    def addingWidToWidWeightInEqPart2(self,document, CF, eqPart2):
        product = 1.0
        traversed = []
        for wid in document.widToWidFreq:
            if wid not in CF[con.I_cww]:  # if this word not exist in the cluster
                continue
            sumOfProbablitiesOfWid = 0.0
            for wid2 in document.widToWidFreq[wid]:
                sumOfProbablitiesOfWid = sumOfProbablitiesOfWid+document.widToWidFreq[wid][wid2]
            for wid2 in document.widToWidFreq[wid]:
                if wid2 in CF[con.I_cww][wid]:
                    if wid2 not in traversed:
                        weight = CF[con.I_cww][wid][wid2] / sumOfProbablitiesOfWid
                        product = product+weight
            traversed.append(wid)
        return product


    def checkOldClusters(self, LAMDA):
        threshold = 0.00001
        clustersToDelete = {}
        for clusterID in self.clusters:
            CF = self.clusters[clusterID]

            lastupdated = CF[con.I_cl]
            power = -LAMDA*(self.currentTimestamp-lastupdated)
            decay=pow(2,power)
            CF[con.I_cd] = CF[con.I_cd]*decay
            if CF[con.I_cd] < threshold:
                clustersToDelete[clusterID] = CF
        for clusIDKey, CFvalue in clustersToDelete.items():
            lenBefore = self.clusters.__len__()
            clusterSize = CFvalue[con.I_cn].__len__()
            self.deleteOldCluster(clusIDKey, CFvalue)
            lenAfter = self.clusters.__len__()
            # print("deleted old cluster: ", clusIDKey , " clusterSize:", clusterSize ," Total Clusters:", lenAfter)

    def deleteOldCluster(self, clusterID, CF):
        for wid in CF[con.I_cwf]:  # remove words from self.widClusid
            self.widClusid[wid].remove(clusterID)
            if self.widClusid[wid].__len__() == 0:
                del[self.widClusid[wid]]
            listOfDocsContainsWid = self.wid_docId[wid]
            listOfDocToDelete=self.intersection(listOfDocsContainsWid, CF[con.I_cn])
            for docIdToDelete in listOfDocToDelete:
                self.wid_docId[wid].remove(docIdToDelete)
                if self.wid_docId[wid].__len__() == 0: #if a word is not used by any document then delete it
                    del[self.wid_docId[wid]]
                    word = self.wid_word_map[wid]
                    del[self.wid_word_map[wid]]
                    del[self.word_wid_map[word]]
        for docId in CF[con.I_cn]: # remove documents from self.documents, self.docIdClusId
            del[self.documents[docId]]
            del[self.docIdClusId[docId]]
            self.deletedDocIdClusId[docId] = clusterID #this DS will be utilized to print output
        del[self.clusters[clusterID]]

    def intersection(self,listA, listB):
        return list(set(listA) & set(listB))

    def ICF(self,wid):
        icf = 1.0
        if self.clusters.__len__() < 20:
            icf = 1.0
        else:
            if wid in self.widClusid:
                icf = math.log2( self.clusters.__len__()/self.widClusid[wid].__len__())
        return icf