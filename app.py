from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
)
import os
import re
import openai
import function
from functools import wraps
import os
import video as vid
from flask_session import Session
import requests  # Ensure you have this import at the top of your file
from flask import jsonify
import images

# Initialize Flask app
app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"  # or 'redis', 'sqlalchemy', etc.
Session(app)
app.secret_key = "supersecretkey"

# Configure OpenAI
openai.api_key = "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"

with open(os.path.join("topic_prompts", "chef_directive.txt"), "r") as f:
    chef_directive = f.read()


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        return redirect(url_for("home"))
    return render_template("login.html")


with open(os.path.join("topic_prompts", "chef_directive.txt"), "r") as f:
    chef_directive = f.read()


# # Function to extract ingredients from the assistant's response
# def extract_ingredients_from_response(response_text):
#     ingredients = []
#     match = re.search(r":\s*(.+)", response_text)
#     if match:
#         items = match.group(1)
#         ingredients = [item.strip(" .") for item in items.split(",")]
#     else:
#         ingredients = [response_text.strip(" .")]

#     return ingredients


@app.route("/")
@login_required
def index():
    return redirect(url_for("home"))


@app.route("/home")
@login_required
def home():
    return render_template("hero.html", username=session.get("username"))


@app.route("/dashboard")
@login_required
def dashboard():
    test = session.get("ingredients")
    print(test)
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/segments")
@login_required
def segments():
    embed_url = session.get("embedUrl")
    transcript = session.get("transcript")
    recipe_format = session.get("recipe_format")

    return render_template(
        "segments.html",
        embed_url=embed_url,
        transcript=transcript,
        recipe_format=recipe_format,
    )  # Pass it to the template


@login_required
@app.route("/recipe_transcript", methods=["POST"])  # type: ignore
def recipe_transcript():
    # Get the transcript from the session
    # Get the transcript from the session
    transcript = session.get("transcript")
    print("hello")
    model = "gpt-4-turbo"
    prompt = "There are no recipe's in this video"
    if transcript is not None:
        # Construct the prompt for ChatGPT
        transcript_array = transcript  # Use the transcript variable from the session
        prompt = (
            "Hello ChatGPT, I want you to create a step by step concise recipe using the following array that represents the transcript of a YouTube video. "
            "The first column represents the time of the video in seconds and the second column represents what is said at that time in the YouTube video. "
            "Make sure for each step you include a timestamp of when that step took place in the transcript. "
            "The following array is: "
            + str(transcript_array)  # Convert to string for the prompt
        )
    # Make an API call to GPT-4 Turbo
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful chef ai called PlatePal assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
    )
    # Extract and print the response
    gpt_response = response.choices[0].message.content
    print("GPT-4 Turbo response:", gpt_response)


@app.route("/store_recipe", methods=["POST"])
@login_required
def store_recipe():
    recipe = request.form.get("recipe")
    vid_info = vid.get_info(recipe)
    session["embedUrl"] = vid_info[0][0]  # type: ignore
    session["transcript"] = vid_info[1]  # type: ignore
    session["recipevideo"] = recipe  # Store the recipe in the session

    # Construct the full URL for the /recipe_transcript endpoint
    recipe_transcript_url = request.url_root + "recipe_transcript"

    # Now make a POST request to the /recipe_transcript endpoint
    transcript = session.get("transcript")
    model = "gpt-4-turbo"
    prompt = "There are no recipe's in this video"
    if transcript is not None:
        # Construct the prompt for ChatGPT
        transcript_array = transcript  # Use the transcript variable from the session
        prompt = (
            "Hello ChatGPT, I want you to create a step by step concise recipe using the following array that represents the transcript of a YouTube video. "
            "The first column represents the time of the video in seconds and the second column represents what is said at that time in the YouTube video. "
            "Make sure for each step you include a timestamp of when that step took place in the transcript and make the timestamps in minutes and seconds format not seconds. "
            "Include a prep, cook, and total time along with serving size if available after the recipe name. "
            "Please respond to the following question using markdown formatting. Include:"
            "A level-1 header (`#`) for the recipe name."
            "A level-3 header (`###`) for prep, cook, total and serving size."
            "A level-2 header (`##`) for sub-sections"
            "The following array is: "
            + str(transcript_array)  # Convert to string for the prompt
        )
    # Make an API call to GPT-4 Turbo
    response = openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful chef ai assistant called PlatePal .",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
        n=1,
        stop=None,
    )
    # Extract and print the response
    gpt_response = response.choices[0].message.content
    with open("transcript_log.txt", "a") as file:  # Open in append mode
        file.write("---------------------------------------------------------------------------------" + "\n" + gpt_response + "\n")  # type: ignore

    latest_recipe = ""
    with open("transcript_log.txt", "r") as file:
        lines = file.readlines()
        print(lines)
        # Find the last recipe before the dashed line
        for line in reversed(lines):
            if (
                line.strip()
                == "---------------------------------------------------------------------------------"
            ):
                break
            latest_recipe = line.strip() + "\n" + latest_recipe  # Concatenate lines
            print(latest_recipe)
    with open("transcript_format.txt", "w") as file:
        file.write(latest_recipe + "\n")
    with open("transcript_format.txt", "r") as recipes:  # Open in append mode
        # Convert lines starting with "###" to <h3> tags
        formatted_recipe = ""
        recipe = recipes.readlines()
        counter = 0
        for line in recipe:
            line = line.replace("**", "<em>")
            if line.startswith("###"):
                counter += 1
                if counter == 1:
                    title = line[4:].strip()
            if line.startswith("### Prep Time:"):
                formatted_recipe += f'<div class = "time2-container"><h4 class = "time2-slot">🍱 {line[4:].strip()}</h4>'
            elif line.startswith("### Cook Time:"):
                formatted_recipe += (
                    f'<h4 class = "time2-slot">👩🏾‍🍳 {line[4:].strip()}</h4>'
                )
            elif line.startswith("### Total Time:"):
                formatted_recipe += (
                    f'<h4 class = "time2-slot">⏰ {line[4:].strip()}</h4>'
                )
            elif line.startswith("### Serving"):
                formatted_recipe += (
                    f'<h4 class = "time2-slot">🍽️ {line[4:].strip()}</h4></div>'
                )
            elif line.startswith("####"):
                formatted_recipe += (
                    f"<h4>{line[4:].strip()}</h4>"  # Remove "###" and wrap in <h3>
                )
            elif line.startswith("###"):
                formatted_recipe += (
                    f"<h3>{line[4:].strip()}</h3>"  # Remove "###" and wrap in <h3>
                )
            elif line.startswith("##"):
                formatted_recipe += (
                    f"<h2>{line[3:].strip()}</h2>"  # Remove "###" and wrap in <h3>
                )
            elif line.startswith("#"):
                formatted_recipe += (
                    f'<h2 class = "recipe2-header">{line[1:].strip()}</h2>'
                )
            elif line.startswith("-"):
                formatted_recipe += f"<ul><li>{line[1:].strip()}</li></ul>"
            else:
                formatted_recipe += f"<p>{line.strip()}</p>"  # Wrap other lines in <p>
        print(formatted_recipe)
        session["recipe_format"] = formatted_recipe

        recipe_ingredient_image = images.scrape_first_google_image(title + "dish")  # type: ignore
    print("GPT-4 Turbo response:", gpt_response)

    return redirect(url_for("segments"))  # Redirect back to the segments page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirmPassword"]
        if password == confirm_password:
            mydb = function.connect_to_database()
            create = function.create_account(mydb, username, password, email)
            function.close_connection(mydb)
            flash("Account Created Successfully")
            return redirect(url_for("login"))
        else:
            flash("Passwords do not match")
            return redirect(url_for("register"))
    return render_template("register.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    # Read the latest recipe from recipe_format.txt
    latest_recipe = ""
    try:
        with open("recipe_log.txt", "r") as file:
            lines = file.readlines()
            print(lines)
            # Find the last recipe before the dashed line
            for line in reversed(lines):
                if (
                    line.strip()
                    == "---------------------------------------------------------------------------------"
                ):
                    break
                latest_recipe = line.strip() + "\n" + latest_recipe  # Concatenate lines
        with open("recipe_format.txt", "w") as file:
            file.write(latest_recipe + "\n")
            print(latest_recipe)
        with open("recipe_format.txt", "r") as recipes:  # Open in append mode
            # Convert lines starting with "###" to <h3> tags
            formatted_recipe = ""
            recipe = recipes.readlines()
            counter = 0
            for line in recipe:
                line = line.replace("**", "<em>")
                if line.startswith("###"):
                    counter += 1
                if counter >= 1:
                    if line.startswith("#### Prep Time:"):
                        formatted_recipe += f'<div class = "time-container"><h4 class = "time-slot">🍱 {line[4:].strip()}</h4>'
                    elif line.startswith("#### Cook Time:"):
                        formatted_recipe += (
                            f'<h4 class = "time-slot">👩🏾‍🍳 {line[4:].strip()}</h4>'
                        )
                    elif line.startswith("#### Chill Time:"):
                        formatted_recipe += (
                            f'<h4 class = "time-slot">❄️ {line[4:].strip()}</h4>'
                        )
                    elif line.startswith("#### Total Time:"):
                        formatted_recipe += (
                            f'<h4 class = "time-slot">⏰ {line[4:].strip()}</h4></div>'
                        )
                        break
                    elif line.startswith("####"):
                        formatted_recipe += f"<h4>{line[4:].strip()}</h4>"  # Remove "###" and wrap in <h3>
                    elif line.startswith("###") and counter == 1:
                        formatted_recipe += (
                            f'<h2 class = "recipe-header">{line[4:].strip()}</h2>'
                        )
                        title = line[4:].strip()
                    elif line.startswith("###"):
                        formatted_recipe += f"<h3>{line[4:].strip()}</h3>"  # Remove "###" and wrap in <h3>
                    elif line.startswith("-"):
                        formatted_recipe += f"<ul><li>{line[1:].strip()}</li></ul>"
                    else:
                        formatted_recipe += (
                            f"<p>{line.strip()}</p>"  # Wrap other lines in <p>
                        )
            recipe_ingredient_image = images.scrape_first_google_image(title + "dish")  # type: ignore
    except FileNotFoundError:
        formatted_recipe = "<p>No recipes found.</p>"

    missing_ingredients = []
    if request.method == "POST":
        # Fetch missing ingredients
        missing_ingredients = extract_missing_ingredients("recipe_format.txt")
        product_info = []
        for ingredient in missing_ingredients:
            result = scrape_amazon(ingredient)
            if result:
                product_info.append(result)

        missing_ingredients = product_info

    return render_template(
        "account.html",
        latest_recipe=formatted_recipe,
        image=recipe_ingredient_image,  # type: ignore
        missing_ingredients=missing_ingredients,
    )


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


from ingredientGrab import extract_missing_ingredients
from product_listing_pull import scrape_amazon


@app.route("/fetch_missing_ingredients", methods=["GET"])
@login_required
def fetch_missing_ingredients():
    # Step 1: Extract missing ingredients from the recipe_format.txt
    missing_ingredients = extract_missing_ingredients("recipe_format.txt")

    # Step 2: Gather product information for each missing ingredient
    product_info = []
    for ingredient in missing_ingredients:
        result = scrape_amazon(ingredient)
        if result:
            product_info.append(result)

    # Step 3: Return the product information as JSON
    return jsonify(product_info)


@app.route("/ingredients")
@login_required
def ingredients():
    return render_template("ingredients.html")


@app.route("/store_ingredients", methods=["POST"])
@login_required
def store_ingredients():
    data = request.json
    ingredients = data.get("ingredients", [])  # type: ignore

    if ingredients:
        session["ingredient_growth"] = ingredients  # Store ingredients in session
        return jsonify({"message": "Ingredients stored successfully."}), 200
    else:
        return jsonify({"error": "No ingredients provided."}), 400


@app.route("/process_image", methods=["POST"])
@login_required
def process_image():
    print("Processing image...")
    try:
        data = request.get_json()
        if not data or "image_data" not in data:
            return jsonify({"error": "No image data provided"}), 400

        # Get the base64 image data
        image_data = data["image_data"]
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]

        # Process with OpenAI
        image_url = f"data:image/jpeg;base64,{image_data}"

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What ingredients do you see in this image? Please list them in a comma-separated format.",
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        response = openai.chat.completions.create(
            model="gpt-4-turbo", messages=messages, max_tokens=300  # type: ignore
        )

        ingredients = response.choices[0].message.content.strip()  # type: ignore
        session["ingredients"] = ingredients
        print("Detected ingredients:", ingredients)

        return jsonify({"ingredients": ingredients.split(",")})

    except Exception as e:
        print("Error processing image:", str(e))
        return jsonify({"error": str(e)}), 500


# Chat route - handles the conversation with the LLM
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]  # type: ignore
    ingredients = session.get("ingredients")
    print(ingredients)

    if "conversation" not in session:
        session["conversation"] = []

    # Append the user's message to the conversation
    session["conversation"].append({"role": "user", "content": user_message})

    # Construct the system message with the ingredients
    if ingredients is not None:
        print(ingredients)
        system_message = f"The following is the context of what you, the AI Chef Assistant, can see: {ingredients}. For every recipe that you generate I want you to include at the bottom of your response all the ingredients that are in the recipe but weren't provided for you to see. I want you to label this section as 'Ingredients Not Provided in Your List'"

    else:
        system_message = "The user has not provided any ingredients."

    # The messages structure for the API call
    messages = session["conversation"] + [
        {"role": "system", "content": chef_directive},
        {
            "role": "system",
            "content": "You are a helpful assistant that provides cooking suggestions based on available ingredients.",
        },
        {"role": "system", "content": system_message},
    ]

    app.logger.info(f"Messages sent to OpenAI API: {messages}")

    try:
        # Make API call to OpenAI using the messages
        response = openai.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=messages,
            max_tokens=500,
        )
        # Extract the content from the response
        gpt_response = response.choices[0].message.content
        with open("recipe_log.txt", "a") as file:  # Open in append mode
            file.write(
                "---------------------------------------------------------------------------------"
                + "\n"
                + gpt_response  # type: ignore
                + "\n"
            )

        # Append the GPT response to the conversation history
        session["conversation"].append({"role": "assistant", "content": gpt_response})

        # Return the GPT response
        return jsonify({"response": gpt_response})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5001)
