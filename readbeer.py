import csv
from pybeerxml import Parser

path_to_beerxml_file = "cloudsafe.bsmx" #/Users/sosinski/Documents/BeerSmith3/Cloud.bsmx"

parser = Parser()
recipes = parser.parse(path_to_beerxml_file)

og_eff = {}
#for recipe in recipes:
    # some general recipe properties
    #print(recipe.name)
    #recipe.stats_pretty()

with open("session_data.csv", 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    header = True
    for recipe in recipes:
        print("Writing %s" % recipe.name)
        spamwriter.writerows(recipe.stats_csv2(header=header))
        header = False
        #if recipe.name == "Rings of Light - BIAB - BnW - 3/13/20":
        #    recipe.stats_pretty()

