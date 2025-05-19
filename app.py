from flask import Flask, render_template, request, redirect, url_for, session
import openai
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

openai.api_key = os.getenv("OPENAI_API_KEY")

USERNAME = "econ708"
PASSWORD = "managerial"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    response = ""
    if request.method == "POST":
        user_input = request.form["prompt"]
        action = request.form["action"]
        module = request.form["module"]
        with open(f"course_content/{module}", "r") as f:
            module_content = f.read()

        if action == "explain":
            system_prompt = f"You are an MBA economics tutor. Explain the following concept clearly using the context of this module:\n\n{module_content}"
        elif action == "quiz":
            system_prompt = f"You are an MBA economics tutor. Create a 3-question multiple choice quiz with answers based on the following module:\n\n{module_content}"
        elif action == "example":
            system_prompt = f"You are an MBA economics tutor. Show a step-by-step example problem with a solution using the following module:\n\n{module_content}"
        else:
            system_prompt = f"You are an MBA economics tutor. Use this context:\n\n{module_content}"

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        response = completion.choices[0].message.content

    module_files = os.listdir("course_content")
    return render_template("chat.html", response=response, modules=module_files)

@app.route("/logout")
def logout():
    session["logged_in"] = False
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
