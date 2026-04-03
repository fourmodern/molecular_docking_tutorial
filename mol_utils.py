"""
mol_utils.py — PyMOL-free utility functions for molecular docking pipeline.
Replaces pymol.cmd with MDAnalysis + requests + openbabel.
Works in Docker/WSL where pymol-open-source is not installed.
"""

import os
import urllib.request
import warnings
import numpy as np

warnings.filterwarnings("ignore")


def fetch_pdb(pdb_code, save_dir="."):
    """Download PDB file from RCSB."""
    pdb_code = pdb_code.lower()
    url = f"https://files.rcsb.org/download/{pdb_code}.pdb"
    out_path = os.path.join(save_dir, f"{pdb_code}.pdb")
    if not os.path.exists(out_path):
        urllib.request.urlretrieve(url, out_path)
    return out_path


def extract_chain(pdb_path, chain="A", output=None):
    """Extract a single chain from PDB, keep only protein atoms."""
    import MDAnalysis as mda

    u = mda.Universe(pdb_path)
    sel = u.select_atoms(f"chainID {chain} and protein")
    if output is None:
        output = pdb_path.replace(".pdb", f"_chain{chain}.pdb")
    sel.write(output)
    return output


def extract_ligand(pdb_path, chain="A", output=None):
    """Extract organic ligand (HETATM, non-water, non-protein) from PDB."""
    import MDAnalysis as mda
    from openbabel import pybel

    u = mda.Universe(pdb_path)
    # Select HETATM that are not water and not protein
    lig_sel = u.select_atoms(
        f"(chainID {chain} or chainID *) and not protein and not resname HOH WAT SOL"
    )
    if len(lig_sel) == 0:
        # Try without chain filter
        lig_sel = u.select_atoms("not protein and not resname HOH WAT SOL")

    if len(lig_sel) < 3:
        print(f"  Warning: only {len(lig_sel)} ligand atoms found")
        return None

    # Save as PDB first, then convert to MOL2 via openbabel
    tmp_pdb = pdb_path.replace(".pdb", "_lig_tmp.pdb")
    lig_sel.write(tmp_pdb)

    if output is None:
        output = pdb_path.replace(".pdb", "_lig.mol2")

    mol = list(pybel.readfile(format="pdb", filename=tmp_pdb))[0]
    out = pybel.Outputfile(filename=output, format="mol2", overwrite=True)
    out.write(mol)
    out.close()
    os.remove(tmp_pdb)
    return output


def pdb_clean(pdb_code, chain="A", work_dir="."):
    """
    Fetch PDB, extract chain, separate protein and ligand.
    Returns: (clean_pdb, lig_mol2)
    """
    pdb_path = fetch_pdb(pdb_code, save_dir=work_dir)

    clean_pdb = os.path.join(work_dir, f"{pdb_code}_clean.pdb")
    lig_mol2 = os.path.join(work_dir, f"{pdb_code}_lig.mol2")

    # Extract protein chain
    extract_chain(pdb_path, chain=chain, output=clean_pdb)

    # Extract ligand
    result = extract_ligand(pdb_path, chain=chain, output=lig_mol2)
    if result is None:
        print(f"  Warning: no ligand found in {pdb_code} chain {chain}")

    print(f"  Protein: {clean_pdb}")
    print(f"  Ligand:  {lig_mol2}")
    return clean_pdb, lig_mol2


def get_docking_box(lig_path, extending=7.0):
    """
    Calculate docking box from ligand coordinates.
    Returns: (center_dict, size_dict)
    """
    import MDAnalysis as mda

    fmt = "mol2" if lig_path.endswith(".mol2") else "pdb"
    u = mda.Universe(lig_path, format=fmt)
    coords = u.atoms.positions

    minX, minY, minZ = coords.min(axis=0)
    maxX, maxY, maxZ = coords.max(axis=0)

    pad = float(extending)
    center = {
        "center_x": float((maxX + minX) / 2),
        "center_y": float((maxY + minY) / 2),
        "center_z": float((maxZ + minZ) / 2),
    }
    size = {
        "size_x": float(maxX - minX + 2 * pad),
        "size_y": float(maxY - minY + 2 * pad),
        "size_z": float(maxZ - minZ + 2 * pad),
    }
    print(f"  Box center: ({center['center_x']:.1f}, {center['center_y']:.1f}, {center['center_z']:.1f})")
    print(f"  Box size:   ({size['size_x']:.1f}, {size['size_y']:.1f}, {size['size_z']:.1f})")
    return center, size


def cealign(ref_pdb, mobile_pdb, output=None):
    """Align mobile structure to reference using MDAnalysis."""
    import MDAnalysis as mda
    from MDAnalysis.analysis import align as mda_align

    ref = mda.Universe(ref_pdb)
    mobile = mda.Universe(mobile_pdb)

    mda_align.alignto(mobile, ref, select="protein and name CA")

    if output is None:
        output = mobile_pdb
    mobile.atoms.write(output)
    return output
