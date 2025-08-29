import taipy.gui.builder as tgb
from datetime import datetime, timedelta
from Database.dataRequest import *

from .users import recalculateStateMostPost, recalculateBotScore
from .tags import recalculateState, recalculateStateEvol, recalculateStateTrend
from .posts import recalculateStatePosts


def updateState(state):


    state.period = (state.endDate - state.startDate).days
    state.totalPost = getPostNumber(state.startDate, state.endDate)

    if state.page_name == "Posts":
        recalculateStatePosts(state)
    
    if state.page_name == "Tags":
        if state["Tags"].partSelection == "Most popular" :
            recalculateState(state)
            
        if state["Tags"].partSelection == "Evolution":
            recalculateStateEvol(state)
        
        if state["Tags"].partSelection == "Trends":
            recalculateStateTrend(state)

    if state.page_name == "Users":
        if state["Users"].partSelectionUsers == "Most Post":
            recalculateStateMostPost(state)




def onStartDateChange(state, var_name, value):

    #change    
    state.startDate = datetime(value.year, value.month, value.day)
    state.endDate = datetime(state.endDate.year, state.endDate.month, state.endDate.day)
    if state.startDate > state.endDate :
        state.startDate = state.endDate - timedelta(days=1)
    
    updateState(state)

def onEndDateChange(state, var_name, value):

    #change    
    state.endDate = datetime(value.year, value.month, value.day)
    state.startDate = datetime(state.startDate.year, state.startDate.month, state.startDate.day)
    if state.startDate > state.endDate :
        state.startDate = state.endDate - timedelta(days=1)

    updateState(state)


with tgb.Page() as root_page:

    tgb.toggle(theme=True)

    tgb.text("# 9Scrap Data visualiser", mode="md", class_name="text-center")
    tgb.navbar()

    tgb.text("{pageTitle}", mode="md", class_name="text-center")

    tgb.html("br")

    with tgb.part("card", class_name="card card-warning card-pad-one-line"):
        tgb.text("⚠ This data presented is not representative of all the data available on 9gag, it consist of data from **" + "{totalPost}" + "** posts collected over a period of **" + "{period}" + "** day(s), but is not exhaustive. ", mode="md")

    tgb.html("br")

    with tgb.part("card", render="{renderDate}"):
        with tgb.layout(columns="1 1 1") :
            with tgb.layout(columns="1 1"):
                tgb.date("{startDate}", label="Start date", min="{minDate}", max="{endDate}", on_change=onStartDateChange)
                tgb.date("{endDate}", label="End date", min="{startDate}", max="{maxDate}", on_change=onEndDateChange)

