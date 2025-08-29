import pandas as pd
from Database.dataRequest import *
import taipy.gui.builder as tgb
from datetime import datetime, timedelta


partSelection = "Most popular"
boolMP = True
boolEvo = False
boolTrends = False

totalPost = 0

period = 30
endDateTags = datetime.today() - timedelta(days=1)
startDateTags = endDateTags - timedelta(days=period)


sliderValues = [0, 20]

resPop = getPopularTag(sliderValues[0], sliderValues[1], startDateTags, endDateTags)
posts = [ (k,v) for k, v in resPop.items()]
data_tagsUsage = pd.DataFrame(resPop["tags"], columns=["Tags","Post Number"])

tagList = [f[0] for f in resPop["tags"]]
tagsHidden = ""

res2 = getTagEvolutionInTime(tagList[0], startDateTags, endDateTags)
data_evol = {
    "date" : [r["average"].strftime('%m/%d/%Y') for r in res2],
    "Post Number" : [r["count"] for r in res2]
}

tagEvol = tagList[0]
allTags = getAllUsedTags(startDateTags, endDateTags)

resTrend = getTagsTrend(startDateTags, endDateTags, 10, "slope")
boolTrendSlope = True 
columnsTrend = {
    "Tag": {"title": "Tag"},
    "Percentage**": {"title": "Percentage**", "format": "%.0f %%"},
    "Slope*": {"title": "Slope*", "format": "%.0f posts"},
}
data_trend_up = {
    "Tag" : ["↗ "+r["tag"] for r in resTrend["up"]],
    "Slope*": [int(r["slope"])  for r in resTrend["up"]],
    "Percentage**": [int(r["pct_change"]) for r in resTrend["up"]]
}
data_trend_down = {
    "Tag" : ["↘ "+r["tag"] for r in resTrend["down"]],
    "Slope*": [int(r["slope"]) for r in resTrend["down"]],
    "Percentage**": [int(r["pct_change"]) for r in resTrend["down"]]
}

def recalculateState(state):

    state.period = (state.endDate - state.startDate).days
    resPop = getPopularTag(state.sliderValues[0], state.sliderValues[1], state.startDate, state.endDate)
    hidenList = [f for f in resPop["tags"] if f[0] not in state.tagsHidden]
    state.tagList = [f[0] for f in resPop["tags"]]
    state.data_tagsUsage =  pd.DataFrame(hidenList, columns=["Tags", "Post Number" ])

def recalculateStateEvol(state):

    state.period = (state.endDate - state.startDate).days
    res2 = getTagEvolutionInTime(state.tagEvol, state.startDate, state.endDate)
    state.data_evol = {
        "date" : [r["average"].strftime('%m/%d/%Y') for r in res2],
        "Post Number" : [r["count"] for r in res2]
    }

def recalculateStateTrend(state):


    state.period = (state.endDate - state.startDate).days

    if state.boolTrendSlope :
        sortby = "slope"
    else : 
        sortby = "pct_change"
    resTrend = getTagsTrend(state.startDate, state.endDate, 10, sortby)
    state.data_trend_up = {
        "Tag" : ["↗ "+r["tag"] for r in resTrend["up"]],
        "Percentage**": [round(r["pct_change"]) for r in resTrend["up"]],
        "Slope*": [round(r["slope"])  for r in resTrend["up"]],
    }
    state.data_trend_down = {
        "Tag" : ["↘ "+r["tag"] for r in resTrend["down"]],
        "Percentage**": [round(r["pct_change"]) for r in resTrend["down"]],
        "Slope*": [round(r["slope"]) for r in resTrend["down"]],
    }


def onRangeChange(state, var_name, value):
    state.sliderValues = [int(value[0]), int(value[1])]

    recalculateState(state)

def onTagsHiddenChange(state, var_name, value):
    state.tagsHidden = value

    recalculateState(state)

def onTagEvolChange(state, var_name, value):
    state.tagEvol = value

    recalculateStateEvol(state)

def onToggleTrendChange(state, var_name, value):
    state.boolTrendSlope = value

    recalculateStateTrend(state)

def onPartSelectionChange(state, var_name, value):

    state.boolMP = False
    state.boolEvo = False
    state.boolTrends = False
    
    if value == "Most popular" :
        state.boolMP = True
        
    if value == "Evolution":
        state.boolEvo = True
    
    if value == "Trends":
        state.boolTrends = True

    

with tgb.Page() as tags_page:

    tgb.html("br")
    tgb.toggle("{partSelection}", lov="Most popular;Evolution;Trends", on_change=onPartSelectionChange)
    tgb.html("br")

    with tgb.part("card", render="{boolMP}"):
        tgb.text("### Most popular Tags", mode="md")
        with tgb.layout(columns="3% 40% 10% 20%"):
            tgb.part()
            with tgb.part():
                tgb.text("Number of tags range :")
                tgb.slider("{sliderValues}", labels="True",  lov="0;10;20;30;40;50;60;70;80;90;100", on_change=onRangeChange)

            tgb.part()
            with tgb.part() :
                tgb.text("Tag(s) to exclude from the chart :")
                tgb.selector("{tagsHidden}", lov="{tagList}", filter=True, multiple=True, dropdown=True, on_change=onTagsHiddenChange)

        tgb.html("br")

        tgb.chart("{data_tagsUsage}", type="bar", orientation="v", y="Post Number", x="Tags")

    with tgb.part("card", render="{boolEvo}") :
        tgb.text("### Evolution of the Tag", mode="md")
        tgb.selector("{tagEvol}", lov="{allTags}", filter=True, dropdown=True, on_change=onTagEvolChange)
        tgb.chart("{data_evol}", x="date", y="Post Number")

    with tgb.part("card", render="{boolTrends}") :
        tgb.text("### Trend of Tags", mode="md")
        tgb.text("###### The trend is calculated based on the difference between the first half and the second half of the selected period", mode="md")
        tgb.html("br")
        
        tgb.toggle("{boolTrendSlope}", on_change=onToggleTrendChange, label="Top by relative growth")
        tgb.table("{data_trend_up}", number_format="%.02f", show_all=True, class_name="stonk", columns="{columnsTrend}")
        tgb.table("{data_trend_down}", number_format="%.02f", show_all=True, class_name="not-stonk", columns="{columnsTrend}")

        tgb.html("br")

        tgb.text("* : Slope represent an absolute growth or decrease")
        tgb.text("** : Percentage represent a relative growth or decrease")

