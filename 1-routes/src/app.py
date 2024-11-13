from flask import Flask
import json
from flask import request

app = Flask(__name__)

post_id_counter = 2
comment_id_counter = 1

posts = {
    0: {
        "id": 0,
        "upvotes": 1,
        "title": "My cat is the cutest!",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98",
    },
    1: {
        "id": 1,
        "upvotes": 3,
        "title": "Cat loaf",
        "link": "https://i.imgur.com/TJ46wX4.jpg",
        "username": "alicia98",
    },
}

# keys are post_id for comment's post
comments = {
    0: {
        0: {
            "id": 0,
            "upvotes": 8,
            "text": "Wow, my first Reddit gold!",
            "username": "alicia98",
        }
    },
    1: {},
}


@app.route("/")
def hello():
    return "Hello World!"


@app.errorhandler(404)
def invalid_url(e):
    """
    Checks if URL is valid.
    """
    return json.dumps({"error": "URL is invalid"}), 400


@app.route("/api/posts/")
def get_posts():
    """
    Returns all posts.
    """
    res = {"posts": list(posts.values())}
    return json.dumps(res), 200


@app.route("/api/posts/", methods=["POST"])
def create_post():
    """
    Creates a new post.
    """
    global post_id_counter
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if not title:
        return json.dumps({"error": "User did not supply title"}), 400
    if not link:
        return json.dumps({"error": "User did not supply link"}), 400
    if not username:
        return json.dumps({"error": "User did not supply username"}), 400
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username,
    }
    posts[post_id_counter] = post
    comments[post_id_counter] = {}
    post_id_counter += 1
    return json.dumps(post), 201


@app.route("/api/posts/<int:post_id>/")
def get_post(post_id):
    """
    Returns post given its id.
    """
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    """
    Deletes post given its ID.
    """
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    del comments[post_id]
    return json.dumps(post), 200


@app.route("/api/posts/<int:post_id>/comments/")
def get_comments(post_id):
    """
    Returns the comments for a post given its ID.
    """
    res = comments.get(post_id)
    if res is None:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps({"comments": list(res.values())}), 200


@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    """
    Creates a new comment for a post given its ID.
    """
    global comment_id_counter
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    if not text:
        return json.dumps({"error": "User did not supply text"}), 400
    if not username:
        return json.dumps({"error": "User did not supply username"}), 400
    comment = {
        "id": comment_id_counter,
        "upvotes": 1,
        "text": text,
        "username": username,
    }
    dct = comments.get(post_id)
    if dct is None:
        return json.dumps({"error": "Post not found"}), 404
    dct[comment_id_counter] = comment
    comment_id_counter += 1
    return json.dumps(comment), 201


@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"])
def edit_comment(post_id, comment_id):
    """
    Updates specified comment given post and comment IDs.
    """
    cmts = comments.get(post_id)
    if cmts is None:
        return json.dumps({"error": "Post not found"}), 404
    comment = cmts.get(comment_id)
    if not comment:
        return json.dumps({"error": "Comment not found"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    if not text:
        return json.dumps({"error": "User did not supply text"}), 400
    comment["text"] = text
    return json.dumps(comment), 200


# OPTIONAL CHALLENGES
# TASK 1


@app.route("/api/extra/posts/", methods=["POST"])
def create_post_extra():
    """
    Creates a new post while checking preconditions.
    """
    global post_id_counter
    body = json.loads(request.data)
    title = body.get("title")
    link = body.get("link")
    username = body.get("username")
    if not title:
        return json.dumps({"error": "User did not supply title"}), 400
    if not link:
        return json.dumps({"error": "User did not supply link"}), 400
    if not username:
        return json.dumps({"error": "User did not supply username"}), 400
    if not isinstance(title, str):
        return json.dumps({"error": "Title must be a string"}), 400
    if not isinstance(link, str):
        return json.dumps({"error": "Link must be a string"}), 400
    if not isinstance(username, str):
        return json.dumps({"error": "Username must be a string"}), 400
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username,
    }
    posts[post_id_counter] = post
    comments[post_id_counter] = {}
    post_id_counter += 1
    return json.dumps(post), 201


@app.route("/api/extra/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment_extra(post_id):
    """
    Creates a new comment for a post given its ID while checking preconditions.
    """
    global comment_id_counter
    body = json.loads(request.data)
    text = body.get("text")
    username = body.get("username")
    if not text:
        return json.dumps({"error": "User did not supply text"}), 400
    if not username:
        return json.dumps({"error": "User did not supply username"}), 400
    if not isinstance(text, str):
        return json.dumps({"error": "Text must be a string"}), 400
    if not isinstance(username, str):
        return json.dumps({"error": "Username must be a string"}), 400
    comment = {
        "id": comment_id_counter,
        "upvotes": 1,
        "text": text,
        "username": username,
    }
    dct = comments.get(post_id)
    if dct is None:
        return json.dumps({"error": "Post not found"}), 404
    dct[comment_id_counter] = comment
    comment_id_counter += 1
    return json.dumps(comment), 201


@app.route(
    "/api/extra/posts/<int:post_id>/comments/<int:comment_id>/", methods=["POST"]
)
def edit_comment_extra(post_id, comment_id):
    """
    Updates specified comment given post and comment IDs while checking preconditions.
    """
    cmts = comments.get(post_id)
    if cmts is None:
        return json.dumps({"error": "Post not found"}), 404
    comment = cmts.get(comment_id)
    if not comment:
        return json.dumps({"error": "Comment not found"}), 404
    body = json.loads(request.data)
    text = body.get("text")
    if not text:
        return json.dumps({"error": "User did not supply text"}), 400
    if not isinstance(text, str):
        return json.dumps({"error": "Text must be a string"}), 400
    comment["text"] = text
    return json.dumps(comment), 200


# TASK 2


@app.route("/api/extra/posts/<int:post_id>/", methods=["POST"])
def increment_upvotes(post_id):
    """
    Increments the upvotes for a post given its ID either by one or the given amount.
    """
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    if not request.data:
        post["upvotes"] += 1
    else:
        body = json.loads(request.data)
        amt = body.get("upvotes")
        if not isinstance(amt, int):
            return json.dumps({"error": "Upvotes must be an integer"}), 400
        post["upvotes"] += amt
    return json.dumps(post), 200


@app.route("/api/extra/posts/")
def get_posts_sorted():
    """
    Returns all posts and, if sort parameter is provided, sorts them based on upvotes.
    """
    sort_order = request.args.get("sort")
    if not sort_order:
        return get_posts()
    else:
        lst = list(posts.values())
        if sort_order == "increasing":
            lst.sort(key=lambda post: post["upvotes"])
        else:
            lst.sort(key=lambda post: post["upvotes"], reverse=True)
        return json.dumps({"posts": lst}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
