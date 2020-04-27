from xml.etree import ElementTree
from .recipe import *
from .hop import Hop
from .mash import Mash
from .mash_step import MashStep
from .misc import Misc
from .yeast import Yeast
from .style import Style
from .fermentable import Fermentable
import sys


bsmx_overrides = {
        "abv": "bs_actual_abv",
        "og": "bs_actual_og",
        "fg": "bs_actual_fg",
}
 
class Parser(object):

    def nodes_to_object(self, node, object):
        "Map all child nodes to an object's attributes"

        for n in list(node):
            self.node_to_object(n, object)

    def node_to_object(self, node, object):
        "Map a single node to an object's attributes"

        tag = self.to_lower(node.tag)
        if tag.startswith('f_'):
            tag = tag[tag.find('_', 2)+1:]
        try:
            attribute = bsmx_overrides[tag]
            print("yay: " + attribute)
        except KeyError:
            attribute = tag
        # Yield is a protected keyword in Python, so let's rename it
        attribute = "_yield" if attribute == "yield" else attribute

        try:
            valueString = node.text or ""
            value = float(valueString)
        except ValueError:
            value = node.text

        try:
            setattr(object, attribute, value)
        except AttributeError():
            sys.stderr.write("Attribute <%s> not supported." % attribute)

    def parse(self, xml_file):
        "Get a list of parsed recipes from BeerXML input"

        recipes = []

        parser = ElementTree.XMLParser()
#        parser.parser.UseForeignDTD(True)
# in case you want to parse cloud.bsmx directly
# but probably not
#        parser.entity["lsquo"] = "'"
#        parser.entity["rsquo"] = "'"
#        parser.entity["deg"] = "*"
#        parser.entity["ldquo"] = '"'
#        parser.entity["rdquo"] = '"'
#        parser.entity["uuml"] = "u"
#        parser.entity["auml"] = "a"
#        parser.entity["ndash"] = "-"
#        parser.entity["ouml"] = "o"
#        parser.entity["reg"] = "R"
#        parser.entity["trade"] = "TM"
#        parser.entity["ccedil"] = ""
#        parser.entity["AElig"] = ""
        with open(xml_file, "rt") as f:
            tree = ElementTree.parse(f)
            #etree = ElementTree.ElementTree()

            #tree = etree.parse(f, parser=parser)

        for recipeNode in tree.iter():
            #print recipeNode.tag
            if self.to_lower(recipeNode.tag) != "recipe":
                continue

            recipe = Recipe()
            recipes.append(recipe)
            for recipeProperty in list(recipeNode):
                tag_name = self.to_lower(recipeProperty.tag)
                if tag_name.startswith('f_'):
                    tag_name = tag_name[tag_name.find('_', 2)+1:]
                    #print(tag_name)

                if tag_name == "ingredients":
                    #print("made it to ingredients!")
                    for ing_node in list(recipeProperty.find('Data')):
                        ing_tag = self.to_lower(ing_node.tag)
                        #print(ing_tag)
                        if ing_tag == "grain":
                            #print("made it to grain!")
                            fermentable = Fermentable()
                            self.nodes_to_object(ing_node, fermentable)
                            recipe.fermentables.append(fermentable)

                        elif ing_tag == "yeast":
                            print("made it to yeast")
                            yeast = Yeast()
                            self.nodes_to_object(ing_node, yeast)
                            recipe.yeasts.append(yeast)

                        elif ing_tag == "hops":
                            hop = Hop()
                            self.nodes_to_object(ing_node, hop)
                            recipe.hops.append(hop)

                        elif ing_tag == "misc":
                            misc = Misc()
                            self.nodes_to_object(ing_node, misc)
                            recipe.miscs.append(misc)

                elif tag_name == "mash":
                    mash = Mash()
                    recipe.mash = mash

                    for mash_node in list(recipeProperty):
                        print(mash_node.tag)
                        if self.to_lower(mash_node.tag) == "mash_steps":
                            for mash_step_node in list(mash_node):
                                mash_step = MashStep()
                                self.nodes_to_object(mash_step_node, mash_step)
                                mash.steps.append(mash_step)
                        else:
                            self.nodes_to_object(mash_node, mash)
                else:
                    self.node_to_object(recipeProperty, recipe)

        return recipes

    def to_lower(self, string):
        "Helper function to transform strings to lower case"
        value = None
        try:
            value = string.lower()
        except AttributeError:
            value = ""
        finally:
            return value
