import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
from lxml.etree import HTMLParser
#from SVM.SVMImpl import SVMImpl
import sys
class MaxDepth:
	maxDepth = 0
	depth =0
	val = "text"
	flag = False
	
	values = ['text', 'header1', 'header2', 'datarow', 'caption', 'dataheader', 'footer']
	def init_fw(self,filename):
		self.fw = open(filename, 'w')
	def start(self, tag, attrib):   # Called for each opening tag.
            	self.depth += 1
            	if tag=="input":
			if "name" in attrib: 
				if attrib["name"].startswith("texttag"):
					self.flag = True
					print attrib['value']
					self.fw.write(str(self.values.index(self.val)) + "\t" + attrib['value'].encode('utf-8')+"\n")
				if attrib["name"].startswith("pagebegin"):
					self.fw.write("=======================================PAGE========================================\n")
			
				if attrib["name"].startswith("colbegin"):
					self.fw.write("=======================================COL========================================\n")
		if tag=="option":
			if 'selected' in attrib:
				self.val = attrib['value']
		if self.depth > self.maxDepth:
                	self.maxDepth = self.depth
        def end(self, tag):             # Called for each closing tag.
            self.depth -= 1
        def data(self, data):
	    if (self.flag):
		self.flag = False     # We do not need to do anything with data.
        def close(self):    # Called when all data has been parsed. 
            return self.maxDepth
def readHTMLFile(filename, outFile):
#	tree= ET()
	text = ''
	f = open(filename)
	for line in f:
		text = text + " "+ line
	target = MaxDepth()
	target.init_fw(outFile)
	parser = HTMLParser(target=target)
	
	parser.feed(text)
	parser.close()
	#tree.parse(filename)

readHTMLFile(sys.argv[1], sys.argv[2])	   

