import taipy.gui.builder as tgb

with tgb.Page() as home_page:
    with tgb.layout(columns="30% 40% 30%", class_name="text-center"):

        tgb.part()

        with tgb.layout(columns="1"):
            tgb.text("# Welcome to **9Scrap**", mode="md")
            tgb.image("./media/9scrap.png")
            
            tgb.html("br")
            tgb.text("This project presents an interactive view of data scraped from 9GAG.\n\n" \
            "The collected dataset is only a partial representation of the platform’s content and should not be considered exhaustive.\n\n" \
            "Although the dataset does not include every post or piece of content available on the platform, it offers a representative snapshot that can be used to observe, explore, and better understand certain patterns and trends over time." \
            "The purpose is to provide an accessible overview rather than a complete archive.\n\n " \
            "All original content and data remain the property of 9GAG. \n", mode="md")
            tgb.html("br")
