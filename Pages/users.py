import pandas as pd
from Database.dataRequest import *
import taipy.gui.builder as tgb
from datetime import datetime, timedelta

partSelectionUsers = "Most Post"
boolMPU = True
boolBS = False

endDateUsers = datetime.today() - timedelta(days=1)
startDateUsers = endDateUsers - timedelta(days=period)

sliderValuesUser = [0, 20]
mostPostRes = getMostPostUser(sliderValuesUser[0], sliderValuesUser[1], startDateUsers, endDateUsers)
data_mostPost = pd.DataFrame([ [u.name, c] for u, c in mostPostRes], columns=["Username","Post Number"])
userList = [u.name for u, c in mostPostRes]
userHidden = []


AllUserList = getAllUsers()
userSelected = userList[0]

streakColorMap = {0:"green", 5:"orange",10:"red"}
maxAdayColorMap = {0:"green", 2:"orange",5:"red"}
userInfo = getUserBotScore(userSelected)

maxPostDay = userInfo['user']['maxPostperDay']
maxStreak = userInfo['user']['maxStreak']
postCount = userInfo['posts_count']
tags = [tt['tag'] for tt in userInfo['top_tags']]
categories = [tc['category'] for tc in userInfo['top_categories']]

def recalculateStateMostPost(state):
    mostPostRes = getMostPostUser(state.sliderValuesUser[0], state.sliderValuesUser[1], state.startDate, state.endDate)
    state.data_mostPost = pd.DataFrame([ [u.name, c] for u, c in mostPostRes if u.name not in state.userHidden], columns=["Username","Post Number"])
    state.userList = [u.name for u, c in mostPostRes]

def recalculateBotScore(state):
    userInfo = getUserBotScore(state.userSelected)

    state.maxPostDay = userInfo['user']['maxPostperDay']
    state.maxStreak = userInfo['user']['maxStreak']
    state.postCount = userInfo['posts_count']
    state.tags = [tt['tag'] for tt in userInfo['top_tags']]
    state.categories = [tc['category'] for tc in userInfo['top_categories']]
    

def onUserHiddenListChange(state, var_name, value):
    state.userHidden = value

    recalculateStateMostPost(state)

def onsliderValuesUserChange(state, var_name, value):
    state.sliderValuesUser = [int(value[0]), int(value[1])]

    recalculateStateMostPost(state)

def onUserSelectedChange(state, var_name, value):
    state.userSelected = value

    recalculateBotScore(state)


def onPartSelectionChange(state, var_name, value):

    state.boolMPU = False
    state.boolBS = False
    if value == "Most Post" :
        state.boolMPU = True
        state.renderDate = True
    if value == "Bot Score" :
        state.boolBS = True
        state.renderDate = False


with tgb.Page() as users_page:


    tgb.html("br")
    tgb.toggle("{partSelectionUsers}", lov="Most Post;Bot Score", on_change=onPartSelectionChange)
    tgb.html("br")

    with tgb.part("card", render="{boolMPU}"):
        tgb.text("### Biggest Posters", mode="md")
        with tgb.layout(columns="3% 40% 10% 20%"):
            tgb.part()
            with tgb.part():
                tgb.text("Number of tags range :")
                tgb.slider("{sliderValuesUser}", labels="True",  lov="0;10;20;30;40;50;60;70;80;90;100", on_change=onsliderValuesUserChange)

            tgb.part()
            with tgb.part() :
                tgb.text("User(s) to exclude from the chart :")
                tgb.selector("{userHidden}", lov="{userList}", filter=True, multiple=True, dropdown=True, on_change=onUserHiddenListChange)

        tgb.html("br")

        tgb.chart("{data_mostPost}", type="bar", orientation="v", y="Post Number", x="Username")


    with tgb.part("card", render="{boolBS}"):
        tgb.text("### Bot Score", mode="md")
        with tgb.part() :
            tgb.text("User :")
            tgb.selector("{userSelected}", lov="{AllUserList}", filter=True, dropdown=True, on_change=onUserSelectedChange)
        
        tgb.html("br")

        tgb.text("### {userSelected}", mode="md")
        tgb.text("##### Post number : **{postCount}**", mode="md")

        with tgb.layout(columns="1 1 1 1"):
            
            with tgb.part("card"):
                tgb.text("Most used Tags")
                tgb.selector("", lov="{tags}", active=False)

            with tgb.part("card"):
                tgb.text("Most used Categories")
                tgb.selector("", lov="{categories}", active=False)

     
            with tgb.part("card", class_name="card card-pad-one-line"):
                tgb.metric("{maxStreak}", format="%d day(s)", height="350px", width="100%", color_map="{streakColorMap}", min="0", max="20", bar_color="black", title="Max streak of posts")
        
            with tgb.part("card", class_name="card card-pad-one-line"):
                tgb.metric("{maxPostDay}", format="%d post(s)", height="350px", width="100%", color_map="{maxAdayColorMap}", min="0", max="10", bar_color="black", title="Max post in 1 day")


