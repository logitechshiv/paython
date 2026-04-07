from flask import Flask, render_template, request, redirect, url_for
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        print(name, email, message)
        return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "").lower()
    per_page = 10

    url = "https://jsonplaceholder.typicode.com/posts"
    posts = requests.get(url).json()

    # 🔍 Search filter
    if query:
        posts = [
            post for post in posts
            if query in post["title"].lower() or query in post["body"].lower()
        ]

    start = (page - 1) * per_page
    end = start + per_page

    paginated_posts = posts[start:end]

    total_pages = len(posts) // per_page

    return render_template(
        "index.html",
        posts=paginated_posts,
        page=page,
        total_pages=total_pages,
        query=query
    )

@app.route("/post/<int:id>")
def post_detail(id):
    url = f"https://jsonplaceholder.typicode.com/posts/{id}"
    post = requests.get(url).json()

    # 🤖 AI Summary
    prompt = f"""
    Summarize this blog post in 2-3 simple sentences:

    Title: {post['title']}
    Content: {post['body']}
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    summary = response.output[0].content[0].text
    return render_template("post_detail.html", post=post, summary=summary)

if __name__ == "__main__":
    app.run(debug=True)