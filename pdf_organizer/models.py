from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # stored filename
    original_filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(100))  # e.g. Math, Physics
    batch = db.Column(db.String(50))     # e.g. 2024, Batch-A
    class_name = db.Column(db.String(100))  # daily class / lecture name
    class_date = db.Column(db.Date)      # date of the class
    students = db.Column(db.Text)        # optional list of students or group
    tags = db.Column(db.String(500))     # comma-separated
    category = db.Column(db.String(50), default='PDF')  # PDF, Notes, Other
    notes = db.Column(db.Text)           # optional extra notes
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description or '',
            'subject': self.subject or '',
            'batch': self.batch or '',
            'class_name': self.class_name or '',
            'class_date': self.class_date.isoformat() if self.class_date else '',
            'students': self.students or '',
            'tags': self.tags or '',
            'category': self.category,
            'notes': self.notes or '',
            'original_filename': self.original_filename,
            'uploaded_at': self.uploaded_at.isoformat(),
            'file_size': self.file_size,
            'download_url': f'/download/{self.id}'
        }

    def tags_list(self):
        return [t.strip() for t in (self.tags or '').split(',') if t.strip()]
