#!/usr/bin/env python3
"""Download the H->gammagamma inputs using the repository's cache mechanism."""

import argparse
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import atlasopenmagic as atom
import fsspec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    # Same atlasopenmagic + simplecache approach used by ../HyyAnalysis.ipynb.
    atom.set_release("2025e-13tev-beta")
    urls = atom.get_urls("data", "GamGam", protocol="https", cache=True)
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=120, sock_read=3600)
    data_dir = args.data_dir.resolve()
    http = fsspec.filesystem("https", client_kwargs={"timeout": timeout})
    files = []
    for index, url in enumerate(urls, 1):
        source = url.removeprefix("simplecache::")
        cached = data_dir / Path(urlparse(source).path).name
        if cached.exists() and cached.stat().st_size != http.info(source)["size"]:
            cached.unlink()
        print(f"downloading {index}/{len(urls)}", flush=True)
        files.append(
            fsspec.open_local(
                url,
                simplecache={
                    "cache_storage": str(data_dir),
                    "same_names": True,
                },
                https={"client_kwargs": {"timeout": timeout}},
            )
        )
    print(f"downloaded {len(files)} files to {data_dir}")


if __name__ == "__main__":
    main()
