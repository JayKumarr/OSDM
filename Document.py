# @author Jay Kumar

import json
import Contant as Con

# Input: This class takes a json object of document
# Output: update global Map of word_wid_map

class Document:

    def __init__(self,jsonObject, word_wid_map, wid_word_map, wid_docId, word_counter):
        self.docText = jsonObject[Con.K_DOC_TEXT]
        # self.docTime = jsonObject[Con.K_DOC_TIME]
        self.docId = jsonObject[Con.K_DOC_ID]
        self.classId = jsonObject[Con.K_CLASS_ID]
        self.widFreq = {}   # maintaining wordId and the occurance
        self.widToWidFreq = {}
        ws = self.docText.strip().split(' ')
        for w in ws:
            NEWID = word_counter[0]+ 1
            # NEWID = word_wid_map.__len__()+1
            wid = word_wid_map.get(w,NEWID)   #if the key exist in word_wid_map then it will return wid OTHERWISE it will return default value
            if wid == NEWID:  # if a word occuring first time globaly then Add it with new ID
                word_counter[0]  =NEWID
                word_wid_map[w] = NEWID    #  defining new ID to word
                wid_word_map[NEWID] = w
                self.widFreq[NEWID] = 1
                wid_docId[NEWID] = []
                wid_docId[NEWID].append(self.docId)
            else:   # if any word is already came before than update local document widFreq

                tf = 0
                defaultTF = 0
                tf = self.widFreq.get(wid,defaultTF)
                if tf == defaultTF:  # if this word is occuring first time in this document
                    self.widFreq[wid] = 1
                    wid_docId[wid].append(self.docId)
                else:
                    tf = tf+1
                    self.widFreq[wid] = tf

        #calculate word to word score
        for w in self.widFreq:
            wFreq = self.widFreq[w]
            self.widToWidFreq[w]={}  # adding wid into self.widToWidFreq
            for w2 in self.widFreq:
                if w!=w2:
                    w2Freq = self.widFreq[w2]
                    total = wFreq+w2Freq
                    score = wFreq/total
                    self.widToWidFreq[w][w2] = score