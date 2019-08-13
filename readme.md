Project to integrate data from https://www.cepi.state.mi.us/eem/PublicDatasets.aspx 
into OpenStreetMap.

Currently there's tags for copy-paste at [https://maxerickson.github.io/mischools/](https://maxerickson.github.io/mischools/),
sorted by school district.

Use mitwp.sparq to fetch wikidata ids:

    curl -G "https://query.wikidata.org/sparql?" -o wikidata.csv -H "Accept: text/csv" --data-urlencode query="$(< highschools.sparql)"