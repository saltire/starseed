import base64
import io
import os

from flask import Flask, flash, redirect, render_template, request, url_for

from starseed.starseed import generate_map


app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def serve_form():
    return render_template('form.html')

@app.route('/map', methods=['POST'])
def get_map():
    try:
        img = generate_map(request.files['savefile'].read())
    except:
        flash('There was an error uploading your file. Please try again.')
        return redirect(url_for('serve_form'))

    output = io.BytesIO()
    img.save(output, format='PNG')

    return render_template('map.html',
        image='data:image/png;base64,' + base64.b64encode(output.getvalue()).decode('ascii'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
