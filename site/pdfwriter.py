#!/usr/bin/python
MEASURE={
	"arial":{
		14:(7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,5,5,7,11,11,17,13,4,6,6,7,11,6,7,6,5,11,11,11,11,11,11,11,11,11,11,6,6,11,11,11,10,20,13,13,14,14,13,12,15,15,6,9,13,11,16,14,15,13,15,14,12,13,13,13,18,13,12,12,5,5,5,9,11,6,11,11,10,11,11,6,11,10,4,4,9,4,16,10,11,11,11,6,10,7,10,10,14,10,10,10,7,5,7,11,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,13,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,9,7,5,6,10,11,11,11,5,10,7,15,8,11,11,7,15,11,7,11,7,7,7,11,10,6,6,6,8,11,16,17,16,11,13,13,12,13,13,13,19,14,13,13,13,13,6,6,6,7,15,14,15,15,15,15,15,11,15,13,13,13,13,12,13,11,11,11,11,11,11,11,17,10,11,11,11,11,5,6,6,7,11,10,11,11,11,11,11,11,11,10,10,10,10,10,11,9),
	},
}
from unicodedata import normalize
from collections import defaultdict
import string
breakable=string.whitespace+string.punctuation
def psify(o,ml=(),wrap=880,measure=MEASURE["arial"][14]):
	for k in o:
		if isinstance(o[k],unicode):
			o[k]=normalize("NFKD",o[k]).encode("ascii","ignore")
	for p in ml:#estimate word wrap
		line=[]
		width=0
		row=0
		fold=0
		for c in o.pop(p)or"":
			w=measure[ord(c)]
			width+=w
			if width>wrap:
				fold=(fold-1)%len(line)+1
				o["%s_%d"%(p,row)]="".join(line[:fold])
				width=w
				row+=1
				line=line[fold:]
				fold=0
			line.append(c)
			if c in breakable:
				fold=len(line)
		o["%s_%d"%(p,row)]="".join(line)
	return defaultdict(str,((k,"<"+"".join("%02x"%ord(c)for c in(('X'if v else"")if type(v)is bool else""if v is None else str(v)))+">Tj")for k,v in o.iteritems()))#render bool using " X"
def obj(data,id1,id2=None):
	if id2 is None:
		id2=id1+1
	return"""%d 0 obj
<<
/Length %d 0 R
>>
stream
%s
endstream
endobj
%d 0 obj
%d
endobj
"""%(id1,id2,data,id2,len(data))
import re
objstart=re.compile(r"^([0-9]+) 0 obj$",re.MULTILINE)
def write(cb,data,root=1,info=2):
	oid,ofs=zip(*[(int(m.group(1)),m.start())for m in objstart.finditer(data)])
	xref=[None]*max(oid)
	for i in xrange(len(oid)):
		xref[oid[i]-1]=ofs[i]
	size=len(xref)+1
	cb(data)
	cb("""
xref
0 %d
0000000000 65535 f 
"""%size)
	for x in xref:
		if x is None:
			cb("0000000000 00000 f \n")
		else:
			cb("%010d 00000 n \n"%x)
	if isinstance(root,(int,long)):
		root="%d 0 R"%root
	if isinstance(info,(int,long)):
		info="%d 0 R"%info
	cb("""trailer
<<
/Size %d
/Root %s
/Info %s
>>
startxref
%d
%%%%EOF
"""%(size,root,info,len(data)))
from time import strftime,localtime
def moddate():
	strftime("%Y%m%d%H%M%S",localtime())
