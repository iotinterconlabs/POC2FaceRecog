import boto3
REGION_NAME = 'ap-south-1'
AWS_ACCESS_KEY_ID = 'AKIAIH677GI5PK2ZV6UQ'
AWS_SECRET = '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'
BUCKET = "facedetectiondemo"


def get_all_s3_bucket():
    buckets = []
    s3 = boto3.resource('s3', region_name='ap-south-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET)
    buckets = [bucket for bucket in s3.buckets.all()]
    return buckets

def get_all_s3_bucket_names():
    buckets = []
    s3 = boto3.resource('s3', region_name='ap-south-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET)
    buckets = [bucket.name for bucket in s3.buckets.all()]
    return buckets

def bucket_safe_to_create(bucket_name):
    if bucket_name in get_all_s3_bucket_names():
        return False
    else:
        return True
    
def create_bucket(bucket_name):
    bucket_name = str(AWS_ACCESS_KEY_ID).lower() + bucket_name
    if bucket_safe_to_create(bucket_name):
        s3 = boto3.client('s3', region_name='ap-south-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET)
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': REGION_NAME})
        return True
    else:
        return False

def upload_images_to_bucket(bucket_name, img):
    create_bucket(bucket_name)
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET,
    )
    s3 = session.resource('s3')
    bucket_name = str(AWS_ACCESS_KEY_ID).lower() + bucket_name
    key ='media/{}'.format(img.name)
    s3.Bucket(bucket_name).put_object(Key=key, Body=img)
    return bucket_name, key
        
def get_bucket_key_dict():
    bucket_key = {}
    for buckt in get_all_s3_bucket():
        bucket_key[buckt.name] = []
        for obj in buckt.objects.all():
            bucket_key[buckt.name].append(obj.key)
    return bucket_key

def delete_match_bucket(bucket_name):
    bucket_name = str(AWS_ACCESS_KEY_ID).lower() + bucket_name
    s3 = boto3.resource('s3', region_name='ap-south-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET)
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()

def delete_bucket(bucket_name):  
    s3 = boto3.resource('s3', region_name='ap-south-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET)
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()


def compare_faces(bucket, key, bucket_target, key_target, threshold=97, region='ap-south-1'):
        rekognition = boto3.client("rekognition", region_name='ap-south-1', aws_access_key_id='AKIAIH677GI5PK2ZV6UQ',
    aws_secret_access_key='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')
        response = rekognition.compare_faces(
            SourceImage={
                "S3Object": {
                    "Bucket": bucket,
                    "Name": key,
                }
            },
            TargetImage={
                "S3Object": {
                    "Bucket": bucket_target,
                    "Name": key_target,
                }
            },
            SimilarityThreshold=threshold,
        )
        return response['SourceImageFace'], response['FaceMatches']

def match_person(per_bucket, per_key):
    bucket_name = 'No Match'
    score = '0.0'
    bucket_found = False
    all_buckets = get_bucket_key_dict()
    del all_buckets[per_bucket]
    for bucket, keys in all_buckets.items():
        for key in keys:
            source_face, matches = compare_faces(per_bucket, per_key, bucket, key)            
            for match in matches:
                scr = match['Similarity']
                if scr > 97 and bucket != per_bucket:
                    bucket_name = bucket
                    score = scr
                    bucket_found = True
                    break
            if bucket_found:
                break
        if bucket_found:
            break
    person = bucket_name.replace('akiaih677gi5pk2zv6uq','')
    return person, score
            

