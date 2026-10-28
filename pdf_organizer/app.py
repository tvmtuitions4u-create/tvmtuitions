import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from models import db, Document

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pdf-organizer-secret-key-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pdf_organizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'zip', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    subject = request.args.get('subject', '').strip()
    batch = request.args.get('batch', '').strip()
    category = request.args.get('category', '').strip()
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Document.query

    if q:
        like = f'%{q}%'
        query = query.filter(
            db.or_(
                Document.title.ilike(like),
                Document.description.ilike(like),
                Document.tags.ilike(like),
                Document.subject.ilike(like),
                Document.class_name.ilike(like),
                Document.notes.ilike(like),
                Document.original_filename.ilike(like)
            )
        )
    if subject:
        query = query.filter(Document.subject.ilike(f'%{subject}%'))
    if batch:
        query = query.filter(Document.batch.ilike(f'%{batch}%'))
    if category:
        query = query.filter(Document.category == category)
    if date_from:
        try:
            query = query.filter(Document.class_date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        except ValueError:
            pass
    if date_to:
        try:
            query = query.filter(Document.class_date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        except ValueError:
            pass

    documents = query.order_by(Document.uploaded_at.desc()).all()

    # Distinct values for filters
    subjects = [r[0] for r in db.session.query(Document.subject).distinct().filter(Document.subject.isnot(None)).all() if r[0]]
    batches = [r[0] for r in db.session.query(Document.batch).distinct().filter(Document.batch.isnot(None)).all() if r[0]]
    categories = [r[0] for r in db.session.query(Document.category).distinct().all()]

    return render_template('index.html', documents=documents, q=q, subject=subject, batch=batch,
                           category=category, date_from=date_from, date_to=date_to,
                           subjects=subjects, batches=batches, categories=categories)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            original = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            stored_name = f"{timestamp}_{original}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
            file.save(filepath)

            class_date = None
            if request.form.get('class_date'):
                try:
                    class_date = datetime.strptime(request.form['class_date'], '%Y-%m-%d').date()
                except ValueError:
                    pass

            doc = Document(
                filename=stored_name,
                original_filename=original,
                title=request.form.get('title') or original,
                description=request.form.get('description'),
                subject=request.form.get('subject'),
                batch=request.form.get('batch'),
                class_name=request.form.get('class_name'),
                class_date=class_date,
                students=request.form.get('students'),
                tags=request.form.get('tags'),
                category=request.form.get('category') or 'PDF',
                notes=request.form.get('notes'),
                file_size=os.path.getsize(filepath),
                mime_type=file.content_type
            )
            db.session.add(doc)
            db.session.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('detail', doc_id=doc.id))
        else:
            flash('File type not allowed', 'danger')
    return render_template('upload.html')

@app.route('/document/<int:doc_id>')
def detail(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return render_template('detail.html', doc=doc)

@app.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
def edit(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if request.method == 'POST':
        doc.title = request.form.get('title') or doc.title
        doc.description = request.form.get('description')
        doc.subject = request.form.get('subject')
        doc.batch = request.form.get('batch')
        doc.class_name = request.form.get('class_name')
        doc.students = request.form.get('students')
        doc.tags = request.form.get('tags')
        doc.category = request.form.get('category') or doc.category
        doc.notes = request.form.get('notes')
        if request.form.get('class_date'):
            try:
                doc.class_date = datetime.strptime(request.form['class_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            doc.class_date = None
        doc.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Document updated!', 'success')
        return redirect(url_for('detail', doc_id=doc.id))
    return render_template('edit.html', doc=doc)

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete(doc_id):
    doc = Document.query.get_or_404(doc_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], doc.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted', 'success')
    return redirect(url_for('index'))

@app.route('/download/<int:doc_id>')
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True,
                               download_name=doc.original_filename)

@app.route('/static-catalog')
def static_catalog():
    """Live version of the static catalog (can be exported)."""
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template('static_catalog.html', documents=documents)

@app.route('/generate-static')
def generate_static():
    """Generate a self-contained static HTML file with all metadata + client-side search."""
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    data = [d.to_dict() for d in documents]
    html = render_template('static_catalog_export.html', documents=documents, json_data=data)
    export_path = os.path.join(app.root_path, 'static', 'pdf_catalog.html')
    with open(export_path, 'w', encoding='utf-8') as f:
        f.write(html)
    flash(f'Static catalog generated at static/pdf_catalog.html', 'success')
    return redirect(url_for('index'))

@app.route('/api/documents')
def api_documents():
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    return jsonify([d.to_dict() for d in documents])

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
