import boto3
import json
import os
import urllib.parse
from PIL import Image
import io
import uuid
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']
DYNAMODB_TABLE   = os.environ['DYNAMODB_TABLE']

SIZES = {
    'thumbnail': (100, 100),
    'medium':    (500, 500),
    'large':     (1200, 1200)
}

def lambda_handler(event, context):
    record         = event['Records'][0]
    source_bucket  = record['s3']['bucket']['name']
    source_key     = urllib.parse.unquote_plus(record['s3']['object']['key'])
    image_id       = str(uuid.uuid4())

    print(f"Processing {source_key} from {source_bucket}")

    response = s3.get_object(Bucket=source_bucket, Key=source_key)
    image_data = response['Body'].read()
    image = Image.open(io.BytesIO(image_data))

    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')

    processed_keys = {}

    for size_name, dimensions in SIZES.items():
        resized = image.copy()
        resized.thumbnail(dimensions, Image.LANCZOS)

        buffer = io.BytesIO()
        resized.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        processed_key = f"{size_name}/{source_key}"
        s3.put_object(
            Bucket      = PROCESSED_BUCKET,
            Key         = processed_key,
            Body        = buffer,
            ContentType = 'image/jpeg'
        )
        processed_keys[size_name] = processed_key
        print(f"Saved {size_name}: {processed_key}")

    table = dynamodb.Table(DYNAMODB_TABLE)
    table.put_item(Item={
        'image_id':       image_id,
        'original_key':   source_key,
        'original_bucket': source_bucket,
        'processed_keys': processed_keys,
        'processed_bucket': PROCESSED_BUCKET,
        'status':         'processed',
        'created_at':     datetime.utcnow().isoformat(),
        'filename':       source_key.split('/')[-1]
    })

    print(f"Saved metadata to DynamoDB: {image_id}")
    return {'statusCode': 200, 'body': json.dumps({'image_id': image_id})}
