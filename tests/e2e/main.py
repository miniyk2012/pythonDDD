import tempfile
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
from pathlib import Path

if __name__ == '__main__':
    tempdir = tempfile.mkdtemp()
    filename = "orders.csv"
    path1 = Path(tempdir) / filename
    path = Path(__file__).parent / "../../src/bin/allocate-from-csv"
    spec = spec_from_loader("script", SourceFileLoader("script", str(path)))
    script = module_from_spec(spec)
    spec.loader.exec_module(script)
    script.main(path1)
