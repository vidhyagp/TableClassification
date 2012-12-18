'''
Created on Nov 20, 2012

@author: shriram
'''
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

'''
    Annotating only Sparse and Non Sparse Lines
'''
class Trainer:
    def html_escape(self,text):
        html_escape_table = {
        '"': "&quot;",
        "'": "&apos;"
        }
        return escape(text, html_escape_table)
  
    def train(self, preprocessedxml, xmlname):
        f = open('../TrainingData/htmls/train'+xmlname+'.html','w')
        f.write('<html><body><form action="http://localhost/cgi-bin/TableProcessor.py" method="post">')
        f.write('<input type="hidden" name="xmlname" value="'+xmlname +'"/>')
        i = 0
        pageno = 0
        colno = 0
        for page in preprocessedxml:
            f.write('<div class="page"><input type="hidden" name="pagebegin'+str(pageno)+'" value="'+str(colno)+'"/>')
            for col in page:
                f.write('<div class="col"><input type="hidden" name="colbegin'+str(colno)+'" value="'+str(i)+'"/>')
                for tup in col:
                    f.write('<div><select id="docparams" name="docparams'+ str(i) +'">')
                    f.write('<option value="header1">Header 1</option>')
                    f.write('<option value="text" selected="selected">Text</option>')
                    f.write('<option value="header2">Header 2</option>')
                    f.write('<option value="dataheader">Data Header</option>')
		    f.write('<option value="footer">Footer</option>')
                    f.write('<option value="datarow">Data Row</option>')
                    f.write('<option value="caption">Caption</option>')
                    f.write("</select><input type='hidden' name='texttag"+str(i)+"' value='"+  self.html_escape(ET.tostring(tup[1],'utf-8',"xml")) + "'/>"+ ET.tostring(tup[1]) +"</div>")
                    i += 1
                f.write('<input type="hidden" name="colend'+str(colno)+'" value="'+str(i)+'"/><div>')
                colno += 1
            f.write('<input type="hidden" name="pageend'+str(pageno)+'" value="'+str(colno)+'"/> <div>')
            pageno += 1
        f.write('<input type="submit" value="Done!"/></form></body></html>')
        f.close()
        
    def readAnnotatedXml(self,xmlname):
        f = open(xmlname)
        preprocessedxml = list()
        col = list()
	last_last_line = ''
	last_line = ''
        for line in f:
	    if len(line.strip())==0: continue
            if(line == "=======================================PAGE========================================\n"):
                pagelist = list()
                preprocessedxml.append(pagelist)
            elif(line == "=======================================COL========================================\n"):
                col = list()
		last_last_line = ''
		last_line = ''
                pagelist.append(col)
            else:
                tup0 = line[:line.find("\t")]
                tup1 = line[line.find("\t")+1:]
                if tup0!='0':
			tup0_0 = last_line[:last_line.find("\t")]
			if tup0_0=='0':
		                tup1_0= last_line[last_line.find("\t")+1:]
				col.append([tup0_0, ET.fromstring(tup1_0)])
				tup0_0 = last_last_line[:last_last_line.find("\t")]
		                tup1_0= last_last_line[last_last_line.find("\t")+1:]
				if tup0_0 =='0':
					col.append([tup0_0, ET.fromstring(tup1_0)])
				
			col.append([tup0,ET.fromstring(tup1)])
       	
		last_last_line = last_line
		last_line = line 
        return preprocessedxml
                    
                
        
        
        
        
        
        
        
