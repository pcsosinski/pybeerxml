from pybeerxml import Parser

path_to_beerxml_file = "/Users/sosinski/Documents/BeerSmith3/aprilporter.bsmx"

parser = Parser()
recipes = parser.parse(path_to_beerxml_file)


for recipe in recipes:
    #print dir(recipe)
  
    #print "recipe?"
    #print recipe.og
    #print recipe.fg
    #print recipe.ibu
    #print recipe.abv
    #print 'mash'
    #print(dir(recipe.mash))
    #print recipe.mash.notes
    #print "mash steps"
    #for step in recipe.mash.steps:
    #   print (step.name)
    # some general recipe properties
    print(recipe.name)
    print(recipe.brewer)
    for yeast in recipe.yeasts:
        print(yeast.name)
        print(yeast.attenuation)
    # calculated properties
    print("OG:\n beerxml: %s\n bs est: %s\n bs actual: %s" % (recipe.og, recipe.est_og, recipe.og_measured))
    print ("FG:\n beerxml: %s\n bs est: %s\n bs actual: %s" % (recipe.fg, recipe.est_fg, recipe.fg_measured))
    print ("ABV:\n beerxml: %s\n bs est: %s\n bs actual: %s" % (recipe.abv, recipe.est_abv, recipe.abv_measured))    
    #print "BH Efficiency:\n bs est: %s\n bs actual: %s" % (recipe.efficiency, recipe.actual_efficiency)

    #print recipe.display_boil_size
    # iterate over the ingredients
    #for hop in recipe.hops:
        #print(hop.name)

    #for fermentable in recipe.fermentables:
        #print(fermentable.name)
	#print fermentable.amount
        #print fermentable._yield
    for yeast in recipe.yeasts:
        print(yeast.name)
        print(yeast.attenuation)

    #for misc in recipe.miscs:
        #print(misc.name)
