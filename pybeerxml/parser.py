from xml.etree import ElementTree
from .recipe import *
from .hop import Hop
from .mash import Mash
from .mash_step import MashStep
from .misc import Misc
from .yeast import Yeast
from .style import Style
from .fermentable import Fermentable
from .session import Session
from .equipment import Equipment
import sys


session_variables = [
        'mash_ph',
        'boil_vol_measured', # ounces preboil
        'og_boil_measured', # pre boil gravity
        'volume_measured', # batch size into ferm
        'og_measured', # Measured OG
        'final_vol_measured', # bottling amount (oz)
        'fg_measured', # Measured FG
        'date', # Brew date
        ]
 
class Parser(object):

    def nodes_to_object(self, node, object):
        "Map all child nodes to an object's attributes"

        for n in list(node):
            self.node_to_object(n, object)

    def node_to_object(self, node, object):
        "Map a single node to an object's attributes"

        tag = self.to_lower(node.tag)
        if tag.startswith('f_'):
            attribute = tag[tag.find('_', 2)+1:]
        else:
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
        with open(xml_file, "rt") as f:
            tree = ElementTree.parse(f)

        # get table IDs for the folders
        # we want folders named "Brew Sessions"
        brew_session_table_ids = []
        for table in tree.iter():
            if table.tag == "Table":
                if table.find('Name').text == "Brew Sessions":
                    brew_session_table_ids.append(table.find("TExtra").text)
        for recipeHeader in tree.iter():
            if self.to_lower(recipeHeader.tag) != "cloud":
                continue
            # make sure this cloud header is a recipe
            if not recipeHeader.find("F_C_RECIPE"):
                continue
            if recipeHeader.find("F_C_FOLDER_ID").text not in brew_session_table_ids:
                continue
            recipeNode = recipeHeader.find("F_C_RECIPE")
            recipe = Recipe()
            # TODO(fix all this shit)
            recipe.est_og = float(recipeHeader.find("F_R_OG").text)
            recipe.est_fg = float(recipeHeader.find("F_R_FG").text)
            recipe.est_abv = float(recipeHeader.find("F_R_EST_ABV").text)
            recipe.volume = float(recipeHeader.find("F_R_VOLUME").text)
            recipe.efficiency = float(recipeHeader.find("F_R_EFFICIENCY").text)/100
            recipe.est_boil_vol = float(recipeHeader.find("F_R_BOIL_VOL").text)
            recipe.boil_time = float(recipeHeader.find("F_R_BOIL_TIME").text)
            recipes.append(recipe)
            for recipeProperty in list(recipeNode):
                tag_name = self.to_lower(recipeProperty.tag)
                if tag_name.startswith('f_'):
                    tag_name = tag_name[tag_name.find('_', 2)+1:]
                    #print("%s: %s" % (tag_name, recipeProperty.text))
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
                            #print("made it to yeast")
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

                elif tag_name == "equipment":
                    if recipe.session:
                        session = recipe.session
                    else:
                        session = Session()
                        recipe.session = session

                    equip = Equipment()
                    session.equipment = equip
                    self.nodes_to_object(recipeProperty, equip)

                elif tag_name == "mash":
                    mash = Mash()
                    recipe.mash = mash

                    for mash_node in list(recipeProperty):
                        #print(mash_node.tag)
                        if self.to_lower(mash_node.tag) == "mash_steps":
                            for mash_step_node in list(mash_node):
                                mash_step = MashStep()
                                self.nodes_to_object(mash_step_node, mash_step)
                                mash.steps.append(mash_step)
                        else:
                            self.nodes_to_object(mash_node, mash)
                elif tag_name in session_variables:
                    if recipe.session:
                        session = recipe.session
                    else:
                        session = Session()
                        recipe.session = session
                    #print(tag_name)
                    self.node_to_object(recipeProperty, session)

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
