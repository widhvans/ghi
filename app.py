from flask import Flask, request, send_file
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import io
import requests
import time

app = Flask(__name__)

def load_model():
    model_id = "nitrosocke/Ghibli-Diffusion"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    print("Model ko load kar raha hoon...")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    pipe.enable_attention_slicing()
    print("Model load ho gaya!")
    return pipe

def generate_ghibli_image(image, pipe, strength):
    image = image.convert("RGB")
    image = image.resize((512, 512))
    prompt = "Ghibli-style anime painting, soft pastel colors, highly detailed, masterpiece"
    print("Image generate kar raha hoon...")
    start_time = time.time()
    result = pipe(prompt=prompt, image=image, strength=strength).images[0]
    print(f"Image {time.time() - start_time:.2f} seconds mein generate hui!")
    return result

pipe = load_model()

@app.route('/generate', methods=['GET', 'POST'])
def generate_image():
    strength = float(request.args.get('strength', 0.6) if request.method == 'GET' else request.form.get('strength', 0.6))

    if request.method == 'GET':
        image_url = request.args.get('imageUrl')
        if not image_url:
            return "Image URL nahi diya!", 400
        response = requests.get(image_url)
        if response.status_code != 200:
            return "Image URL se download nahi hua!", 400
        image = Image.open(io.BytesIO(response.content))

    elif request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            image = Image.open(file.stream)
        elif 'image_url' in request.form and request.form['image_url']:
            url = request.form['image_url']
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
            else:
                return "Image URL se download nahi hua!", 400
        else:
            return "Koi file ya URL nahi diya!", 400

    result_img = generate_ghibli_image(image, pipe, strength)
    output = io.BytesIO()
    result_img.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype='image/png', as_attachment=True, download_name='ghibli_image.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
