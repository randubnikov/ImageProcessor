import boto3
import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from boto3.dynamodb.conditions import Attr

app = Flask(__name__)
CORS(app)

s3        = boto3.client('s3', region_name=os.environ['AWS_REGION'])
dynamodb  = boto3.resource('dynamodb', region_name=os.environ['AWS_REGION'])

ORIGINAL_BUCKET  = os.environ['ORIGINAL_BUCKET']
PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']
DYNAMODB_TABLE   = os.environ['DYNAMODB_TABLE']
AWS_REGION       = os.environ['AWS_REGION']

def get_presigned_url(bucket, key, expiry=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiry
    )

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/images')
def list_images():
    table  = dynamodb.Table(DYNAMODB_TABLE)
    result = table.scan()
    images = result.get('Items', [])

    for image in images:
        urls = {}
        for size, key in image.get('processed_keys', {}).items():
            urls[size] = get_presigned_url(PROCESSED_BUCKET, key)
        image['urls'] = urls
        image['original_url'] = get_presigned_url(ORIGINAL_BUCKET, image['original_key'])

    images.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(images)

@app.route('/images/<image_id>')
def get_image(image_id):
    table  = dynamodb.Table(DYNAMODB_TABLE)
    result = table.get_item(Key={'image_id': image_id})
    image  = result.get('Item')

    if not image:
        return jsonify({'error': 'Image not found'}), 404

    urls = {}
    for size, key in image.get('processed_keys', {}).items():
        urls[size] = get_presigned_url(PROCESSED_BUCKET, key)
    image['urls'] = urls
    image['original_url'] = get_presigned_url(ORIGINAL_BUCKET, image['original_key'])

    return jsonify(image)

@app.route('/upload', methods=['POST'])
def get_upload_url():
    data     = request.get_json()
    filename = data.get('filename', 'image.jpg')
    key      = f"{uuid.uuid4()}/{filename}"

    presigned = s3.generate_presigned_post(
        Bucket     = ORIGINAL_BUCKET,
        Key        = key,
        ExpiresIn  = 300,
        Conditions = [['content-length-range', 1, 10485760]]
    )

    return jsonify({'upload_url': presigned, 'key': key})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
