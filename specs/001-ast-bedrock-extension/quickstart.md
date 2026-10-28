# Quickstart

```bash
pip install git+https://github.com/eraevous/AEC            # or: export PYTHONPATH=$AEC_HOME/src
python -m aec edges . -o .aec/edges.jsonl                  # snapshot the code
# ...edit code...
python -m aec edges . -o /tmp/new.jsonl && python -m aec edges --diff .aec/edges.jsonl /tmp/new.jsonl
python -m aec code-impact .aec/records.jsonl .aec/edges.jsonl /tmp/new.jsonl
specify extension add /path/to/AEC/extension                # inside a Spec Kit project
```
