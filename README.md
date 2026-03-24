# 🎨 Image Background Remover & Editor

A modern Flask web application that allows users to upload images, remove backgrounds using AI, and add editable text layers. Perfect for creating professional portraits, social media content, and marketing materials.

## ✨ Features

- **AI-Powered Background Removal**: Uses Remove.bg API for high-quality background removal
- **Layer Management**: Toggle between original image, background-removed image, and text layers
- **Text Editor**: Add, edit, and style text with various fonts, sizes, and colors
- **Drag & Drop Interface**: Modern, responsive UI with drag-and-drop file upload
- **Real-time Preview**: See changes instantly as you edit
- **Session Management**: Save and load text content for each editing session
- **Mobile Responsive**: Works perfectly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Remove.bg API key (free tier available)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Remove.bg API key**:

   - Sign up at [remove.bg](https://www.remove.bg/api)
   - Get your free API key
   - Replace the API key in `app.py` line 15:
     ```python
     REMOVE_BG_API_KEY = 'your-api-key-here'
     ```

4. **Run the application**:

   ```bash
   python app.py
   ```

5. **Open your browser** and go to `http://localhost:5000`

## 📖 How to Use

### 1. Upload an Image

- Drag and drop an image file onto the upload area, or click to browse
- Supported formats: JPG, PNG, GIF, BMP (max 10MB)
- The app will automatically remove the background using AI

### 2. Edit in the Layer Editor

- **Layer Controls**: Toggle visibility of original image, background-removed image, and text layer
- **Text Editor**:
  - Type your text in the text area
  - Choose font size, family, and color
  - Apply bold/italic styling
  - Click "Apply Text" to see changes
- **Text Positioning**: Drag the text layer to position it anywhere on the image

### 3. Save Your Work

- Text content is automatically saved as you type
- Use "Save Text" to manually save your text
- Use "Load Saved Text" to restore previously saved text

## 🛠️ Technical Details

### Project Structure

```
Tbw/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Upload page
│   └── editor.html       # Layer editor page
└── uploads/              # Uploaded images and session data
    └── layers_[session_id]/
        ├── original_[filename]  # Original uploaded image
        ├── nobg_[filename]      # Background-removed image
        └── text_content.txt     # Saved text content
```

### API Endpoints

- `GET /` - Main upload page
- `POST /upload` - Upload image and remove background
- `GET /editor/<session_id>` - Open editor for specific session
- `POST /save_text` - Save text content
- `GET /get_text` - Load saved text content
- `GET /uploads/<path>` - Serve uploaded files

### Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Image Processing**: Remove.bg API, Pillow
- **Styling**: Modern CSS with gradients and animations

## 🔧 Configuration

### Environment Variables

You can set these environment variables for production:

```bash
export FLASK_SECRET_KEY="your-secret-key"
export REMOVE_BG_API_KEY="your-remove-bg-api-key"
```

### Customization

- **File size limit**: Modify `MAX_FILE_SIZE` in `app.py`
- **Allowed file types**: Edit `ALLOWED_EXTENSIONS` in `app.py`
- **Styling**: Customize CSS in the HTML template files

## 🚀 Deployment

### Local Development

```bash
python app.py
```

### Production Deployment

For production deployment, consider using:

- **WSGI Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx
- **Process Manager**: Supervisor or systemd

Example with Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📝 API Usage

The Remove.bg API has usage limits:

- **Free tier**: 50 images per month
- **Paid plans**: Available for higher usage

Monitor your usage at [remove.bg/api](https://www.remove.bg/api)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Troubleshooting

### Common Issues

**"Failed to remove background" error**

- Check your Remove.bg API key is correct
- Verify you have remaining API credits
- Ensure the image file is valid and under 10MB

**Images not loading**

- Check the `uploads/` directory has proper permissions
- Verify file paths in the browser console

**Text not saving**

- Check browser console for JavaScript errors
- Verify the session is active

### Support

If you encounter issues:

1. Check the browser console for errors
2. Verify all dependencies are installed
3. Ensure your API key is valid
4. Check the Flask application logs

## 🎯 Future Enhancements

- [ ] Export final composition as image
- [ ] Multiple text layers
- [ ] Image filters and effects
- [ ] Undo/redo functionality
- [ ] Collaborative editing
- [ ] Cloud storage integration

---

**Happy editing! 🎨**
