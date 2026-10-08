# Original dependency ZIP

`python.zip` is the original archive supplied by the project author. It contains requests and dependencies (certifi, charset_normalizer, idna, urllib3), not the Lambda handler.

Inspection found Windows executables, Windows Python 3.14 `.pyd` extensions, and cached bytecode. AWS Lambda runs on Linux. Some libraries contain Python fallbacks, but do not assume Windows binaries will load on Lambda; this original archive is preserved for reference, not certified as a compatible layer.

The repository weather implementation uses built-in urllib, so no requests layer is needed.

To reproduce a requests-based implementation, build a fresh layer in a Linux environment compatible with the chosen Lambda runtime and architecture, such as an appropriate Lambda Python container or AWS CloudShell. For requests alone, a pure-Python wheel build can avoid Windows extensions:

```bash
mkdir -p layer/python
python3 -m pip install --only-binary=:all: --platform any --target layer/python requests
cd layer
zip -r requests-layer.zip python
```

Choose dependencies compatible with your actual Python runtime. In Lambda Console → Layers → Create layer, upload the fresh ZIP, select the matching compatible runtime, then attach that layer to your requests-based function. The `python/` folder must be at the ZIP root.
