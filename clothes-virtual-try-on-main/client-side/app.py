from flask import Flask, request, render_template
from PIL import Image
from io import BytesIO
import base64
import os

# Import your local pipeline functions
from run import try_on_model

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template("index.html")


@app.route("/preds", methods=['POST'])
def submit():
    cloth_file = request.files['cloth']
    model_file = request.files['model']

    # Save uploaded files
    cloth_path = os.path.join(UPLOAD_FOLDER, "cloth.jpg")
    model_path = os.path.join(UPLOAD_FOLDER, "model.jpg")
    output_path = os.path.join(UPLOAD_FOLDER, "output.png")

    cloth_file.save(cloth_path)
    model_file.save(model_path)

    # Call your local try-on function
    try_on_model(model_path, cloth_path, output_path)  # <- implement this in run.py

    # Load the output image and convert to base64
    with open(output_path, "rb") as f:
        encoded_img = base64.b64encode(f.read()).decode("utf-8")

    return render_template('index.html', op=encoded_img)


if __name__ == '__main__':
    app.run(debug=True)
