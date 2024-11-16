from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def message_to_binary(message):
    return ''.join([format(ord(char), "08b") for char in message])

def binary_to_message(binary_data):
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join([chr(int(byte, 2)) for byte in all_bytes])

def encode_image(image_path, secret_message, output_path):
    image = cv2.imread(image_path)
    binary_message = message_to_binary(secret_message) + '1111111111111110'
    binary_index = 0

    for row in range(image.shape[0]):
        for col in range(image.shape[1]):
            for channel in range(image.shape[2]):
                if binary_index < len(binary_message):
                    image[row, col, channel] = int(bin(image[row, col, channel])[2:-1] + binary_message[binary_index], 2)
                    binary_index += 1
                else:
                    break

    cv2.imwrite(output_path, image)

def decode_image(image_path):
    image = cv2.imread(image_path)
    binary_data = ""

    for row in range(image.shape[0]):
        for col in range(image.shape[1]):
            for channel in range(image.shape[2]):
                binary_data += bin(image[row, col, channel])[-1]

        if "1111111111111110" in binary_data:
            binary_data = binary_data[:binary_data.index("1111111111111110")]
            break

    return binary_to_message(binary_data)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/encode", methods=["POST"])
def encode():
    image = request.files["image"]
    message = request.form["message"]
    input_path = os.path.join(UPLOAD_FOLDER, image.filename)
    output_path = os.path.join(OUTPUT_FOLDER, "encoded_" + image.filename)

    image.save(input_path)
    encode_image(input_path, message, output_path)
    return send_file(output_path, as_attachment=True)

@app.route("/decode", methods=["POST"])
def decode():
    image = request.files["image"]
    input_path = os.path.join(UPLOAD_FOLDER, image.filename)

    image.save(input_path)
    hidden_message = decode_image(input_path)
    return f"<h1>Decoded Message:</h1><p>{hidden_message}</p>"

if __name__ == "__main__":
    app.run(debug=True)
