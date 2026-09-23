# ATLAS H→γγ with TaskVine

Two ways to run the same ATLAS Open Data H→γγ analysis:

| Environment | Entry point | Worker setup |
| --- | --- | --- |
| ODF JupyterHub | [Notebook and instructions](odf_jupyterhub/README.md) | `taskvine-gateway` starts Kubernetes worker pods from the notebook. |
| Standalone cluster | [Python scripts and instructions](standalone/README.md) | Start a `vine_worker` separately and connect it to the Python manager. |

Both versions process the 16 public ROOT files and use the same event selection and histogram code. The ODF notebook writes its own helper files and packages a worker environment; the standalone version runs from the files in `standalone/`.
