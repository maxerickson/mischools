import csv
keys=["EntityOfficialName","EntityStatus","EntityPhone",
           "EntityPhysicalStreet","EntityPhysicalCity",
           "EntityPhysicalState","EntityPhysicalZip4",
           "DistrictOfficialName",
           "EntityActualGrades","EntityReligiousOrientationName"]
with open("reduced.csv", 'w') as outfile:
    csvout=csv.writer(outfile)
    csvout.writerow(keys)
    with open("EEMDataReport") as infile:
        csvin=csv.DictReader(infile)
        for row in csvin:
            newrow=[row[key] for key in keys]
            #~ print(newrow)
            csvout.writerow(newrow)