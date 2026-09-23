# ODF JupyterHub notebook

The [self-contained notebook](hyy-taskvine-demo.ipynb) runs the ATLAS Open Data H→γγ analysis on [ODF JupyterHub](https://jupyterhub.odf.uchicago.edu/) with worker pods created through `taskvine-gateway`.

Upload the notebook to ODF JupyterHub and run Part 0 to install and select the `Python (taskvine-atlas)` kernel. Then continue in order. In Part 2, run `!ls /data` and replace `REPLACE_ME` with your own shared-data directory name before downloading the 16 ROOT files. Run the final cleanup cell when finished.

A run on ODF on 2026-09-23 completed 16 tasks with 36,564,144 entries and 553,458 selected events in 54.3 seconds. These are observations from that run; rerun the notebook to obtain results for your environment.
