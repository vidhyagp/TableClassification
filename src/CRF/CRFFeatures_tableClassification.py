from Utils.SparseType import SparseType
from Utils.Constants import Constants
import sys
class CRFFeatures:
    def getText(self,text):
	out_text=''
	for c in text:
		if ord(c)<128:
			out_text = out_text+c
	return out_text	
    def fontSizefeatures(self, featurelist, col, prevtag, curtag, i, fontdict):
	fontSizeDiff = fontdict[int(col[i][1].attrib['font'])] - fontdict[int(col[i - 1][1].attrib['font'])]
	if fontSizeDiff <0 and prevtag=='1' and curtag=='3':
		featurelist.append(1)
	else:
		featurelist.append(0)
        if fontSizeDiff >0 and prevtag==3 and curtag==5:
                featurelist.append(1)
        else:
                featurelist.append(0)
    def tableTextfeatures(self, featurelist, col, prevtag, curtag, i, fontdict):
        text_i_1 = self.getText(col[i-1][1].text)
	text_i= self.getText(col[i][1].text)

	text_i_plus_1 = ''
	if i<len(col)-1:
		text_i_plus_1 =self.getText(col[i+1][1].text)
	text_i_2 = self.getText(col[i-2][1].text)
	text_i_plus_2 = ''
	if i<len(col)-2:
		text_i_plus_2 =self.getText(col[i+2][1].text)

	tabletextbefore = ((i>0 and col[i-1][1].text is not None and text_i_1.lower().startswith("table ")) or 
                           (i>1 and col[i-2][1].text is not None and text_i_2.lower().startswith("table ")))
        tabletextafter = (i < len(col) - 2 and col[i+1][1].text is not None and col[i+2][1].text is not None
           and ((text_i_plus_1.lower().startswith("table ") and col[i+1][0]=='4') or (text_i_plus_2.lower().startswith("table ") and col[i+2][0]=='4')))
	tabletext = (i>0 and col[i][1].text is not None and text_i.lower().startswith("table") and curtag=='4')
	#if col[i][1].text is not None and curtag is not None and i>0:
			#print str(text_i) + " --> " + str(curtag)
        if (tabletext):
            featurelist.append(1)
        else:
            featurelist.append(0)

        if (tabletextbefore and curtag=='4'):
		featurelist.append(1)
		print "table text before"
	else:
		featurelist.append(0)    
	if (i>0 and tabletextbefore and curtag=='1' and prevtag=='4' and int(col[i][1].attrib['textpieces']) >  int(col[i-1][1].attrib['textpieces'])):
		featurelist.append(1)
		print "table starts"
	else:
		featurelist.append(0)
        if (i>0 and tabletextbefore and curtag=='4' and prevtag=='4' and int(col[i][1].attrib['textpieces']) ==  int(col[i-1][1].attrib['textpieces'])):
                featurelist.append(1)
        else:
                featurelist.append(0)
	if (i>0 and tabletextafter and curtag=='3'):
		featurelist.append(1)
	else:
		featurelist.append(0)
    def findnuminline(self,text):
	count = 0
	length = 1
	for c in text:
		if c>='0' and c<='9':
			count = count+1    
		if c!= ' ':
			length  = length+1
	num = float(count)/float(length)
	return num
    def findcharinline(self,text):
        count = 0
        length = 1
        for c in text:
                if (c>='A' and c<='Z') or (c>='a' and c<='z'):  
                        count = count+1
                if c!= ' ':
                        length  = length+1
        num = float(count)/float(length)
        return num
    def lexicalfeatures(self, featurelist, col, prevtag, curtag, i):
        text = col[i][1].text
	text1=''
	if i>=1: text1 = col[i-1][1].text
        if self.findnuminline(text) > self.findnuminline(text1) and prevtag=='1' and curtag =='3':
                featurelist.append(1)
        else:
                featurelist.append(0)
	
	if (self.findnuminline(text) > self.findnuminline(text1)) and prevtag=='3' and curtag =='5':
                featurelist.append(1)
        else:
                featurelist.append(0)
        

        if self.findcharinline(text) < self.findcharinline(text1) and prevtag=='1' and curtag=='3':
                featurelist.append(1)
        else:
                featurelist.append(0)




    def spaceinline(self, text):
        if(text is None):
            return [0,0,0]
        spacecount = 0
        largestspace = 0
        wordcount = 0
        smallestspace = sys.maxint
        for r in xrange(len(text)):
            if(text[r] == ' '):
                spacecount += 1
            elif(spacecount != 0):
                wordcount += 1
                if(spacecount < smallestspace):
                    smallestspace = spacecount
                if(spacecount > largestspace):
                    largestspace = spacecount
                spacecount = 0
        return [largestspace, smallestspace, wordcount+1 ]
    
    def spacelayoutfeatures(self, featurelist, col, curtag, i):
        spaceincurrentline = self.spaceinline(col[i][1].text)
        if (spaceincurrentline[0] >= Constants.LARGEST_SPACE and curtag !='0'):
            featurelist.append(1)
        else:
            featurelist.append(0)
        if (spaceincurrentline[1] <= Constants.SMALLEST_SPACE and curtag !='0'):
            featurelist.append(1)
        else:
            featurelist.append(0)
        if (spaceincurrentline[2] <= Constants.WORDS_IN_LINE and curtag !='0'):
            featurelist.append(1)
        else:
            featurelist.append(0)

    def layoutfeatures(self, featurelist, col, prevtag, curtag, i): 
        #[textpieces, heightprev, heightnext, largest space, smallest space, words]
        if(i>1 and int(col[i][1].attrib['textpieces']) >  int(col[i-1][1].attrib['textpieces']) and prevtag=='4' and curtag=='1'):
            featurelist.append(1)
        else:
            featurelist.append(0)
        
       	if(i>1 and int(col[i][1].attrib['textpieces']) ==  int(col[i-1][1].attrib['textpieces']) and prevtag==curtag):
            featurelist.append(1)
        else:
            featurelist.append(0)
	if(i>1 and int(col[i][1].attrib['textpieces']) ==  int(col[i-1][1].attrib['textpieces']) and prevtag in ['1', '2', '3', '5'] and curtag in ['1','2', '3', '5']):
            featurelist.append(1)
        else:
            featurelist.append(0)
	if (i>1 and int(col[i][1].attrib['textpieces']) >  int(col[i-1][1].attrib['textpieces']) and int(col[i-1][1].attrib['textpieces'])!=0 and prevtag=='1' and curtag=='2'):
		featurelist.append(1)
	else:	
		featurelist.append(0)
	if(i>1 and int(col[i][1].attrib['textpieces']) <  int(col[i-1][1].attrib['textpieces']) and prevtag=='3' and curtag=='4'):
            featurelist.append(1)
        else:
            featurelist.append(0)

	if(i>1 and int(col[i][1].attrib['height']) < int(col[i-1][1].attrib['height']) and curtag =='1' and prevtag in ['0','4']):
            featurelist.append(1)
        else:
            featurelist.append(0)
            
        if(i!=len(col)-1 and int(col[i][1].attrib['height']) < int(col[i+1][1].attrib['height']) and prevtag in ['1', '2','5'] and curtag=='3'):
            featurelist.append(1)
        else:
            featurelist.append(0)
        
        if(i>1 and abs(int(col[i][1].attrib['top'])-int(col[i-1][1].attrib['top'])) < abs(int(col[i-1][1].attrib['top'])-int(col[i-2][1].attrib['top'])) and curtag !='0'):
            featurelist.append(1)
        else:
            featurelist.append(0)
            
       	if(i>1 and abs(int(col[i][1].attrib['top'])-int(col[i-1][1].attrib['top'])) > abs(int(col[i-1][1].attrib['top'])-int(col[i-2][1].attrib['top'])) and curtag !='0'):
            featurelist.append(1)
        else:
            featurelist.append(0)
        
        self.spacelayoutfeatures(featurelist, col, curtag, i) 
        
    def otherfeatures(self,featurelist, col, prevtag, curtag, i):
	
        for i in xrange(0, 6):
		for j in xrange(0,6):
			if (i!=0 and prevtag==i and curtag==j):
				featurelist.append(1)
			else:
				featurelist.append(0)	
    
    def domainfindfeatureFunction(self, i, col, fontdict, prevtag = None, curtag = None):
        featurelist = list()
        if(prevtag is None and i!=0):
            prevtag = int(col[i-1][0])
        if(curtag is None and i!=0):
            curtag = int(col[i][0])
	print self.getText(col[i][1].text) + " --> "+str(curtag)
        self.fontSizefeatures(featurelist, col, prevtag, curtag, i, fontdict)
        self.tableTextfeatures(featurelist, col, prevtag, curtag, i, fontdict)
        #featurelist.append(self.lexicalfeatures(featurelist, col, prevtag, curtag, i))
        self.layoutfeatures(featurelist, col, prevtag, curtag, i)
        self.lexicalfeatures(featurelist, col, prevtag, curtag, i)
        self.otherfeatures(featurelist, col, prevtag, curtag, i)   
        
        return featurelist
