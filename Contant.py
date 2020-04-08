
K_DOC_ID = "Id"
K_DOC_TIME = "time"
K_DOC_TEXT = "textCleaned"
K_CLASS_ID = "clusterNo"

I_cn = 0
I_cwf = 1
I_cww = 2
I_cd = 3
I_csw = 4
I_cl = 5
# variables which have underscore '_'  are globaly shareable and updatable
# variable without underscore are local variables

#------ Variable defined Terminology
# wid      :   word ID
# word     :  a term of word in text
# clus     :  Cluster
# freq     :  frequency
# docId    :  Document ID


#-------Cluster Feature Representation
# cn   : number of documents in cluster , documents indexs
# cwf  : word frequency in cluster          {wid, frequency}
# cww  : word to word co-occurance matrix
# cd   : cluster decay weight
# csw  : number of words in cluster ,  sum of all frequencies of words
# cl   : last time stamp