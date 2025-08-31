

from taipy.gui import Gui

from Database.dataRequest import *

from Pages.root import root_page, updateState
from Pages.posts import post_page
from Pages.tags import tags_page
from Pages.home import home_page
from Pages.users import users_page


pages = {
    "/": root_page,
    "Home": home_page,
    "Posts": post_page,
    "Tags": tags_page,
    "Users": users_page,
}


pageTitle = ""
totalPost = 0
period = 30
endDate = datetime.today() - timedelta(days=1)
startDate = endDate - timedelta(days=period)
totalPost = getPostNumber(startDate, endDate)
page_name = "home"

maxDate = datetime.today() - timedelta(days=1)
minDate = datetime(day=1, month=4, year=2025)

renderDate = False

def on_navigate(state, page_name):
    state.page_name = page_name
    if page_name == "results" and not state.results_ready:
        return "no_results"

    if page_name == "Home":
        state.renderDate = False
        state.pageTitle = ""

    if page_name == "Posts":
        state.renderDate = True
        state.pageTitle = "## Posts Statistics"

    if page_name == "Tags":
        state.renderDate = True
        state.pageTitle = "## Tags Statistics"


    if page_name == "Users":
        state.renderDate = True
        state.pageTitle = "## Users Statistics"

    updateState(state)
    
    return page_name

gui = Gui(pages=pages)
gui.run(title="9Scrap Data visualiser", favicon="./media/icon.png")