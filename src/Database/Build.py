import csv
import os
import sys
from datetime import datetime, timedelta
from tqdm import tqdm
import time

from unicodedata import category
from enum import IntEnum

from .openDB import *

class Column(IntEnum) :
    postId = 0
    postTitle = 1
    postType = 2
    upVoteCount = 3
    downVoteCount = 4
    commentsCount = 5
    postTags = 6
    category = 7
    creationTsp = 8
    userName = 9
    userId = 10


def botDetectionRequest():
    per_day_cte = (
        session.query(
            Post.user_id.label("user_id"),
            func.date(Post.timestamp).label("dt"),
            func.count().label("cnt")
        )
        .group_by(Post.user_id, func.date(Post.timestamp))
        .cte("per_day")
    )

    # 2. Max par jour
    max_per_day_cte = (
        session.query(
            per_day_cte.c.user_id,
            func.max(per_day_cte.c.cnt).label("max_per_day")
        )
        .group_by(per_day_cte.c.user_id)
        .cte("max_per_day")
    )

    # 3. Ranking pour calcul streak
    ranked_cte = (
        session.query(
            per_day_cte.c.user_id,
            per_day_cte.c.dt,
            func.row_number().over(
                partition_by=per_day_cte.c.user_id,
                order_by=per_day_cte.c.dt
            ).label("rn"),
            func.julianday(per_day_cte.c.dt).label("jd")
        )
        .cte("ranked")
    )

    grp_cte = (
        session.query(
            ranked_cte.c.user_id,
            (ranked_cte.c.jd - ranked_cte.c.rn).label("grp_key")
        )
        .cte("grp")
    )

    streaks_cte = (
        session.query(
            grp_cte.c.user_id,
            func.count().label("cnt")
        )
        .group_by(grp_cte.c.user_id, grp_cte.c.grp_key)
        .cte("streaks")
    )

    max_streak_cte = (
        session.query(
            streaks_cte.c.user_id,
            func.max(streaks_cte.c.cnt).label("max_streak")
        )
        .group_by(streaks_cte.c.user_id)
        .cte("max_streak")
    )

    # 4. Jointure max_per_day + max_streak
    stats_cte = (
        session.query(
            max_per_day_cte.c.user_id,
            max_per_day_cte.c.max_per_day,
            max_streak_cte.c.max_streak
        )
        .join(max_streak_cte, max_streak_cte.c.user_id == max_per_day_cte.c.user_id)
        .cte("stats")
    )

    # 5. UPDATE en masse
    stmt = (
        update(User)
        .values(
            maxPostperDay=stats_cte.c.max_per_day,
            maxStreak=stats_cte.c.max_streak
        )
        .where(User.id == stats_cte.c.user_id)
    )

    print("Start sql request...", end=" ")
    session.execute(stmt)
    session.commit()
    print("Done !")



def getFileData(path) :

    with open(path, 'r', encoding='utf-8') as f:
        num_lignes = sum(1 for _ in f) - 1

    f = open(path, 'r',encoding="utf-8")
    reader = csv.reader(f)
    #pass the first line
    next(reader)
    duplicatePost = 0
    duplicateUser = 0

    #Micro sleep because too fast make 2 tqdm lines.......
    time.sleep(0.01)

    nbLines = 0
    for row in tqdm(reader, total=num_lignes, desc=path, unit=" line(s)", colour="#555c70"):

        # create User if it doesn't exist
        if not row[Column.userId] :
            row[Column.userId] = 0
            row[Column.userName] = "anonymous"
        existing_user = session.query(User).filter_by(id=int(row[Column.userId])).first()
        if not existing_user:
            user = User(
                id=int(row[Column.userId]),
                name=row[Column.userName],
                maxStreak = 0,
                maxPostperDay = 0
            )
            session.add(user)
        else :
            duplicateUser += 1

        #remove "[" "]"
        tags = row[Column.postTags][1:-1]
        tagList = tags.split(',')
        newTagList = []
        for tag in tagList:
            #remove whitespace and '
            tag = tag.strip()[1:-1].lower()
            existing_tag = session.query(Tag).filter_by(name=tag).first()
            if not existing_tag:
                newTag = Tag(name=tag)
                newTagList.append(newTag)
            else :
                newTagList.append(existing_tag)

        session.add_all(newTagList)

        #create post if it doesn't exist
        existing_post = session.query(Post).filter_by(id=row[Column.postId]).first()
        if not existing_post:
            post = Post(
                id=row[Column.postId],
                title=row[Column.postTitle],
                type=row[Column.postType],
                upVoteCounts=int(row[Column.upVoteCount]),
                downVoteCounts=int(row[Column.downVoteCount]),
                commentsCounts=int(row[Column.commentsCount]),
                category=row[Column.category],
                timestamp=datetime.fromtimestamp(float(row[Column.creationTsp])),
                user_id=int(row[Column.userId]),
            )
            post.tags = newTagList
            session.add(post)
        else:
            duplicatePost += 1

        try:
            if nbLines % 100 == 0:
                session.commit()
        except Exception as e:
            session.rollback()
            raise e

        nbLines += 1

    session.commit()
    f.close()

    return duplicatePost, duplicateUser


def UpdateDb(sourceDirectory) :
    print("curent dir :", os.getcwd())
    files = os.listdir(sourceDirectory)
    print(f"populating DB with {len(files)} files in {sourceDirectory}")
    for filename in files:

        #test if doc already read and is csv
        existing_doc = session.query(ReadDoc).filter_by(docName=filename).first()
        if filename.endswith(".csv") and not existing_doc :
            #read the doc
            path = os.path.join(sourceDirectory, filename)
            duplicatePost, duplicateUser = getFileData(path)

            #add the doc to already read docs
            doc = ReadDoc(docName=filename, duplicatePost=duplicatePost, duplicateUser=duplicateUser)
            session.add(doc)
            session.commit()
    

def findArg(argument, argumentSecond="", defaultValue=None):
    found = False
    for arg in sys.argv:
        #we find the tag
        if arg == argument or arg == argumentSecond:
            found = True
        #next loop we return the argument
        elif found:
            return arg

    return defaultValue

if __name__ == "__main__":
    UpdateDb("../../../archive/hot")
    UpdateDb("../../../archive/fresh")
    UpdateDb("../../../archive/old")

    botDetectionRequest()
