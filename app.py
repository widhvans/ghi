from flask import Flask, request, send_file
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import io
import requests
import time
import threading
import os

app = Flask(__name__)

def load_model():
    model_id = "runwayml/stable-diffusion-v1-5"  # Lightweight model
    dtype = torch.float32  # CPU only for Render free tier
    print("Model ko load kar raha hoon...")
    retries = 5
    for attempt in range(retries):
        try:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_id,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                safety_checker=None,
                cache_dir="/tmp/model_cache"  # Cache for faster reload
            )
            pipe.to("cpu")
            pipe.enable_attention_slicing()
            print("Model load ho gaya!")
            return pipe
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                raise Exception("Model loading failed after retries")

pipe = load_model()

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

def generate_ghibli_image(image, pipe, strength):
    image = image.convert("RGB")
    image = image.resize((512, 512))
    prompt = "Ghibli-style anime painting, soft pastel colors, highly detailed, masterpiece"
    print("Image generate kar raha hoon...")
    start_time = time.time()
    result = pipe(prompt=prompt, image=image, strength=strength, num_inference_steps=10).images[0]
    print(f"Image {time.time() - start_time:.2f} seconds mein generate hui!")
    return result

@app.route('/generate', methods=['GET', 'POST'])
def generate_image():
    strength = float(request.args.get('strength', 0.6) if request.method == 'GET' else request.form.get('strength', 0.6))

    if request.method == 'GET':
        image_url = request.args.get('imageUrl')
        if not image_url:
            return "Image URL nahi diya!", 400
        for _ in range(3):
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    break
            except Exception as e:
                print(f"Image download failed: {e}. Retrying...")
                time.sleep(5)
        else:
            return "Image URL se download nahi hua!", 400

    elif request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            image = Image.open(file.stream)
        elif 'image_url' in request.form and request.form['image_url']:
            url = request.form['image_url']
            for _ in range(3):
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        image = Image.open(io.BytesIO(response.content))
                        break
                except Exception as e:
                    print(f"Image download failed: {e}. Retrying...")
                    time.sleep(5)
            else:
                return "Image URL se download nahi hua!", 400
        else:
            return "Koi file ya URL nahi diya!", 400

    try:
        result_img = generate_ghibli_image(image, pipe, strength)
        output = io.BytesIO()
        result_img.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name='ghibli_image.png')
    except Exception as e:
        print(f"Generation failed: {e}")
        return "Internal error, retrying...", 500

def keep_alive():
    while True:
        print("Keeping alive...")
        time.sleep(60)

if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    port = int(os.environ.get("PORT", 8080))  # Render PORT env use karega
    app.run(host='0.0.0.0', port=port)

