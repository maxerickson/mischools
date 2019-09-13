import csv
import json
import collections

head='''<html><head>
<style>
.reviewed {background-color: #7c78;}
</style>
</head>
<body>
'''
foot='''
<script>
handleClick=function(e){
  e.preventDefault();
  e.stopPropagation();
  req = new XMLHttpRequest();
  req.onreadystatechange = function(){
    if (this.readyState == 4 && this.status == 200) {
      var pop=document.createElement('div');
      pop.style.position="fixed";
      pop.style.top="10px";
      pop.style.left="50%";
      pop.style.padding="10px";
      pop.style.backgroundColor="white";
      pop.style.outline="black solid thick";
      pop.innerHTML="Done";
      document.body.appendChild(pop);
      setTimeout(function(){document.body.removeChild(pop)}, 1500);
    };
  };
  req.open('GET', e.target.href, true);
  req.send(null);
};
links=document.getElementsByClassName("im");
for(var i=0; i<links.length; i++){
  links[i].addEventListener("click", handleClick, "false");
}
</script>
</body></html>'''

josmtmpl='''<a class="im" href="http://127.0.0.1:8111/load_and_zoom?left={left}&right={right}&top={top}&bottom={bottom}">JOSM</a>&nbsp;\n'''
idtmpl='''<a href="https://openstreetmap.org/edit?editor=id&lon={lon}&lat={lat}&zoom=17">iD</a>&nbsp;\n'''
osmtmpl='''<a href="https://openstreetmap.org/#map=17/{lat}/{lon}">OSM</a></br>\n'''
districtlists=collections.defaultdict(list)

reviewed=set()
with open("reviewed") as infile:
    for line in infile:
        reviewed.add(line.strip())

locations=dict()
with open('geocodes.csv') as infile:
    geo=csv.reader(infile)
    for record in geo:
        data=json.loads(record[3])
        if data:
            locations[(record[1],record[2])]=data

schools=0
with open("formatted.csv") as infile:
    csvin=csv.DictReader(infile)
    for record in csvin:
        schools+=1
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
locmatches=0
reviewed_school_count=0
for key in worklist:
    index.write('<li><a href="{}.html">{}</a></li>\n'.format(key,key))
    print(key,len(alphas[key]))
    with open("docs/"+key+".html", "w") as outfile:
        outfile.write(head)
        for dist in sorted(alphas[key]):
            if dist.strip() in reviewed:
                outfile.write("<div class=reviewed>")
                reviewed_school_count+=len(districtlists[dist])
            else:
                outfile.write("<div>")
            outfile.write("<h3>{}</h3>\n".format(dist))
            for record in districtlists[dist]:
                outfile.write("<h5>{}</h5>\n".format(record["name"]))
                if (record['name'],record['addr:city']) in locations:
                    locmatches+=1
                    locationdata=locations[(record['name'],record['addr:city'])]
                    lat=float(locationdata[0]["lat"])
                    lon=float(locationdata[0]["lon"])
                    delta=0.0025
                    josm=josmtmpl.format(top=lat+delta,left=lon-delta,bottom=lat-delta,right=lon+delta)
                    outfile.write(josm)
                    id=idtmpl.format(lat=lat,lon=lon)
                    outfile.write(id)
                    osm=osmtmpl.format(lat=lat,lon=lon)
                    outfile.write(osm)
                outfile.write("<p>\n")
                for tag in ['name','addr:housenumber','addr:street',
                                 'addr:city','addr:state','addr:postcode',
                                 'phone','operator','isced:level','grades','wikidata','website']:
                    if record[tag]:
                        outfile.write("{}={}<br/>\n".format(tag,record[tag]))
                if record['wikipedia']:
                    outfile.write("wikipedia=en:{}<br/>\n".format(record['wikipedia']))
                outfile.write("amenity=school<br/>\n")
                outfile.write("</p>\n")
            outfile.write("</div>\n")
        outfile.write(foot)
index.write("</ul>")
index.write(foot)
print(schools,"schools.")
print(locmatches,"addresses geocoded.")
print(reviewed_school_count,"reviewed schools.")
print("{:.1%} done.".format(reviewed_school_count / schools))