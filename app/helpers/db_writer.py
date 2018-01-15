"""Module writing posted image and prediction to database."""

from ..models import ImageRef, User, db
from .s3_helper import upload_file_to_s3


class DB_Writer:
    """Writing image data to S3 and prediction to relational DB."""

    def write(self, image, fileStoreObj, prediction, probabilities, username):
        """Writing to persistence."""
        link = upload_file_to_s3(image, fileStoreObj)
        imageRef = ImageRef(
            user_id=User.query.filter_by(username=username).first().id,
            link=link,
            predicted_label=prediction,
            c0=probabilities[0],
            c1=probabilities[1],
            c2=probabilities[2],
            c3=probabilities[3],
            c4=probabilities[4],
            c5=probabilities[5],
            c6=probabilities[6],
            c7=probabilities[7],
            c8=probabilities[8],
            c9=probabilities[9],
        )
        db.session.add(imageRef)
        db.session.commit()
