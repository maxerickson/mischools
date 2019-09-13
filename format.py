import csv

denoms={'Christian (no specific denomination)':("christian",""),
'Wisconsin Evangelical Lutheran Synod':("christian","lutheran"),
'Roman Catholic':("christian","roman_catholic"),
'Islamic':("muslim",""),
'Amish':("christian","amish"),
'Lutheran Church - Missouri Synod':("christian","lutheran"),
'Seventh-Day Adventist':("christian","seventh_day_adventist"),
'Jewish':("jewish",""),
'Mennonite':("christian","mennonite"),
'Muslim':("muslim",""),
'Baptist':("christian","baptist")}

abbvs={
  "Acad.":"Academy",
  "Alt.":"Alternative",
  "Assem.":"Assembly",
  "Chr.":"Christian",
  "Co.":"County",
  "Ctr":"Center",
  "Ctr.":"Center",
  "Educ.":"Education",
  "Elem.":"Elementary",
  "Ev.":"Evangelical",
  "Fr.":"Father",
  "H.S.":"High School",
  "Inst.":"Institute",
  "Jr.":"Junior",
  "Jr./Sr.":"Junior/Senior",
  "Sr.":"Senior",
  "M.S.":"Middle School",
  "Mt.":"Mount",
  "Nurs.":"Nursery",
  "Sch.":"School",
  "Sp.":"Special",
  "SS.":"Saints",
  "St.":"Saint",
  "Twp.":"Township"
  }

def expand_school_name(name):
    parts=name.split(" ")
    for i,p in enumerate(parts):
        if p in abbvs:
            parts[i]=abbvs[p]
    newname=" ".join(parts)
    if newname.endswith("Elementary"):
        newname=newname+" School"
    return newname

def parse_street(street):
    number=""
    idx=0
    while street[idx].isnumeric():
        number+=street[idx]
        idx+=1
    street=street[idx:].strip()
    return number,street

district_renames={
"Covenant House Academy Detroit":"Covenant House Academy",
"Covenant House Academy Grand Rapids":"Covenant House Academy",
"East Lansing School District":"East Lansing Public Schools",
"Ewen-Trout Creek Consolidated School District":"Ewen-Trout Creek School District",
"Ironwood Area Schools of Gogebic County":"Ironwood Area Schools",
"Ishpeming Public School District No. 1":"Ishpeming Public Schools",
"Muskegon, Public Schools of the City of":"Muskegon Public Schools",
"Newaygo Public School District":"Newaygo Public Schools",
"North Huron School District":"North Huron Schools",
"Nottawa Community School":"Nottawa Community Schools",
"NexTech High School of Lansing":"NexTech High School",
"Oak Park, School District of the City of":"Oak Park Schools",
"Paw Paw Public School District":"Paw Paw Public Schools",
"Peck Community School District":"Peck Community Schools",
"Unionville-Sebewaing Area S.D.":"Unionville-Sebewaing Area School District"}

levels=[{"DevK","DevK-Part","KG","KG-Part","K-Part"},
            {"1","2","3","4","5"},
            {"6","7","8"},
            {"9","10","11","12"}]
def parse_grades(grades):
    values=set(grades.split(","))
    isced=list()
    for n,level in enumerate(levels):
        if values.intersection(level):
            isced.append(str(n))
    return ";".join(isced)


def grade_sort_key(value):
    if value=="PK":
        return -1
    elif value=="K":
            return 0
    elif value=="":
        return -2
    else:
            return int(value)
             
grade_map={"DevK":"PK",
                      "DevK-Part":"PK",
                      "KG":"K",
                      "KG-Part":"K",
                      "K-Part":"K"}
def format_grades(grades):
    for k,v in grade_map.items():
        grades=grades.replace(k,v)
    values=sorted(list(set(grades.split(","))),key=grade_sort_key)
    return ";".join(values)

wikidata=dict()
with open("wikidata.csv") as source:
    data=csv.reader(source)
    header=next(data)
    for line in data:
        wikiname=line[2].rsplit("(")[0].strip()
        #~ print(wikiname)
        wikidata[wikiname]=line

with open("formatted.csv", 'w') as outfile:
    csvout=csv.writer(outfile)
    with open("reduced.csv") as infile:
        csvin=csv.reader(infile)
        header=next(csvin)
        header[0]="name"
        header[2]="phone"
        header[3]="addr:street"
        header[4]="addr:city"
        header[5]="addr:state"
        header[6]="addr:postcode"
        header[7]="operator"
        header[8]="isced:level"
        header[9]="grades"
        header.append("religion")
        header.append("denomination")
        header.extend(["wikidata","wikipedia","website"])
        header.insert(3,"addr:housenumber")
        # remove status
        header.pop(1)
        csvout.writerow(header)
        for row in csvin:
            name=expand_school_name(row[0])
            #~ if "." in name:
                #~ print(name)
            row[0]=name
            #status
            if row[1]=="Closed":
                continue
            #phone
            if row[2]:
                row[2]="+1 "+row[2][:3]+" "+row[2][3:6]+" "+row[2][6:]
            #city
            c=row[4].title().strip()
            if c.startswith("Mc "):
                c=c.replace("Mc ", "Mc")
            row[4]=c
            #postcode
            row[6]=row[6][:5]
            if "S/D" in row[7]:
                row[7]=row[7].replace("S/D", "School District")
            if row[7] in district_renames:
                row[7]=district_renames[row[7]]
            row8=row[8]
            row[8]=parse_grades(row8)
            #religion affiliation
            if row[9] in denoms:
                r,d=denoms[row[9]]
                row[9]=r
                row.append(d)
            else:
                row[9]=""
                row.append("")
            #housenumber+street, last because of insert
            number,street=parse_street(row[3])
            row[3]=street.title()
            row.insert(3,number)
            # grades
            row.insert(10,format_grades(row8))
            # add wikidata/wikipedia infos
            if name in wikidata:
                #~ print(name)
                wd=wikidata[name]
                row.append(wd[0].lstrip("http://www.wikidata.org/entity/"))
                row.append(wd[2])
                row.append(wd[4])
            # remove status
            row.pop(1)
            csvout.writerow(row)