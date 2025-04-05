from flask import Flask, request, send_file
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import io
import time

app = Flask(__name__)

# Model ko load karne ka function
def load_model():
    model_id = "nitrosocke/Ghibli-Diffusion"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    print("Model ko load kar raha hoon...")
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipe.to("cuda" if torch.cuda.is_available() else "cpu")
    pipe.enable_attention_slicing()
    print("Model load ho gaya!")
    return pipe

# Ghibli-style image generate karne ka function
def generate_ghibli_image(image, pipe, strength):
    image = image.convert("RGB")
    image = image.resize((512, 512))
    prompt = "Ghibli-style anime painting, soft pastel colors, highly detailed, masterpiece"
    print("Image generate kar raha hoon...")
    start_time = time.time()
    result = pipe(prompt=prompt, image=image, strength=strength).images[0]
    print(f"Image {time.time() - start_time:.2f} seconds mein generate hui!")
    return result

# Model ko globally load karo
pipe = load_model()

# API endpoint banayein
@app.route('/generate', methods=['POST'])
def generate_image():
    if 'file' not in request.files:
        return "Koi file upload nahi ki gayi!", 400
    
    file = request.files['file']
    strength = float(request.form.get('strength', 0.6))  # Default strength 0.6
    
    # File ko image mein convert karo
    image = Image.open(file.stream)
    
    # Ghibli image generate karo
    result_img = generate_ghibli_image(image, pipe, strength)
    
    # Result ko save karo aur bhejo
    output = io.BytesIO()
    result_img.save(output, format="PNG")
    output.seek(0)
    
    return send_file(output, mimetype='image/png', as_attachment=True, download_name='ghibli_image.png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
