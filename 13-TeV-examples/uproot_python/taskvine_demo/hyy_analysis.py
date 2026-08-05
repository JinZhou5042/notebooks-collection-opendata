import numpy as np
import awkward as ak
import uproot
import vector


TREE_NAME = "analysis"
VARIABLES = [
    "photon_pt",
    "photon_eta",
    "photon_phi",
    "photon_e",
    "photon_isTightID",
    "photon_ptcone20",
]
BIN_EDGES = np.arange(100, 161, 1)


def cut_photon_reconstruction(is_tight):
    return is_tight[:, 0] & is_tight[:, 1]


def cut_photon_pt(pt):
    return (pt[:, 0] > 50) & (pt[:, 1] > 30)


def cut_isolation_pt(ptcone20, pt):
    return ((ptcone20[:, 0] / pt[:, 0]) < 0.055) & (
        (ptcone20[:, 1] / pt[:, 1]) < 0.055
    )


def cut_photon_eta_transition(eta):
    condition_0 = (np.abs(eta[:, 0]) < 1.52) | (np.abs(eta[:, 0]) > 1.37)
    condition_1 = (np.abs(eta[:, 1]) < 1.52) | (np.abs(eta[:, 1]) > 1.37)
    return condition_0 & condition_1


def calc_mass(pt, eta, phi, energy):
    p4 = vector.zip({"pt": pt, "eta": eta, "phi": phi, "e": energy})
    return (p4[:, 0] + p4[:, 1]).M


def cut_mass(mass):
    return mass != 0


def cut_iso_mass(pt, mass):
    return ((pt[:, 0] / mass) > 0.35) & ((pt[:, 1] / mass) > 0.35)


def process_file(path):
    tree = uproot.open(f"{path}:{TREE_NAME}")
    cutflow = np.zeros(7, dtype=np.int64)
    masses = []

    for data in tree.iterate(VARIABLES, library="ak"):
        cutflow[0] += len(data)
        data = data[cut_photon_reconstruction(data["photon_isTightID"])]
        cutflow[1] += len(data)
        data = data[cut_photon_pt(data["photon_pt"])]
        cutflow[2] += len(data)
        data = data[cut_isolation_pt(data["photon_ptcone20"], data["photon_pt"])]
        cutflow[3] += len(data)
        data = data[cut_photon_eta_transition(data["photon_eta"])]
        cutflow[4] += len(data)
        data["mass"] = calc_mass(
            data["photon_pt"],
            data["photon_eta"],
            data["photon_phi"],
            data["photon_e"],
        )
        data = data[cut_mass(data["mass"])]
        cutflow[5] += len(data)
        data = data[cut_iso_mass(data["photon_pt"], data["mass"])]
        cutflow[6] += len(data)
        masses.append(data["mass"])

    masses = ak.concatenate(masses) if masses else ak.Array([])
    histogram, _ = np.histogram(ak.to_numpy(masses), bins=BIN_EDGES)
    return {
        "histogram": histogram.astype(np.int64),
        "cutflow": cutflow,
        "entries": int(cutflow[0]),
        "selected": int(cutflow[-1]),
    }


def merge_results(results):
    return {
        "histogram": np.sum(
            [result["histogram"] for result in results], axis=0, dtype=np.int64
        ),
        "cutflow": np.sum(
            [result["cutflow"] for result in results], axis=0, dtype=np.int64
        ),
        "entries": sum(result["entries"] for result in results),
        "selected": sum(result["selected"] for result in results),
    }
