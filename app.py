import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import io
import base64

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_bg_with_rembg(input_path, output_path):
    input_image = Image.open(input_path).convert("RGBA")
    output_image = remove(input_image)
    # Ensure output size matches original
    output_image = output_image.resize(input_image.size, Image.LANCZOS)
    output_image.save(output_path, "PNG")
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session_dir = os.path.join(UPLOAD_FOLDER, f'layers_{session_id}')
        os.makedirs(session_dir, exist_ok=True)
        original_filename = secure_filename(file.filename)
        original_path = os.path.join(session_dir, f'original_{original_filename}')
        file.save(original_path)
        no_bg_filename = f'nobg_{original_filename.rsplit(".", 1)[0]}.png'
        no_bg_path = os.path.join(session_dir, no_bg_filename)
        removed_bg_path = remove_bg_with_rembg(original_path, no_bg_path)
        if removed_bg_path:
            return jsonify({
                'success': True,
                'session_id': session_id,
                'original_image': f'/uploads/layers_{session_id}/original_{original_filename}',
                'no_bg_image': f'/uploads/layers_{session_id}/{no_bg_filename}'
            })
        else:
            return jsonify({'error': 'Failed to remove background'}), 500
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/editor/<session_id>')
def editor(session_id):
    session['session_id'] = session_id
    session_dir = os.path.join(UPLOAD_FOLDER, f'layers_{session_id}')
    if not os.path.exists(session_dir):
        return "Session not found", 404
    files = os.listdir(session_dir)
    original_image = None
    no_bg_image = None
    for file in files:
        if file.startswith('original_'):
            original_image = f'/uploads/layers_{session_id}/{file}'
        elif file.startswith('nobg_'):
            no_bg_image = f'/uploads/layers_{session_id}/{file}'
    return render_template('editor.html', 
                         session_id=session_id,
                         original_image=original_image,
                         no_bg_image=no_bg_image)

@app.route('/save_text', methods=['POST'])
def save_text():
    data = request.get_json()
    text_content = data.get('text', '')
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    session_dir = os.path.join(UPLOAD_FOLDER, f'layers_{session_id}')
    text_file_path = os.path.join(session_dir, 'text_content.txt')
    try:
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_text', methods=['GET'])
def get_text():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    session_dir = os.path.join(UPLOAD_FOLDER, f'layers_{session_id}')
    text_file_path = os.path.join(session_dir, 'text_content.txt')
    try:
        if os.path.exists(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            return jsonify({'text': text_content})
        else:
            return jsonify({'text': ''})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export_image', methods=['POST'])
def export_image():
    session_id = session.get('session_id')
    if not session_id:
        return jsonify({'error': 'No active session'}), 400
    data = request.get_json()
    text_layers = data.get('text_layers', [])
    layer_visibility = data.get('layer_visibility', {})
    canvas_width = int(data.get('canvas_width', 800))
    canvas_height = int(data.get('canvas_height', 500))
    original_width = int(data.get('original_width', canvas_width))
    original_height = int(data.get('original_height', canvas_height))
    canvas_fitted_x = float(data.get('canvas_fitted_x', 0))
    canvas_fitted_y = float(data.get('canvas_fitted_y', 0))
    canvas_fitted_width = float(data.get('canvas_fitted_width', canvas_width))
    canvas_fitted_height = float(data.get('canvas_fitted_height', canvas_height))
    session_dir = os.path.join(UPLOAD_FOLDER, f'layers_{session_id}')
    try:
        files = os.listdir(session_dir)
        original_path = None
        nobg_path = None
        for file in files:
            if file.startswith('original_'):
                original_path = os.path.join(session_dir, file)
            elif file.startswith('nobg_'):
                nobg_path = os.path.join(session_dir, file)
        if not original_path or not nobg_path:
            return jsonify({'error': 'Image files not found'}), 404
        result_image = create_composite_image(
            original_path,
            nobg_path,
            text_layers,
            layer_visibility,
            canvas_width,
            canvas_height,
            original_width,
            original_height,
            canvas_fitted_x,
            canvas_fitted_y,
            canvas_fitted_width,
            canvas_fitted_height
        )
        if result_image:
            export_filename = f'exported_{session_id}.png'
            export_path = os.path.join(session_dir, export_filename)
            result_image.save(export_path, 'PNG')
            return jsonify({
                'success': True,
                'download_url': f'/uploads/layers_{session_id}/{export_filename}'
            })
        else:
            return jsonify({'error': 'Failed to create composite image'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_composite_image(original_path, nobg_path, text_layers, layer_visibility, canvas_width=800, canvas_height=500, original_width=800, original_height=500, canvas_fitted_x=0, canvas_fitted_y=0, canvas_fitted_width=800, canvas_fitted_height=500):
    from PIL import Image, ImageDraw, ImageFont
    import math
    composite = Image.new('RGBA', (original_width, original_height), (0, 0, 0, 255))
    original_img = Image.open(original_path).convert('RGBA')
    nobg_img = Image.open(nobg_path).convert('RGBA')
    def fit_image(img):
        img_aspect = img.width / img.height
        out_aspect = original_width / original_height
        if img_aspect > out_aspect:
            draw_width = original_width
            draw_height = int(original_width / img_aspect)
        else:
            draw_height = original_height
            draw_width = int(original_height * img_aspect)
        x = (original_width - draw_width) // 2
        y = (original_height - draw_height) // 2
        return img.resize((draw_width, draw_height), Image.LANCZOS), x, y, draw_width, draw_height
    # Fit images and get fitted area
    fitted_img, fitted_x, fitted_y, fitted_width, fitted_height = fit_image(original_img)
    if layer_visibility.get('original', True):
        composite.paste(fitted_img, (fitted_x, fitted_y), fitted_img)
    # Draw text layers relative to fitted image area
    if layer_visibility.get('text', False) and text_layers:
        for layer in text_layers:
            scaled_layer = layer.copy()
            # Map (x, y) from canvas fitted area to original fitted area
            rel_x = (float(layer['x']) - canvas_fitted_x) / canvas_fitted_width
            rel_y = (float(layer['y']) - canvas_fitted_y) / canvas_fitted_height
            scaled_layer['x'] = fitted_x + rel_x * fitted_width
            scaled_layer['y'] = fitted_y + rel_y * fitted_height
            # Font size relative to fitted image area
            scale_font = fitted_height / canvas_fitted_height
            scaled_layer['fontSize'] = float(layer['fontSize']) * scale_font
            text_img = create_text_image_advanced(scaled_layer, original_width, original_height)
            if text_img:
                composite = Image.alpha_composite(composite, text_img)
    # No-bg image
    fitted_nobg, nobg_x, nobg_y, nobg_width, nobg_height = fit_image(nobg_img)
    if layer_visibility.get('nobg', False):
        composite.paste(fitted_nobg, (nobg_x, nobg_y), fitted_nobg)
    return composite

def create_text_image_advanced(layer, max_width, max_height):
    try:
        from PIL import Image, ImageDraw, ImageFont
        import math
        text = layer.get('text', '')
        font_size = int(layer.get('fontSize', 24))
        font_family = layer.get('fontFamily', 'Arial')
        color = layer.get('color', 'rgba(0,0,0,1)')
        font_weight = layer.get('fontWeight', 400)
        opacity = float(layer.get('opacity', 1))
        rotation = float(layer.get('rotation', 0))
        x_percent = float(layer.get('x', 50)) / 100.0
        y_percent = float(layer.get('y', 50)) / 100.0
        # Font path logic (simple)
        font_path = 'arial.ttf'
        if 'times' in font_family.lower():
            font_path = 'times.ttf'
        elif 'courier' in font_family.lower():
            font_path = 'cour.ttf'
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
        # Parse color (rgba)
        import re
        m = re.match(r'rgba?\((\d+), ?(\d+), ?(\d+)(?:, ?([\d.]+))?\)', color)
        if m:
            r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
            a = int(float(m.group(4)) * 255) if m.group(4) else 255
        else:
            r, g, b, a = 0, 0, 0, 255
        a = int(a * opacity)
        # Render text to image
        text_img = Image.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = int(x_percent * max_width - text_width / 2)
        y = int(y_percent * max_height - text_height / 2)
        # Create a temp image for rotation
        temp_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), text, font=font, fill=(r, g, b, a))
        rotated = temp_img.rotate(-rotation, expand=1, resample=Image.BICUBIC)
        # Paste rotated text onto text_img
        rx, ry = rotated.size
        text_img.paste(rotated, (x - (rx - text_width)//2, y - (ry - text_height)//2), rotated)
        return text_img
    except Exception as e:
        print(f"Error creating advanced text image: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 