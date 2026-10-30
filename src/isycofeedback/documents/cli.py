"""Synthetic document demonstration with no external extraction provider."""
from .pipeline import Document, DocumentPipeline, Extraction, FieldValue
from .validation import FieldConfidencePolicy


class DemoDocumentService:
    """Fixed fixture metadata, explicitly for demonstration, not calibrated extraction."""
    name = 'demo-document-service'

    def extract(self, document: Document) -> Extraction:
        return Extraction(fields={
            'document_type': FieldValue('demo', .99, {'source': 'synthetic-fixture'}),
            'bytes': FieldValue(len(document.content), 1., {'source': 'synthetic-fixture'}),
        }, document_confidence=.91)


def demo() -> int:
    class UnknownExtractor:
        name = 'plain-text-normalizer'
        def extract(self, document):
            return Extraction({'text': FieldValue(document.content.decode(), None,
                                                 {'source': 'plain-text'})}, None)

    class ExplicitRejection:
        def review(self, extraction):
            return False

    result = DocumentPipeline(UnknownExtractor(), ExplicitRejection(),
                              rules=(FieldConfidencePolicy(('text',), .85),)).run(
        Document(b'Synthetic example', 'example.txt', 'text/plain'))
    valid, _ = result.evidence.verify()
    print(f'DOCUMENT {result.status} (unknown confidence, explicit demo rejection)')
    print(f'EVIDENCE {"VALID" if valid else "INVALID"}')
    return 0 if result.status == 'REJECTED' and valid else 1
