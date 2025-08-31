from datetime import date, timedelta
import numpy as np

from sqlalchemy import create_engine, func, desc, cast
from sqlalchemy.orm import sessionmaker, joinedload
from .models import *

engine = create_engine('sqlite:///Database/9Scrap.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def getPostNumber(start, end):
    return session.query(Post).filter(Post.timestamp >= start).filter(Post.timestamp <= end).count()

def getFormatTypeUsage(start, end):

    images = session.query(Post).filter(Post.type == "Photo").filter(Post.timestamp >= start).filter(Post.timestamp <= end).count()
    animated = session.query(Post).filter(Post.type == "Animated").filter(Post.timestamp >= start).filter(Post.timestamp <= end).count()
    article = session.query(Post).filter(Post.type == "Article").filter(Post.timestamp >= start).filter(Post.timestamp <= end).count()
    other = session.query(Post).filter(Post.type != "Animated").filter(Post.type != "Photo").filter(Post.type != "Article").filter(Post.timestamp >= start).filter(Post.timestamp <= end).all()

    #remove duplicate
    otherTypes = [o.type for o in other]
    otherTypes = list(dict.fromkeys(otherTypes))

    types = {
        "images" : images,
        "animated" : animated,
        "article" : article,
        "others" : len(other),
        "other_detail" : otherTypes
    }
    return types



def getPopularTag(minTag, maxTag, start, end):

    tag_counts = (
        session.query(Tag.name, func.count(post_tag_association.c.post_id))
        .join(post_tag_association, Tag.name == post_tag_association.c.tag_id)
        .join(Post, Post.id == post_tag_association.c.post_id)
        .filter(Post.timestamp >= start)
        .filter(Post.timestamp <= end)
        .group_by(Tag.name)
        .order_by(func.count(post_tag_association.c.post_id).desc())
        .offset(minTag)   
        .limit(maxTag - minTag)
        .all()
    )

    tags = {"tags" : tag_counts}
    return tags


def getMostPostUser(minUser,maxUser, start, end):


    users = (
        session.query(User, func.count(Post.id).label('post_count'))
        .outerjoin(Post)  # outerjoin to include users with 0 posts
        .filter(Post.timestamp >= start)
        .filter(Post.timestamp <= end)
        .group_by(User.id)
        .order_by(desc('post_count'))
        .offset(minUser)
        .limit(maxUser - minUser)
        .all()
    )

    return users

def getAllUsedTags(start, end, minpost=10):
    
    tags = (
        session.query(Tag.name, func.count(Post.id).label("post_count"))
        .join(Tag.posts)  
        .filter(
            Post.timestamp >= start,
            Post.timestamp <= end
        )
        .group_by(Tag.name)
        .having(func.count(Post.id) > minpost)
        .all()
    )

    
    a = [ n for (n, b) in tags]
    
    return a


def getTagEvolutionInTime(tag, start, end):
    date_start = date(start.year, start.month, start.day)
    date_end = date(end.year, end.month, end.day + 1)

    total_days_inclusive = (date_end - date_start).days

    # choisir un nombre de buckets entre 15 et 30
    # ici on vise ~20 mais on ajuste si trop petit ou trop grand
    bucket_size = round(total_days_inclusive / 20)
    nb_buckets = round(total_days_inclusive / bucket_size)

    # taille d'un bucket (même pour tous)
    bin_days = total_days_inclusive / nb_buckets

    bin_expr = func.floor(
        (func.julianday(Post.timestamp) - func.julianday(date_start)) / bin_days
    ).label("bucket")

    rows = (
        session.query(
            bin_expr,
            func.count(Post.id).label("count")
        )
        .join(Post.tags)
        .filter(
            Tag.name == tag,
            Post.timestamp >= date_start,
            Post.timestamp <= date_end
        )
        .group_by(bin_expr)
        .order_by(bin_expr)
        .all()
    )

    bucket_dict = {b: c for b, c in rows}

    points = []
    for b in range(nb_buckets):
        start_bucket = date_start + timedelta(days=round(b * bin_days))
        end_bucket = date_start + timedelta(days=round((b + 1) * bin_days) - 1)
        if end_bucket > date_end:
            end_bucket = date_end

        average_date = start_bucket + (end_bucket - start_bucket) / 2

        points.append({
            "start": start_bucket,
            "end": end_bucket,
            "average": average_date,
            "count": int(bucket_dict.get(b, 0))
        })

    return points


def getTagsTrend(start, end, top_n=10, sortby="slope"):
    total_days = (end - start).days + 1
    buckets=2
    bin_days = total_days / buckets

    bin_expr = cast(
        (func.julianday(Post.timestamp) - func.julianday(start)) / bin_days,
        Integer
    ).label("bucket")

    rows = (
        session.query(
            Tag.name.label("tag"),
            bin_expr,
            func.count(Post.id).label("count")
        )
        .join(Post.tags)
        .filter(Post.timestamp >= start, Post.timestamp <= end)
        .group_by(Tag.name, bin_expr)
        .order_by(Tag.name, bin_expr)
        .having(func.count(Post.id) >= 20)
        .all()
    )

    tag_buckets = {}
    for tag, bucket, count in rows:
        tag_buckets.setdefault(tag, {})[bucket] = count

    results = []
    for tag, counts in tag_buckets.items():
        xs = np.arange(buckets)
        ys = np.array([counts.get(b, 0) for b in xs])

        if ys.sum() == 0:
            continue

        # Pente avec régression linéaire
        slope, _ = np.polyfit(xs, ys, 1)

        # Variation en pourcentage
        first_val = ys[0]
        last_val = ys[-1]
        if first_val == 0 and last_val == 0:
            pct_change = 0.0
        elif first_val == 0:
            pct_change = np.float64(100)  
        else:
            pct_change = ((last_val - first_val) / first_val) * 100


        results.append({
            "tag": tag,
            "slope": slope.item(),
            "pct_change": pct_change,
            "total": int(ys.sum()),
            "first_bucket": int(first_val),
            "last_bucket": int(last_val)
        })

    # Top croissance
    top_up = sorted(results, key=lambda x: x[sortby], reverse=True)[:top_n]

    # Top baisse
    top_down = sorted(results, key=lambda x: x[sortby])[:top_n]

    return {"up": top_up, "down": top_down}


def getAllUsers(minPost=5):

    users = (
        session.query(User)
        .join(Post, User.id == Post.user_id)
        .group_by(User.id)
        .having(func.count(Post.id) >= minPost)
        .order_by(desc(User.maxPostperDay))
        .all()
    )

    return [u.name for u in users]

def getUserBotScore(username):

    user = session.query(User).filter(User.name == username).first()
    if not user:
        return None

    # Nombre de posts total
    posts_count = session.query(func.count(Post.id)).filter(Post.user_id == user.id).scalar()

    # Top 10 tags les plus utilisés par le user
    top_tags = (
        session.query(Tag.name, func.count(Post.id).label("count"))
        .join(post_tag_association, Tag.name == post_tag_association.c.tag_id)
        .join(Post, Post.id == post_tag_association.c.post_id)
        .filter(Post.user_id == user.id)
        .group_by(Tag.name)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    # Top 5 catégories les plus utilisées par le user
    top_categories = (
        session.query(Post.category, func.count(Post.id).label("count"))
        .filter(Post.user_id == user.id)
        .group_by(Post.category)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    #last posts
    last_posts = (
        session.query(Post)
        .options(joinedload(Post.tags))
        .filter(Post.user_id == user.id)
        .order_by(Post.timestamp.desc())
        .limit(5)
        .all()
    )


    # Format résultat
    result = {
        "user": user.json,
        "posts_count": posts_count,
        "top_tags": [{"tag": name, "count": count} for name, count in top_tags],
        "top_categories": [{"category": cat, "count": count} for cat, count in top_categories],
        "last_posts": [
            {
                "title": post.title,
                "type": post.type,
                "category": post.category,
                "timestamp": post.timestamp,
                "tags": [tag.name for tag in post.tags],
            }
            for post in last_posts
        ],
    }

    return result