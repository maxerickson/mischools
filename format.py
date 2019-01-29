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
    return " ".join(parts)

def parse_street(street):
    number=""
    idx=0
    while street[idx].isnumeric():
        number+=street[idx]
        idx+=1
    street=street[idx:].strip()
    return number,street

levels=[{"DevK","DevK-Part","KG","KG-Part"},
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
        header[9]="religion"
        header.append("denomination")
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
            row[4]=row[4].title().strip()
            #postcode
            row[6]=row[6][:5]
            row[8]=parse_grades(row[8])
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
            # remove status
            row.pop(1)
            csvout.writerow(row)