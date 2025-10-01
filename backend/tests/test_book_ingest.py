import pytest
import asyncio
from unittest.mock import MagicMock, patch

from backend.ai.book_ingest import process_book


class DummyDB:
    def __init__(self):
        self._collections = {}

    def get_collection(self, name):
        if name not in self._collections:
            self._collections[name] = MagicMock()
        return self._collections[name]


@pytest.fixture
def dummy_db(tmp_path, monkeypatch):
    db = DummyDB()
    # set up collections to behave like pymongo collection
    coll = db.get_collection('physics_books')
    coll.insert_one = MagicMock(return_value=MagicMock(inserted_id='book123'))
    coll.find_one = MagicMock(return_value={'_id': 'book123', 'title': 'Test Book'})
    import pytest
    import asyncio
    from unittest.mock import MagicMock, patch

    from backend.ai.book_ingest import process_book


    class DummyDB:
        def __init__(self):
            self._collections = {}

        def get_collection(self, name):
            if name not in self._collections:
                self._collections[name] = MagicMock()
            return self._collections[name]


    @pytest.fixture
    def dummy_db(tmp_path, monkeypatch):
        db = DummyDB()
        # set up collections to behave like pymongo collection
        coll = db.get_collection('physics_books')
        coll.insert_one = MagicMock(return_value=MagicMock(inserted_id='book123'))
        coll.find_one = MagicMock(return_value={'_id': 'book123', 'title': 'Test Book'})
        coll.update_one = MagicMock()

        chunks_coll = db.get_collection('book_chunks')
        chunks_coll.insert_one = MagicMock(return_value=MagicMock(inserted_id='chunkid'))
        chunks_coll.find = MagicMock(return_value=[])
        chunks_coll.update_one = MagicMock()

        return db


    def test_process_txt_dryrun(dummy_db, tmp_path, monkeypatch):
        # create a sample txt file
        p = tmp_path / "sample.txt"
        p.write_text("This is a test book. " * 200)

        # ensure embeddings are mocked
        async def fake_embed(chunks):
            out = []
            for c in chunks:
                out.append({**c, 'embedding': [0.1, 0.2, 0.3]})
            return out

        monkeypatch.setattr('backend.ai.book_ingest.embed_chunks', lambda chunks: fake_embed(chunks))

        summary = process_book(dummy_db, 'book123', str(p), dry_run=True)
        assert summary['book_id'] == 'book123'
        assert summary['dry_run'] is True
        assert summary['chunks'] > 0


    @patch('backend.ai.book_ingest.ocr_file')
    def test_process_pdf_ocr(mock_ocr, dummy_db, tmp_path, monkeypatch):
        # create a fake pdf path (we won't read it because ocr_file is mocked)
        pdf_path = str(tmp_path / "doc.pdf")
        mock_ocr.return_value = {'pages': [{'page': 1, 'text': 'Page one text.'}, {'page': 2, 'text': 'Page two text.'}], 'text': 'Page one text.\n\nPage two text.'}

        async def fake_embed(chunks):
            out = []
            for c in chunks:
                out.append({**c, 'embedding': [0.1, 0.2]})
            return out

        monkeypatch.setattr('backend.ai.book_ingest.embed_chunks', lambda chunks: fake_embed(chunks))

        summary = process_book(dummy_db, 'book123', pdf_path, dry_run=True)
        assert summary['book_id'] == 'book123'
        assert summary['chunks'] == 2 or summary['chunks'] == 1 or summary['chunks'] > 0