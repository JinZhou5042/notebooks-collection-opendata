# ATLAS H→γγ TaskVine Demo

This runs the ATLAS Open Data H→γγ analysis with TaskVine. The analysis is adapted from [`HyyAnalysis.ipynb`](../HyyAnalysis.ipynb), and the download uses the same `atlasopenmagic`/`fsspec` cache setup as the notebook.

The demo has three main components:

- `download_data.py` discovers the 16 public CERN ROOT files with `atlasopenmagic` and downloads them through `fsspec.simplecache`.
- `hyy_analysis.py` contains the ROOT reading, event selections, histogram, cutflow, and result merging adapted from [`HyyAnalysis.ipynb`](../HyyAnalysis.ipynb).
- `hyy_taskvine.py` starts the manager, submits one task per ROOT file, waits for workers, and writes the JSON result.

Create the environment once:

```bash
conda env create -f environment.yml
conda activate hyy-taskvine-demo
export PYTHONNOUSERSITE=1
```

Download the approximately 9.86 GB dataset:

```bash
python download_data.py
```

Start the manager in one shell:

```bash
python hyy_taskvine.py --port 9123
```

Start a worker from the same directory and Conda environment in another shell:

```bash
vine_worker 127.0.0.1 9123 --cores 16 --single-shot
```

Workers are started with `vine_worker`, not by the Python script or a factory. Downloaded files are stored in `data/` and reused by later runs. The analysis writes the histogram, cutflow, event counts, timing, and run configuration to `hyy-results.json`.

Paths and worker resources can be changed explicitly:

```bash
python download_data.py --data-dir /path/to/data
python hyy_taskvine.py --data-dir /path/to/data \
  --output /path/to/results.json --port 9123
```

To process selected local files instead, repeat `--input-file` as needed:

```bash
python hyy_taskvine.py --input-file file1.root --input-file file2.root
```
