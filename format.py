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
    fieldnames=["name","phone","addr:housenumber","addr:street","addr:city",
                        "addr:state","addr:postcode","operator","isced:level","grades",
                        "religion","denomination","wikidata","wikipedia","website"]
    csvout=csv.DictWriter(outfile, restval='',fieldnames=fieldnames, extrasaction='ignore')
    csvout.writeheader()
    # The fields used are
    # EntityOfficialName,EntityStatus,EntityPhone,
    # EntityPhysicalStreet,EntityPhysicalCity,
    # EntityPhysicalState,"EntityPhysicalZip4,
    # DistrictOfficialName,
    # EntityActualGrades,EntityReligiousOrientationName
    with open("EEMDataReport") as infile:
        csvin=csv.DictReader(infile)
    #~ with open("reduced.csv") as infile:
        #~ csvin=csv.reader(infile)
        #~ header=next(csvin)
        for row in csvin:
            school=dict()
            school["name"]=expand_school_name(row["EntityOfficialName"])
            if row["EntityStatus"]=="Closed":
                continue
            #phone
            if row["EntityPhone"]:
                school["phone"]="+1 "+row["EntityPhone"][:3]+" "+row["EntityPhone"][3:6]+" "+row["EntityPhone"][6:]
            number,street=parse_street(row["EntityPhysicalStreet"])
            school["addr:street"]=street.title()
            school["addr:housenumber"]=number
            #city
            c=row["EntityPhysicalCity"].title().strip()
            if c.startswith("Mc "):
                c=c.replace("Mc ", "Mc")
            school["addr:city"]=c
            school["addr:state"]=row["EntityPhysicalState"]
            #postcode
            school["addr:postcode"]=row["EntityPhysicalZip4"][:5]
            district=row["DistrictOfficialName"]
            if "S/D" in district:
                district=district.replace("S/D", "School District")
            if district in district_renames:
                district=district_renames[district]
            school["operator"]=district
            school["isced:level"]=parse_grades(row["EntityActualGrades"])
            school["grades"]=format_grades(row["EntityActualGrades"])
            #religion affiliation
            if row["EntityReligiousOrientationName"] in denoms:
                r,d=denoms[row["EntityReligiousOrientationName"]]
                school["religion"]=r
                school["denomination"]=d
            # add wikidata/wikipedia infos
            if school["name"] in wikidata:
                #~ print(name)
                wd=wikidata[school["name"]]
                school['wikidata']=wd[0].lstrip("http://www.wikidata.org/entity/")
                school['wikipedia']=wd[2]
                school['website']=wd[4]
            csvout.writerow(school)