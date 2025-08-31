import pandas as pd
from taipy.gui import Markdown
from Database.dataRequest import *
import taipy.gui.builder as tgb
from datetime import datetime, timedelta


endDatePost = datetime.today() - timedelta(days=1)
startDatePost = endDatePost - timedelta(days=period)

res = getFormatTypeUsage(startDatePost, endDatePost)
data_PostTypes = pd.DataFrame({
    "Types" : ["Images", "Animated", "Other"],
    "Area" : [res["images"], res["animated"], res["article"]]
})
imagesCp = res['images']
animatedCp = res['animated']
othersCp = res["article"]

totalPost = res["images"] + res["animated"] + res["article"]

def recalculateStatePosts(state):

    res = getFormatTypeUsage(state.startDate, state.endDate)
    state.data_PostTypes = pd.DataFrame({
        "Types" : ["Images", "Animated", "Article"],
        "Area" : [res["images"], res["animated"], res["article"]]
    })
    state.imagesCp = res['images']
    state.animatedCp = res['animated']
    state.othersCp = res["article"]



with tgb.Page() as post_page:

    tgb.html("br")
  
    with tgb.layout(columns="30% 13% 13% 13% 30%", class_name="text-center"):

        tgb.part()

        with tgb.part("card", class_name="card card-pad"):
            tgb.text("### **Images**", mode="md")
            tgb.text("{imagesCp}")

        with tgb.part("card", class_name="card card-pad"):
            tgb.text("### **Animated**", mode="md")
            tgb.text("{animatedCp}")

        with tgb.part("card", class_name="card card-pad"):
            tgb.text("### **Article**", mode="md")
            tgb.text("{othersCp}")

    tgb.html("br")

    with tgb.layout(columns="1 1 1 ") :

        tgb.part();
        
        tgb.chart("{data_PostTypes}", type='pie', values='Area', labels='Types', layout={"showlegend": True})
        
