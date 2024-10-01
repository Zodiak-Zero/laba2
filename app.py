from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.recaptcha import RecaptchaField
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Le4vFQqAAAAAH5sKKwj5gvUdAMTOVkEF8dzRQuW'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6Le4vFQqAAAAABNYTNhD5oPWizu5qpKNbG3VVN5z'


class UploadForm(FlaskForm):
    upload = FileField('Upload Image', validators=[DataRequired()])
    brightness = FloatField('Adjust Brightness', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Adjust Brightness')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.upload.data
        brightness = form.brightness.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Изменение яркости
            original_img = Image.open(file_path)
            enhancer = ImageEnhance.Brightness(original_img)
            bright_img = enhancer.enhance(brightness)
            bright_filename = 'bright_' + filename
            bright_img.save(os.path.join(app.config['UPLOAD_FOLDER'], bright_filename))

            # График распределения цветов
            color_distribution_path = os.path.join(app.config['UPLOAD_FOLDER'], 'color_distribution.png')
            plot_color_distribution(file_path, color_distribution_path)

            return redirect(url_for('result', original_img=filename, bright_img=bright_filename))
    return render_template('index.html', form=form)


@app.route('/result')
def result():
    original_img = request.args.get('original_img')
    bright_img = request.args.get('bright_img')
    return render_template('result.html', original_img=original_img, bright_img=bright_img)


def plot_color_distribution(image_path, save_path):
    try:
        # Загружаем изображение и проверяем, RGB ли это изображение
        image = Image.open(image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        img_np = np.array(image)

        # Извлечение каналов R, G, B
        red = img_np[:, :, 0].flatten()
        green = img_np[:, :, 1].flatten()
        blue = img_np[:, :, 2].flatten()

        # Построение гистограммы
        plt.figure(figsize=(10, 5))
        plt.hist(red, bins=256, color='red', alpha=0.5, label='Red', density=True)
        plt.hist(green, bins=256, color='green', alpha=0.5, label='Green', density=True)
        plt.hist(blue, bins=256, color='blue', alpha=0.5, label='Blue', density=True)

        plt.title('Color Distribution')
        plt.xlabel('Color value')
        plt.ylabel('Frequency')
        plt.legend()

        # Сохранение гистограммы
        plt.savefig(save_path)
        plt.close()
    except Exception as e:
        print(f"Error while plotting color distribution: {e}")


if __name__ == "__main__":
    app.run(debug=True)
