'''
Created on Nov 20, 2012

@author: shriram
'''
import xml.etree.ElementTree as ET
import math
import logging
from Utils.SparseType import SparseType
from Utils.Utilities import Utilities
from Utils.Constants import Constants
'''
Dirty replace of <a> tags. Not a prime concern as of now?
'''
class PreProcessor:
    def removeBIATags(self, xmlloc):
        f = open(xmlloc, 'r')
        f1 = open(xmlloc + '_tag', 'w')
        for line in f:
            if(line.strip() == ''):
                continue
            line.decode('ascii','ignore')
            f1.write(line.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '').replace('</a>','').replace('<a','')) 
        f.close()
        f1.close()
        
        return xmlloc+'_tag'
    
    '''
        Check for marked difference in top 
        Info: Figures' data will go into new columns
        Should we check the left too?
    '''
    def findColumns(self, combinedTextTagTuple, height):
        THRESHOLD_HEIGHT = height/Constants.DIFF_IN_HEIGHT_FOR_NEW_COLUMN
        pagecolumns = list()
        newpagecolumns = list()
        
        prevtexttag = combinedTextTagTuple[0][1]
        col = list()
        for tup in combinedTextTagTuple:
            texttag = tup[1]
            prevtop = int(prevtexttag.attrib['top'])
            currtop = int(texttag.attrib['top'])
            if(math.fabs(prevtop - currtop) > THRESHOLD_HEIGHT):
                pagecolumns.append(col)
                newpagecolumns.append(col)
                col = list()
            col.append(tup)
            prevtexttag = texttag
            
        if(len(col) > Constants.MIN_COL_LENGTH):
            pagecolumns.append(col)
            newpagecolumns.append(col)
        
        for colno in xrange(len(pagecolumns)):
            if(Utilities().checkkeywordpresense(pagecolumns[colno], len(pagecolumns[colno]) - 1)):
                for r in xrange(colno+1, len(pagecolumns)):
                    prevtop = int(pagecolumns[colno][len(pagecolumns[colno]) - 1][1].attrib['top'])
                    currtop = int(pagecolumns[r][0][1].attrib['top'])
                    if(math.fabs(prevtop - currtop) < THRESHOLD_HEIGHT):
                        newpagecolumns[colno].extend(newpagecolumns[r])
                        newpagecolumns.remove(newpagecolumns[r])
                        break
        return newpagecolumns
    
    '''
    Combine Superscript and subscript.
    Combine divided lines
    '''
    
    def combineSubAndSuperScripts(self, page):
        prevtexttag = page.find('text')
        texttags = list()
        for texttag in page.findall('text'):
            newtexttag = texttag
            currtop = int(texttag.attrib['top'])
            currheight = int(texttag.attrib['height'])
            prevheight = int(prevtexttag.attrib['height'])
            prevtop = int(prevtexttag.attrib['top'])
            prevleft = int(prevtexttag.attrib['left'])
            prevwidth = int(prevtexttag.attrib['width'])
            currleft = int(texttag.attrib['left'])
            doTextsMerge = prevtop + prevheight > currtop or math.fabs(prevtop - currtop) < currheight
            doLeftsMerge = math.fabs(prevleft + prevwidth - currleft) < Constants.SUBSCRIPT_LEFT_THRESHOLD
            
            if (doTextsMerge and doLeftsMerge and len(texttags) != 0): #Subscript or superscript
                previnsertedtexttag = texttags.pop()
                
                if(texttag.text is None):
                    logging.error("None Type occured in xml doc for tag --> " + ET.tostring(texttag))
                    
                previnsertedtexttag[1].text = previnsertedtexttag[1].text + texttag.text
                previnsertedtexttag[1].attrib['width'] = str(int(previnsertedtexttag[1].attrib['width']) + int(texttag.attrib['width'])) 
                newtexttag = previnsertedtexttag[1]
                
            newtexttag.attrib['textpieces'] = "0"
            texttags.append([SparseType.NONSPARSE, newtexttag])
            prevtexttag = newtexttag
        
        return texttags
    
    
    def combineTextPieces(self, fontdict, subSupCombinedTexttags):
        prevtexttag = subSupCombinedTexttags[0][1]
        texttags = list()
        for tup in subSupCombinedTexttags:
            texttag = tup[1]
            sparsetype = SparseType.NONSPARSE
            newtexttag = texttag
            currtop = int(texttag.attrib['top'])
            prevtop = int(prevtexttag.attrib['top'])
            prevleft = int(prevtexttag.attrib['left'])
            prevwidth = int(prevtexttag.attrib['width'])
            currleft = int(texttag.attrib['left'])
            currheight = int(texttag.attrib['height'])
            prevfontsize = fontdict[int(prevtexttag.attrib['font'])]
            
            if ((prevtop == currtop or math.fabs(prevtop - currtop) < currheight / Constants.SAME_LINE_HEIGHT_FACTOR) and len(texttags) != 0):
                previnsertedtexttag = texttags.pop()
                nopixels = math.fabs(prevleft + prevwidth - currleft)
                space = ''
                for _ in xrange(int(nopixels * Constants.FONT_LOC_FOR_MERGING / prevfontsize)):
                    space += ' ' # 1 Space = FontSize/2 pixels
                
                previnsertedtexttag[1].text = previnsertedtexttag[1].text + space + texttag.text
                previnsertedtexttag[1].attrib['width'] = str(currleft - int(previnsertedtexttag[1].attrib['left']) + int(texttag.attrib['width']))
                newtexttag = previnsertedtexttag[1]
                if (prevtop == currtop):
                    sparsetype = SparseType.OTHERSPARSE
                
                newtexttag.attrib['textpieces'] = str(int(newtexttag.attrib['textpieces']) + 1) #Computing Number of text pieces for CRF
                    
            texttags.append([sparsetype, newtexttag])
            prevtexttag = newtexttag
        
        return texttags
    
    def combineTextTags(self, page, fontdict):
        subSupCombinedTexttags =  self.combineSubAndSuperScripts(page)
        texttags = self.combineTextPieces(fontdict, subSupCombinedTexttags)
        return texttags   
    
    
    def getFontDictionary(self, parseTree):
        fontdict = dict()
        fontspecTags = parseTree.iter('fontspec')
        for tags in fontspecTags:
            fontdict[int(tags.attrib['id'])] = int(tags.attrib['size'])
        return fontdict
    
    def preprocessxml(self, xmlloc):
        logging.basicConfig(filename='preprocessingerrors.log',level=logging.DEBUG)
        xmlloc = self.removeBIATags(xmlloc)
        parseTree = ET.parse(xmlloc)
        f = open('a.xml','w')
        preprocessedxml = list()
        fontdict = self.getFontDictionary(parseTree)
        for page in parseTree.iter('page'):
            combinedTextTagTuple = self.combineTextTags(page, fontdict)
            height = int(page.attrib['height'])
            pagecols = self.findColumns(combinedTextTagTuple, height)
            preprocessedxml.append(pagecols)
            for col in pagecols:
                for tag in col:
                    f.write(ET.tostring(tag[1]))
            #print "For Page " + page.attrib['number'] + " Col = " +str(len(columns)) 
        f.close() 
        return preprocessedxml
    
    def processhtml(self, htmlloc):
	tree = ET.parse('htmlloc')
	root = tree.getroot()
	 
