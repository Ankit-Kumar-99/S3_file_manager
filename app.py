from flask import Flask, render_template, request, redirect, flash
import boto3
import secrets  # Import the secrets module

app = Flask(__name__)

# Generate a secret key
secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key

s3 = boto3.client('s3', aws_access_key_id='AKIAV4WDUNFH53WM7F7O', aws_secret_access_key='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')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list', methods=['GET'])
def list_buckets():
    try:
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return render_template('index.html', buckets=buckets)
    except Exception as e:
        flash('An error occurred while listing buckets: ' + str(e))
        return render_template('index.html')


@app.route('/create_bucket', methods=['POST'])
def create_bucket():
    bucket_name = request.form['bucket_name']
    
    if not bucket_name:
        flash('Bucket name cannot be empty', 'error')
        return redirect('/')
    
    try:
        region = 'us-east-2'  # Specify the desired AWS region here
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
        flash(f'Bucket "{bucket_name}" created successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/delete_bucket', methods=['POST'])
def delete_bucket():
    bucket_name = request.form['bucket_name']
    
    if not bucket_name:
        flash('Bucket name cannot be empty', 'error')
        return redirect('/')
    
    try:
        s3.delete_bucket(Bucket=bucket_name)
        flash(f'Bucket "{bucket_name}" deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/list_content', methods=['POST'])
def list_content():
    try:
        bucket_name = request.form['bucket_name']
        if not bucket_name:
            flash('Bucket name cannot be empty', 'error')
        else:
            response = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                content_list = [obj['Key'] for obj in response['Contents']]
                return render_template('index.html', bucket_name=bucket_name, content_list=content_list)
            else:
                flash(f'Bucket "{bucket_name}" is empty', 'error')
    except Exception as e:
        flash('An error occurred while listing bucket content: ' + str(e), 'error')
    
    return redirect('/')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        bucket_name = request.form['bucket_name']
        file = request.files['file']
        if file:
            file_key = file.filename
            s3.upload_fileobj(file, bucket_name, file_key)
            flash('File uploaded successfully')
        else:
            flash('No file selected for upload')
    except Exception as e:
        flash('An error occurred while uploading the file: ' + str(e))
    return redirect('/')

@app.route('/delete_file', methods=['POST'])
def delete_file():
    try:
        bucket_name = request.form['bucket_name']
        file_key = request.form['file_key']
        s3.delete_object(Bucket=bucket_name, Key=file_key)
        flash('File deleted successfully')
    except Exception as e:
        flash('An error occurred while deleting the file: ' + str(e))
    return redirect('/')

@app.route('/copy_file', methods=['POST'])
def copy_file():
    try:
        source_key = request.form['source_key']
        destination_key = request.form['destination_key']
        source_bucket = request.form['source_bucket']
        destination_bucket = request.form['destination_bucket']
        
        if not source_key or not destination_key or not source_bucket or not destination_bucket:
            flash('All fields are required for copying files', 'error')
        else:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
            flash('File copied successfully', 'success')
    except Exception as e:
        flash('An error occurred while copying the file: ' + str(e), 'error')
    
    return redirect('/')

@app.route('/move_file', methods=['POST'])
def move_file():
    try:
        source_key = request.form['source_key']
        destination_key = request.form['destination_key']
        source_bucket = request.form['source_bucket']
        destination_bucket = request.form['destination_bucket']
        
        if not source_key or not destination_key or not source_bucket or not destination_bucket:
            flash('All fields are required for moving files', 'error')
        else:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            s3.copy_object(CopySource=copy_source, Bucket=destination_bucket, Key=destination_key)
            s3.delete_object(Bucket=source_bucket, Key=source_key)
            flash('File moved successfully', 'success')
    except Exception as e:
        flash('An error occurred while moving the file: ' + str(e), 'error')
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

