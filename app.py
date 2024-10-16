from flask import Flask, render_template, request, redirect, url_for, send_file, flash, after_this_request
import os
import yt_dlp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Directory to save the downloaded files
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


# Function to download media
def download_media(url, format_choice, quality):
    quality_mapping = {
        'best': 'best',
        'High': 'bestvideo[height<=720]+bestaudio',
        'Medium': 'bestvideo[height<=480]+bestaudio',
        'Low': 'bestvideo[height<=360]+bestaudio',
    }

    ydl_opts = {
        'format': quality_mapping.get(quality, 'best'),
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(result)
    return filename, result['title']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('input-url')
    format_choice = request.form.get('select-video-or-audio')
    quality = request.form.get('select-quality')

    try:
        # Download the media
        filepath, title = download_media(url, format_choice, quality)

        flash(f'Successfully downloaded: {title}', 'success')

        # Use after_this_request to delete the file after download
        @after_this_request
        def remove_file(response):
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file {filepath}: {str(e)}")
            return response

        # Return the downloaded file for the user to download
        return send_file(filepath, as_attachment=True)

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('home'))


@app.route('/clear_downloads')
def clear_downloads():
    """ Clear all downloaded files from the server """
    for f in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error: {str(e)}")
    flash('All downloaded files have been cleared.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
