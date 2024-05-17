from flask import Flask, render_template, request, session, send_from_directory, redirect, url_for
import pandas as pd
import re
from openai import OpenAI
import os
from werkzeug.utils import secure_filename
import send2trash

UPLOAD_FOLDER = os.path.join('upload_files')
DOWNLOAD_FOLDER = os.path.join('download_files')

ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'This is your secret key to utilize session in Flask'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        f = request.files.get('file')
        if f and allowed_file(f.filename):
            data_filename = secure_filename(f.filename)
            new_filename = os.path.splitext(data_filename)[0] + '_New.csv'
            f.save(os.path.join(DOWNLOAD_FOLDER, new_filename))
            session['uploaded_data_file_path'] = os.path.join(DOWNLOAD_FOLDER, new_filename)
            session['uploaded_data_file_name'] = new_filename  # Store the filename in session
            return render_template('index2.html')

    return render_template("index.html")

@app.route('/show_data')
def showData():
    data_file_path = session.get('uploaded_data_file_path', None)
    uploaded_df = pd.read_csv(data_file_path, encoding='unicode_escape')
    uploaded_df_html = uploaded_df.head(10).to_html()  # Only show top 10 rows
    return render_template('submit.html', data_var=uploaded_df_html)

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        data_type = request.form['data_type']
        request_input = request.form['request_input']
        field_input = request.form['field_input']
        try:
            api_call(data_type, request_input, field_input)
            # Set data_file_path to the path of the new filename
            data_file_path = os.path.join(DOWNLOAD_FOLDER, session['uploaded_data_file_name'])
            uploaded_df = pd.read_csv(data_file_path, encoding='unicode_escape')
            uploaded_df_html = uploaded_df.head(10).to_html()  # Only show top 10 rows
            return render_template('form.html', data_var=uploaded_df_html)
        except Exception as e:
            return render_template('error.html', error_message=str(e))

    return render_template('form.html')

@app.route('/download')
def download_file():
    data_file_path = os.path.join(DOWNLOAD_FOLDER, session['uploaded_data_file_name'])
    directory = os.path.dirname(data_file_path )
    path = os.path.basename(data_file_path )
    response = send_from_directory(directory, path, as_attachment=True)
    # Move the downloaded file to trash after download
    send2trash.send2trash(data_file_path)
    return response

@app.route('/clear_files', methods=['GET'])
def clear_files():
    # Remove all files from the upload_files directory
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error while deleting file {file_path}: {e}")
    # Remove all files from the download_files directory
    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error while deleting file {file_path}: {e}")
    return redirect(url_for('uploadFile'))

@app.route('/refresh')
def refresh():
    return render_template('refresh.html')

def api_call(data_type, request_input, field_input):
    client = OpenAI(api_key="")
    chat_completion_2 = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"when Dataframe = df, the field = 'field', data type for 'field' is {data_type}: give me a python script, with no comments,that {request_input}"
            }
        ],
        model="gpt-4",
    )

    df = pd.DataFrame(chat_completion_2)
    choices_str = df[1].iloc[1]
    df1 = pd.DataFrame(choices_str)
    t = str(df1[3].values[0])
    match = re.search(r'content(.+?)role', t)
    if match:
        content_string = match.group()
    else:
        print('did not find')
    content_string = match.group()
    replace_string_1 = (content_string.replace('content="','')).replace('", role','')
    new_string = replace_string_1.replace('```python\\nimport pandas as pd\\n\\n','').replace('\\n```','').replace('import pandas as pd\\n\\n','').replace('\\n','').replace('\\\\','').replace('\\','').replace('```python','')

    def read_csv_file():
        test_1_path = os.path.join(DOWNLOAD_FOLDER, session['uploaded_data_file_name'])  # Use the uploaded file name
        if os.path.isfile(test_1_path):
            data = pd.read_csv(test_1_path)
        else:
            data = pd.read_csv(os.path.join(UPLOAD_FOLDER, session['uploaded_data_file_name']))
        return data

    data = read_csv_file()
    df = pd.DataFrame(data)
    input_field = field_input
    new_string_1 = new_string.replace('field',input_field)
    data_file_path = os.path.join(DOWNLOAD_FOLDER, session['uploaded_data_file_name'])
    exec(new_string_1)
    df.to_csv(data_file_path, index=False) 

if __name__ == '__main__':
    app.run(debug=True)




















