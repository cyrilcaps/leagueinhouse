
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("../leagueinhouse-firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def set_batch(collection, document_id, documents):
    batch = db.batch()
    for document in documents:
        doc_ref = db.collection(collection).document(document_id)
        doc_ref.set(document)
    batch.commit()

def set_document(collection, document_id, document):
    doc_ref = db.collection(collection).document(document_id)
    doc_ref.set(document)

def get_document(collection, document_id, document):
    doc_ref = db.collection(collection).document(document_id)
    return doc_ref.get(document)
