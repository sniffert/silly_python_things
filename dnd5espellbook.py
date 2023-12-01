import streamlit as st
import pandas as pd
import requests as r

# Schools of Magic Data
magicSchoolURL = "https://www.dnd5eapi.co/api/magic-schools/"
msData = ["Abjuration", "Conjuration", "Divination", "Enchantment", "Evocation", "Illusion", "Necromancy", "Transmutation"]

# Sidebar Navigation
st.sidebar.title("Spellbook Search") #NEW
search_val = st.sidebar.text_input("Search by Name") #NEW
spell_lvl = st.sidebar.number_input("Select Spell Level", min_value=0, max_value=9, value=0) #NEW
spell_school = st.sidebar.radio("Input School of Magic", msData) #NEW

allSpells = r.get("https://www.dnd5eapi.co/api/spells/").json()["results"]
boolCheck = True
# Direct Search Function        
def directSearch(search_val):
    inputSpell = search_val
    for spellDict in allSpells:
        if inputSpell.lower() == spellDict["name"].lower():
            boolCheck = False
            spellURL = spellDict["url"]
            spellURL = "https://www.dnd5eapi.co" + spellURL
            spellTitleDesc(spellURL)
            spellAttackInfo(spellURL)
            spellCastingInfo(spellURL)

# Spellbook Page
def spellTitleDesc(spellURL):
    spellInfo = r.get(spellURL).json()
    st.header(spellInfo["name"])
    st.subheader("Description")
    st.write(spellInfo["desc"][0])
    if spellInfo["higher_level"] != []:
        st.write(spellInfo["higher_level"][0])
    st.write("---")

# Spell Attack Info
def spellAttackInfo(spellURL):
    spellInfo = r.get(spellURL).json()
    if "damage" in spellInfo:
        st.subheader("Attack Information")
        RADict = attackInfoDictBuilder(spellInfo)
        attackInfo = pd.DataFrame(RADict)
        st.dataframe(attackInfo, column_config={"damage_type": "Damage Type", "casting_time": "Casting Time", "duration": "Duration"},hide_index=True,)
        st.write("---")
    elif "heal_at_slot_level" in spellInfo:
        st.subheader("Healing Information")
        HELdict = attackInfoDictBuilder(spellInfo)
        healInfo = pd.DataFrame(HELdict)
        st.dataframe(healInfo, column_config={"casting_time": "Casting Time", "duration": "Duration"},hide_index=True,)


def attackInfoDictBuilder(spellInfo):
    if "damage" in spellInfo and "damage_at_slot_level" in spellInfo["damage"]:
        retAttackDict = {"damage_type":[spellInfo["damage"]["damage_type"]["name"]],
                        "casting_time":[spellInfo["casting_time"]],
                        "duration":[spellInfo["duration"]],
                        "Attack Die":[spellInfo["damage"]["damage_at_slot_level"][str(spellInfo["level"])]]
                        }
    elif "damage" in spellInfo and "damage_at_character_level" in spellInfo["damage"]:
        retAttackDict = {"damage_type":[spellInfo["damage"]["damage_type"]["name"]],
                        "casting_time":[spellInfo["casting_time"]],
                        "duration":[spellInfo["duration"]],
                        }
    elif "heal_at_slot_level" in spellInfo:
        retAttackDict = {"casting_time":[spellInfo["casting_time"]],
                        "duration":[spellInfo["duration"]],
                        "Healing at Lowest Slot Level":[spellInfo["heal_at_slot_level"][str(spellInfo["level"])]]
                        }
    return retAttackDict



def spellCastingInfo(spellURL):
    spellInfo = r.get(spellURL).json()
    st.subheader("Casting Information")
    tab1, tab2, tab3, tab4 = st.tabs(["Components", "Materials", "Ritual", "Concentration"])
    with tab1:
        st.subheader("Components")
        if "V" in spellInfo["components"]:
            st.write("Verbal - Casting this spell requires a verbal element, such as speaking an incantation or using a particular word.")
        if "S" in spellInfo["components"]:
            st.write("Somatic - Casting this spell requires some sort of hand motion.")
        if "M" in spellInfo["components"]:
            st.write("Material - Casting this spell requires specific materials. If the specified materials do not have a stated monetary value, a Casting Focus can be used instead.")
    with tab2:
        if "M" not in spellInfo["components"]:
            st.write("This spell does not have material components.")
        else:
            st.write(spellInfo["material"])
    with tab3:
        if spellInfo["ritual"]:
            st.write("Certain spells have a special tag: ritual. Such a spell can be cast following the normal rules for spellcasting, or the spell can be cast as a ritual. The ritual version of a spell takes 10 minutes longer to cast than normal. It also doesn't expend a spell slot, which means the ritual version of a spell can't be cast at a higher level. To cast a spell as a ritual, a spellcaster must have a feature that grants the ability to do so.")
        else:
            st.write("This spell cannot be cast as a ritual.")
    with tab4:
        if spellInfo["concentration"]:
            st.write("Some spells require you to maintain concentration in order to keep their magic active. If you lose concentration, such a spell ends.")
        else:
            st.write("This spell does not require concentration")
    st.write("---")


# "Title Page"
def titlePage():
    st.title("Will's Portable Spellbook")
    st.image("https://www.enworld.org/attachments/wizard-png.80084/")
    st.header("Using this Guide")
    st.write("Written and enchanted by Will's Wizarding Co., this Spellbook is a digital collection of spell information from Dungeons and Dragons 5th Edition. To use this guide, either search for a spell directly or use the filters to see a list of possible spells, located at the bottom of the page.")
    st.write("---")

# Filter Tool
def filterInfo(spell_lvl, spell_school):
    if boolCheck:
        st.header("Spells Matching Filters")
        counter = 0
        limitSpellList = "https://www.dnd5eapi.co/api/spells/?level=" + str(spell_lvl)
        limitSpellList = r.get(limitSpellList).json()
        limitSpellList = limitSpellList["results"]
        for spellDict in limitSpellList:
            schoolVar = r.get("https://www.dnd5eapi.co" + spellDict["url"]).json()["school"]["name"]
            schoolCheck = schoolVar == spell_school
            if schoolCheck:
                st.write(spellDict["name"])
                counter += 1
        st.subheader("Portion of All Spells")
        st.progress(counter/319)
        st.write("---")

titlePage()
directSearch(search_val)
filterInfo(spell_lvl, spell_school)