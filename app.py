from flask import Flask, render_template, request, redirect
import boto3

app = Flask(__name__)
s3 = boto3.client('s3', aws_access_key_id='AKIAV4WDUNFHSYEFX7ND', aws_secret_access_key='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')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list', methods=['GET'])
def list_buckets():
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return render_template('index.html', buckets=buckets)

@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
    return redirect('/')

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form['bucket_name']
    s3.delete_bucket(Bucket=bucket_name)
    return redirect('/')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    bucket_name = request.form['bucket_name']
    file = request.files['file']
    file_key = file.filename
    s3.upload_fileobj(file, bucket_name, file_key)
    return redirect('/')

@app.route('/delete_file', methods=['POST'])
def delete_file():
    bucket_name = request.form['bucket_name']
    file_key = request.form['file_key']
    s3.delete_object(Bucket=bucket_name, Key=file_key)
    return redirect('/')

@app.route('/copy_file', methods=['POST'])
def copy_file():
    source_key = request.form['source_key']
    destination_key = request.form['destination_key']
    bucket_name = request.form['bucket_name']
    s3.copy_object(CopySource={'Bucket': bucket_name, 'Key': source_key}, Bucket=bucket_name, Key=destination_key)
    return redirect('/')

@app.route('/move_file', methods=['POST'])
def move_file():
    source_key = request.form['source_key']
    destination_key = request.form['destination_key']
    bucket_name = request.form['bucket_name']
    s3.copy_object(CopySource={'Bucket': bucket_name, 'Key': source_key}, Bucket=bucket_name, Key=destination_key)
    s3.delete_object(Bucket=bucket_name, Key=source_key)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

