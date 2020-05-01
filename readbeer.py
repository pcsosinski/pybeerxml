from pybeerxml import Parser

path_to_beerxml_file = "cloudsafe.bsmx" #/Users/sosinski/Documents/BeerSmith3/Cloud.bsmx"

parser = Parser()
recipes = parser.parse(path_to_beerxml_file)


for recipe in recipes:
    # some general recipe properties
    print(recipe.name)
    print(recipe.brewer)

    session = recipe.session
    # calculated properties
    print("OG:\n beerxml (estimate from planned vol): %s\n bs est: %s\n measured: %s" % (recipe.og, recipe.est_og, session.og_measured))
    print ("FG:\n beerxml: %s\n bs est: %s\n measured: %s" % (recipe.fg, recipe.est_fg, session.fg_measured))
    print ("ABV:\n beerxml: %s\n bs est: %s\n measured: %s" % (recipe.abv, recipe.est_abv, recipe.abv_measured)) 
    print("Fermenter Volume:\n exp: %s\n measured: %s" % (recipe.batch_size, recipe.session.batch_size)) 
    print ("Efficiency:\n BH exp: %s\n BH measured: %s" % (recipe.efficiency, recipe.efficiency_measured))
    yeast = recipe.yeasts[0]
    print("Attenuation:\n exp: %s\n actual: %s" % (yeast.attenuation, session.attenuation))
