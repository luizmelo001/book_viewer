from flask import Flask, render_template, g, redirect, request, url_for  

app = Flask(__name__)

# ==================== Before Request ====================
@app.before_request
def load_contents():
    """This runs before EVERY request"""
    with open("book_viewer/data/toc.txt", "r") as file:
        g.contents = file.readlines()

@app.route("/search")
def search():
    query = request.args.get("query","")
    results = chapters_matching(query) if query else []
    return render_template("search.html", query=query, results=results, contents=g.contents)

# ==================== Main Page ====================
@app.route("/")
def index():
    return render_template('home.html', contents=g.contents)

# ==================== Chapters Display ====================
@app.route("/chapters/<page_num>")
def chapter(page_num):
    with open("book_viewer/data/toc.txt", "r") as f:
        contents = f.readlines()

    # Chapter Name (e.g: "A Scandal in Bohemia")
    chapter_name = g.contents[int(page_num) - 1].strip()

    # Complete Chapter Title (e.g: "Chapter 1: A Scandal in Bohemia")
    chapter_title = f"Chapter {page_num}: {chapter_name}"

    with open(f"book_viewer/data/chp{page_num}.txt", "r") as f:   # ← Correct chapter number in the filename
        chapter = f.read()

    return render_template("chapter.html",
                           chapter_title=chapter_title,
                           contents=g.contents,
                           chapter=chapter)

# === Template Filter ===
@app.template_filter("in_paragraphs")
def in_paragraphs(text):
    """Wrap each non-empty line in <p> tags"""
    if not text:
        return ""
    lines = text.strip().split("\n\n")
    paragraphs = [f"<p>{line.strip()}</p>" for line in lines if line.strip()]
    return "".join(paragraphs)    

@app.template_filter("highlight")
def highlight(text, term):
    if not text or not term:
        return text or ""
    
    # Case-insensitive replace mantendo o texto original
    import re
    pattern = re.compile(re.escape(term), re.IGNORECASE)
    return pattern.sub(lambda m: f"<strong>{m.group(0)}</strong>", text)

# === Search Functionality ===
def chapters_matching(query):
    """Return a list of chapters that match the search query"""
    query = query.lower()
    results = []

    if not query:
        return []
    
    for idx, chapter in enumerate(g.contents, start=1):
        with open(f"book_viewer/data/chp{idx}.txt", "r") as f:
            chapter_content = f.read()

        matches = {}
        for p_index, paragraph in enumerate(chapter_content.split("\n\n"), start=1):
            if query.lower() in paragraph.lower():
                matches[p_index] = paragraph.strip()
        if matches:
            results.append({
                "number": idx,
                "chapter_num": idx,
                "chapter_name": chapter.strip(),
                "paragraphs": matches
            })
    return results

# === Error Handler ===
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5003)