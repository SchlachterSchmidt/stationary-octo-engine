"""S3 helper using Boto3."""

import boto3

from app import app


s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET']
)


def upload_file_to_s3(image, fileStoreObj, acl="public-read"):
    """S3 file uploader."""
    try:
        s3.put_object(Body=image,
                      Bucket=app.config['S3_BUCKET'],
                      ACL=acl,
                      ContentType=fileStoreObj.content_type,
                      Key=fileStoreObj.filename)

    except Exception as e:
        print("An Error occurred: ", e)
        return e
    return "{}{}".format(app.config["S3_LOCATION"], fileStoreObj.filename)
