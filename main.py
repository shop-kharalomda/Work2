from flask import Flask, request, send_file, jsonify
import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def is_whatsapp_number(phone):
    time.sleep(0.05)  # محاكاة زمن الشبكة، يمكنك تقليله
    return phone.strip().endswith("5")  # مثال بسيط فقط

@app.route("/")
def home():
    return send_file("index.html")

@app.route("/check", methods=["POST"])
def check_numbers():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    ext = filename.split(".")[-1].lower()
    if ext == "txt":
        with open(path, "r", encoding="utf-8") as f:
            numbers = [line.strip() for line in f.readlines()]
    elif ext == "csv":
        df = pd.read_csv(path)
        numbers = df.iloc[:, 0].astype(str).tolist()
    elif ext == "xlsx":
        df = pd.read_excel(path)
        numbers = df.iloc[:, 0].astype(str).tolist()
    else:
        return "صيغة غير مدعومة", 400

    valid = []
    invalid = []

    for num in numbers:
        if is_whatsapp_number(num):
            valid.append(num)
        else:
            invalid.append(num)

    def save_outputs(data, name):
        txt_path = os.path.join(RESULT_FOLDER, f"{name}.txt")
        csv_path = os.path.join(RESULT_FOLDER, f"{name}.csv")
        xlsx_path = os.path.join(RESULT_FOLDER, f"{name}.xlsx")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(data))
        pd.DataFrame(data).to_csv(csv_path, index=False, header=False)
        pd.DataFrame(data).to_excel(xlsx_path, index=False, header=False)

        return {
            "txt": "/" + txt_path,
            "csv": "/" + csv_path,
            "xlsx": "/" + xlsx_path,
        }

    valid_links = save_outputs(valid, "valid")
    invalid_links = save_outputs(invalid, "invalid")

    return jsonify({
        "valid_txt": valid_links["txt"],
        "valid_csv": valid_links["csv"],
        "valid_xlsx": valid_links["xlsx"],
        "invalid_txt": invalid_links["txt"],
        "invalid_csv": invalid_links["csv"],
        "invalid_xlsx": invalid_links["xlsx"],
    })

@app.route("/results/<filename>")
def download_result(filename):
    return send_file(os.path.join(RESULT_FOLDER, filename), as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)