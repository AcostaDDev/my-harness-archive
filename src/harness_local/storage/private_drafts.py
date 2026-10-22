"""Private onboarding drafts with content CAS, beside the application database."""
from hashlib import sha256
from pathlib import Path
import stat

from harness_local.adapters.bootstrap import DraftConflict, _current, _replace_file
from harness_local.core.engine.definition import allowed_draft, definition_layout, draft_directories
from harness_local.core.engine.documents import MAX_DOCUMENT_BYTES

def area_root(engine, area) -> Path:
    parent = Path(engine.url.database).resolve().parent / area
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        raise ValueError('The import drafts area must be a private directory')
    parent.mkdir(mode=0o700, exist_ok=True)
    return parent


class PrivateDrafts:
    """Drafts of an import conversation; the same interface as the definition reader."""

    area = 'onboarding-drafts'

    def __init__(self, base: Path):
        self.base = base

    @classmethod
    def of(cls, engine, conversation_id: str) -> 'PrivateDrafts':
        if not isinstance(conversation_id, str) or not conversation_id or '/' in conversation_id or conversation_id in ('.', '..'):
            raise ValueError('Invalid import conversation id')
        return cls(area_root(engine, cls.area) / conversation_id)

    def _folder(self) -> Path | None:
        if self.base.is_symlink() or (self.base.exists() and not self.base.is_dir()):
            raise ValueError('The import drafts folder must be a directory')
        return self.base if self.base.exists() else None

    def inspect_definition(self, context, *, texts=False):
        """Admitted drafts (D088 template and `flows/*.md`), invalid and foreign ones in the area."""
        target = definition_layout(context)
        folders = draft_directories(target)
        drafts, contents, foreign, invalid = {}, {}, [], []

        def visit(folder, prefix):
            for item in sorted(folder.iterdir(), key=lambda entry: entry.name):
                path = prefix + item.name
                mode = item.lstat().st_mode
                if stat.S_ISDIR(mode) and path in folders:
                    visit(item, path + '/')
                elif stat.S_ISREG(mode) and allowed_draft(target, path):
                    data = item.read_bytes()
                    try:
                        if len(data) > MAX_DOCUMENT_BYTES or b'\0' in data or stat.S_IMODE(mode) & 0o111:
                            raise ValueError(path)
                        text = data.decode('utf-8')
                    except (ValueError, UnicodeError):
                        invalid.append(path)
                        continue
                    drafts[path] = sha256(data).hexdigest()
                    contents[path] = text
                elif not item.name.endswith('.harness-tmp'):
                    foreign.append(path + ('/' if stat.S_ISDIR(mode) else ''))

        if (folder := self._folder()) is not None:
            visit(folder, '')
        result = {'drafts': drafts, 'foreign': foreign[:100], 'foreign_truncated': len(foreign) > 100,
                  'invalid': invalid, 'import_required': False}
        return {**result, 'texts': contents} if texts else result

    def write_draft(self, context, path, content, base_sha256):
        """Writes (or deletes with `content=None`) a draft if its hash is still `base_sha256`."""
        target = definition_layout(context)
        if not allowed_draft(target, path):
            raise ValueError(f'{path} is not an allowed import draft')
        folders = draft_directories(target)
        self._folder()
        parts = path.split('/')
        for n in range(1, len(parts)):
            folder = self.base.joinpath(*parts[:n])
            if '/'.join(parts[:n]) not in folders or folder.is_symlink() or (folder.exists() and not folder.is_dir()):
                raise ValueError(f'{path} is not inside an allowed draft folder')
        item = self.base.joinpath(*parts)
        current = _current(item)
        after = None if content is None else sha256(content.encode('utf-8')).hexdigest()
        if current == after:
            return {'before': current, 'after': after, 'written': False}
        if current != base_sha256:
            raise DraftConflict(f'{path} changed since it was read (expected {base_sha256}, found {current})')
        if content is None:
            item.unlink()
        else:
            self.base.mkdir(mode=0o700, exist_ok=True)
            item.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            _replace_file(item, content.encode('utf-8'), 'draft', lambda: _current(item) == base_sha256)
        return {'before': current, 'after': after, 'written': True}
