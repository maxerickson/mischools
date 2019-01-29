import csv
import collections

head='''<html><body>
'''
foot='''</body></html>'''

districtlists=collections.defaultdict(list)

with open("formatted.csv") as infile:
    csvin=csv.DictReader(infile)
    for record in csvin:
        districtlists[record["operator"]].append(record)

districts=list(districtlists.keys())
# special case indy schools
districts.remove("")
alphas=collections.defaultdict(list)
for d in districts:
    alphas[d[0]].append(d)
districtlists['indy']=districtlists['']
del districtlists['']
worklist=['indy']+sorted(alphas.keys())
alphas['indy']=['indy']
index=open("docs/index.html","w")
index.write(head)
index.write("<ul>\n")
for key in worklist:
    index.write('<li><a href="{}.html">{}</a></li>\n'.format(key,key))
    print(key,len(alphas[key]))
    with open("docs/"+key+".html", "w") as outfile:
        outfile.write(head)
        for dist in sorted(alphas[key]):
            outfile.write("<h3>{}</h3>\n".format(dist))
            for record in districtlists[dist]:
                outfile.write("<h5>{}</h5>\n".format(record["name"]))
                outfile.write("<p>\n")
                for tag in ['name','addr:housenumber','addr:street',
                                 'addr:city','addr:state','addr:postcode',
                                 'phone','operator','isced:level']:
                    outfile.write("{}={}<br/>\n".format(tag,record[tag]))
                outfile.write("</p>\n")
        outfile.write(foot)
index.write("</ul>")
index.write(foot)