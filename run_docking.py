#!/usr/bin/env python3
"""
Molecular Docking Pipeline (Standalone)
Colab 없이 WSL/Docker에서 실행하는 도킹 스크립트.

Usage:
    python run_docking.py                          # TYK2 기본 도킹
    python run_docking.py --pdb 1M17 --chain A     # 다른 타겟
    python run_docking.py --smiles "CCO" --name ethanol  # 커스텀 리간드
"""

import argparse
import os
import sys
import stat
import subprocess
import urllib.request
import tarfile
import shutil
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# 1. Binary tools setup
# ============================================================

BIN_DIR = os.path.expanduser("~/docking_bin")
os.makedirs(BIN_DIR, exist_ok=True)


def install_smina():
    smina_path = os.path.join(BIN_DIR, "smina")
    if os.path.exists(smina_path):
        return smina_path
    print("Installing smina...")
    urllib.request.urlretrieve(
        "https://sourceforge.net/projects/smina/files/smina.static/download",
        smina_path,
    )
    st = os.stat(smina_path)
    os.chmod(smina_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print("  smina installed.")
    return smina_path


def install_adfrsuite():
    adfr_dir = os.path.join(BIN_DIR, "ADFRsuite")
    prep_rec = os.path.join(BIN_DIR, "prepare_receptor")
    if os.path.exists(prep_rec):
        return
    print("Installing ADFRsuite...")
    adfr_tar = "/tmp/ADFRsuite.tar.gz"
    try:
        urllib.request.urlretrieve(
            "https://ccsb.scripps.edu/adfr/download/1038/", adfr_tar
        )
        with tarfile.open(adfr_tar) as tar:
            tar.extractall("/tmp/")
        adfr_extracted = [
            d for d in os.listdir("/tmp/") if d.startswith("ADFRsuite")
        ][0]
        orig_dir = os.getcwd()
        try:
            os.chdir(f"/tmp/{adfr_extracted}")
            subprocess.run(
                ["bash", "install.sh", "-d", adfr_dir, "-c", "0"],
                input=b"Y\n",
                capture_output=True,
            )
        finally:
            os.chdir(orig_dir)
        # Create wrapper scripts
        for tool in ["prepare_receptor", "prepare_ligand"]:
            wrapper = os.path.join(BIN_DIR, tool)
            adfr_tool = os.path.join(adfr_dir, "bin", tool)
            if os.path.exists(adfr_tool) and not os.path.exists(wrapper):
                with open(wrapper, "w") as f:
                    f.write(f"#!/bin/bash\n{adfr_tool} \"$@\"\n")
                st = os.stat(wrapper)
                os.chmod(
                    wrapper, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
                )
        print("  ADFRsuite installed.")
    except Exception as e:
        print(f"  ADFRsuite install warning: {e}")
    finally:
        if os.path.exists(adfr_tar):
            os.remove(adfr_tar)
        for d in os.listdir("/tmp/"):
            if d.startswith("ADFRsuite"):
                shutil.rmtree(f"/tmp/{d}", ignore_errors=True)


# ============================================================
# 2. Import chemistry libraries
# ============================================================

def check_imports():
    try:
        from pymol import cmd
        from vina import Vina
        from openbabel import pybel
        from rdkit import Chem
        from rdkit.Chem import AllChem, PandasTools
        from pdbfixer import PDBFixer
        from openmm.app import PDBFile
        import MDAnalysis as mda
        import prolif as plf
        import pandas as pd
        return True
    except ImportError as e:
        print(f"Missing package: {e}")
        print("Run: pip install rdkit-pypi meeko vina openbabel-wheel pdbfixer openmm pymol-open-source MDAnalysis prolif seaborn")
        return False


# ============================================================
# 3. Core pipeline functions
# ============================================================

def pdb_clean(pdb_code, chain="A", work_dir="."):
    """Fetch PDB, extract chain, separate protein and ligand."""
    from pymol import cmd

    clean_pdb = os.path.join(work_dir, f"{pdb_code}_clean.pdb")
    lig_mol2 = os.path.join(work_dir, f"{pdb_code}_lig.mol2")

    cmd.delete("all")
    cmd.fetch(code=pdb_code, type="pdb", path=work_dir)
    cmd.remove(f"not chain {chain}")
    cmd.select(name="Prot", selection="polymer.protein")
    cmd.select(name="Lig", selection="organic")

    n_lig = cmd.count_atoms("Lig")
    if n_lig < 5:
        print(f"  Warning: only {n_lig} ligand atoms in chain {chain}")

    cmd.save(filename=clean_pdb, format="pdb", selection="Prot")
    cmd.save(filename=lig_mol2, format="mol2", selection="Lig")
    cmd.delete("all")

    print(f"  Protein: {clean_pdb}")
    print(f"  Ligand:  {lig_mol2}")
    return clean_pdb, lig_mol2


def fix_protein(filename, output, addHs_pH=7.4):
    """Fix missing atoms and add hydrogens with PDBFixer."""
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile

    fixer = PDBFixer(filename=filename)
    fixer.findMissingResidues()
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(True)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(addHs_pH)
    with open(output, "w") as f:
        PDBFile.writeFile(fixer.topology, fixer.positions, f)
    print(f"  Fixed protein: {output}")
    return output


def prep_ligand(lig_mol2):
    """Add hydrogens to ligand."""
    from openbabel import pybel

    lig_H = lig_mol2.replace(".mol2", "_H.mol2")
    mol = list(pybel.readfile(format="mol2", filename=lig_mol2))[0]
    mol.addh()
    out = pybel.Outputfile(filename=lig_H, format="mol2", overwrite=True)
    out.write(mol)
    out.close()
    print(f"  Ligand +H: {lig_H}")
    return lig_H


def get_docking_box(prot_H, lig_H, extending=7.0):
    """Calculate docking box from ligand position using PyMOL."""
    from pymol import cmd

    cmd.delete("all")
    cmd.load(filename=prot_H, format="pdb", object="prot")
    cmd.load(filename=lig_H, format="mol2", object="lig")

    ([minX, minY, minZ], [maxX, maxY, maxZ]) = cmd.get_extent("lig")
    pad = float(extending)
    center = {
        "center_x": (maxX + minX) / 2,
        "center_y": (maxY + minY) / 2,
        "center_z": (maxZ + minZ) / 2,
    }
    size = {
        "size_x": maxX - minX + 2 * pad,
        "size_y": maxY - minY + 2 * pad,
        "size_z": maxZ - minZ + 2 * pad,
    }
    cmd.delete("all")
    print(f"  Box center: ({center['center_x']:.1f}, {center['center_y']:.1f}, {center['center_z']:.1f})")
    print(f"  Box size:   ({size['size_x']:.1f}, {size['size_y']:.1f}, {size['size_z']:.1f})")
    return center, size


def make_pdbqt(prot_H, lig_H):
    """Convert protein and ligand to PDBQT format."""
    rec_qt = prot_H.replace(".pdb", ".pdbqt")
    lig_qt = lig_H.replace(".mol2", ".pdbqt")

    prep_rec = os.path.join(BIN_DIR, "prepare_receptor")
    prep_lig = os.path.join(BIN_DIR, "prepare_ligand")

    if os.path.exists(prep_rec):
        subprocess.run([prep_rec, "-r", prot_H, "-o", rec_qt], capture_output=True)
    else:
        # Fallback: use meeko/openbabel
        from openbabel import pybel
        mol = list(pybel.readfile(format="pdb", filename=prot_H))[0]
        out = pybel.Outputfile(filename=rec_qt, format="pdbqt", overwrite=True)
        out.write(mol)
        out.close()

    if os.path.exists(prep_lig):
        subprocess.run([prep_lig, "-l", lig_H, "-o", lig_qt], capture_output=True)
    else:
        from openbabel import pybel
        mol = list(pybel.readfile(format="mol2", filename=lig_H))[0]
        out = pybel.Outputfile(filename=lig_qt, format="pdbqt", overwrite=True)
        out.write(mol)
        out.close()

    print(f"  Receptor PDBQT: {rec_qt}")
    print(f"  Ligand PDBQT:   {lig_qt}")
    return rec_qt, lig_qt


def run_vina(rec_qt, lig_qt, center, size, exhaustiveness=64, n_poses=20):
    """Run AutoDock Vina docking."""
    from vina import Vina
    from openbabel import pybel

    out_pdbqt = rec_qt.replace(".pdbqt", "_vina_out.pdbqt")
    out_sdf = out_pdbqt.replace(".pdbqt", ".sdf")

    v = Vina(sf_name="vina")
    v.set_receptor(rec_qt)
    v.set_ligand_from_file(lig_qt)
    v.compute_vina_maps(
        center=[center["center_x"], center["center_y"], center["center_z"]],
        box_size=[size["size_x"], size["size_y"], size["size_z"]],
    )

    energy = v.score()
    print(f"  Score before min: {energy[0]:.3f} kcal/mol")
    energy_min = v.optimize()
    print(f"  Score after min:  {energy_min[0]:.3f} kcal/mol")

    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    v.write_poses(out_pdbqt, n_poses=n_poses, overwrite=True)

    # Convert PDBQT → SDF
    out = pybel.Outputfile(filename=out_sdf, format="sdf", overwrite=True)
    for mol in pybel.readfile(format="pdbqt", filename=out_pdbqt):
        mol.data["Pose"] = mol.data.get("MODEL", "?")
        mol.data["Score"] = (
            mol.data.get("REMARK", "").split()[2] if "REMARK" in mol.data else "0"
        )
        for k in ["MODEL", "REMARK", "TORSDO"]:
            mol.data.pop(k, None)
        out.write(mol)
    out.close()

    print(f"  Vina output: {out_sdf}")
    return out_sdf


def run_smina(rec_qt, lig_qt, center, size, exhaustiveness=128, n_poses=20, label="native"):
    """Run smina docking."""
    smina_path = os.path.join(BIN_DIR, "smina")
    out_sdf = rec_qt.replace(".pdbqt", f"_{label}_smina_out.sdf")

    cmd_args = [
        smina_path,
        "-r", rec_qt,
        "-l", lig_qt,
        "-o", out_sdf,
        "--center_x", str(center["center_x"]),
        "--center_y", str(center["center_y"]),
        "--center_z", str(center["center_z"]),
        "--size_x", str(size["size_x"]),
        "--size_y", str(size["size_y"]),
        "--size_z", str(size["size_z"]),
        "--exhaustiveness", str(exhaustiveness),
        "--num_modes", str(n_poses),
    ]
    subprocess.run(cmd_args, capture_output=True)
    print(f"  smina output: {out_sdf}")
    return out_sdf


# ============================================================
# 4. Analysis & export for DataWarrior
# ============================================================

def analyze_results(vina_sdf, smina_sdf, prot_H, lig_H, work_dir):
    """Analyze docking results and export CSV for DataWarrior."""
    from rdkit import Chem
    from rdkit.Chem import PandasTools, Descriptors, rdMolAlign
    import prolif as plf
    import pandas as pd

    results_dir = os.path.join(work_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    all_dfs = []

    for sdf_path, method in [(vina_sdf, "Vina"), (smina_sdf, "smina")]:
        if not os.path.exists(sdf_path):
            continue
        df = PandasTools.LoadSDF(
            sdf_path, smilesName="SMILES", molColName="Molecule",
            includeFingerprints=True, strictParsing=False,
        )
        # Normalize score column
        for col in df.columns:
            if "affinity" in col.lower() or "score" in col.lower():
                df.rename(columns={col: "minimizedAffinity"}, inplace=True)
                break
        if "minimizedAffinity" in df.columns:
            df["minimizedAffinity"] = pd.to_numeric(df["minimizedAffinity"], errors="coerce")

        df["Method"] = method
        df["Pose"] = range(1, len(df) + 1)

        # Molecular properties
        for i, row in df.iterrows():
            mol = row.get("Molecule")
            if mol is not None:
                df.loc[i, "MW"] = round(Descriptors.MolWt(mol), 1)
                df.loc[i, "cLogP"] = round(Descriptors.MolLogP(mol), 2)
                df.loc[i, "HBA"] = Descriptors.NumHAcceptors(mol)
                df.loc[i, "HBD"] = Descriptors.NumHDonors(mol)
                df.loc[i, "RotBonds"] = Descriptors.NumRotatableBonds(mol)
                df.loc[i, "TPSA"] = round(Descriptors.TPSA(mol), 1)
                ha = mol.GetNumHeavyAtoms()
                score = df.loc[i, "minimizedAffinity"] if "minimizedAffinity" in df.columns else 0
                df.loc[i, "HeavyAtoms"] = ha
                if ha > 0 and pd.notna(score):
                    df.loc[i, "LE"] = round(-score / ha, 3)

        all_dfs.append(df)

    if not all_dfs:
        print("  No results to analyze.")
        return

    df_all = pd.concat(all_dfs, ignore_index=True)

    # --- RMSD validation ---
    ref_mol = Chem.MolFromMol2File(lig_H, removeHs=False)
    if ref_mol is None:
        from openbabel import pybel
        pmol = list(pybel.readfile(format="mol2", filename=lig_H))[0]
        pmol.write("pdb", "/tmp/_ref.pdb", overwrite=True)
        ref_mol = Chem.MolFromPDBFile("/tmp/_ref.pdb", removeHs=False)

    if ref_mol is not None:
        ref_noH = Chem.RemoveHs(ref_mol)
        rmsd_list = []
        for sdf_path, method in [(vina_sdf, "Vina"), (smina_sdf, "smina")]:
            if not os.path.exists(sdf_path):
                continue
            for i, mol in enumerate(Chem.SDMolSupplier(sdf_path, removeHs=False)):
                if mol is None or i >= 10:
                    continue
                try:
                    mol_noH = Chem.RemoveHs(mol)
                    rmsd = rdMolAlign.GetBestRMS(ref_noH, mol_noH)
                    rmsd_list.append({"Method": method, "Pose": i + 1, "RMSD": round(rmsd, 2)})
                except Exception:
                    rmsd_list.append({"Method": method, "Pose": i + 1, "RMSD": None})

        if rmsd_list:
            rmsd_df = pd.DataFrame(rmsd_list)
            rmsd_csv = os.path.join(results_dir, "rmsd_validation.csv")
            rmsd_df.to_csv(rmsd_csv, index=False)
            print(f"  RMSD validation: {rmsd_csv}")

    # --- ProLIF interaction fingerprints ---
    try:
        prot_mol = Chem.MolFromPDBFile(prot_H, removeHs=False)
        if prot_mol is not None:
            prot_plf = plf.Molecule(prot_mol)
            lig_suppl = list(plf.sdf_supplier(vina_sdf))
            if lig_suppl:
                fp = plf.Fingerprint()
                fp.run_from_iterable(lig_suppl[:10], prot_plf)
                ifp_df = fp.to_dataframe()
                ifp_csv = os.path.join(results_dir, "interaction_fingerprints.csv")
                ifp_df.to_csv(ifp_csv)
                print(f"  Interactions: {ifp_csv}")
    except Exception as e:
        print(f"  ProLIF skipped: {e}")

    # --- Export CSV for DataWarrior ---
    export_cols = [c for c in df_all.columns if c != "Molecule"]
    csv_path = os.path.join(results_dir, "docking_scores.csv")
    df_all[export_cols].to_csv(csv_path, index=False)
    print(f"  Scores CSV (DataWarrior): {csv_path}")

    # --- Copy SDF files to results ---
    for sdf in [vina_sdf, smina_sdf]:
        if os.path.exists(sdf):
            shutil.copy2(sdf, results_dir)

    # --- Copy protein & ligand for PyMOL ---
    for f in [prot_H, lig_H]:
        if os.path.exists(f):
            shutil.copy2(f, results_dir)

    # --- Summary ---
    print("\n" + "=" * 50)
    print("  Results summary")
    print("=" * 50)
    if "minimizedAffinity" in df_all.columns:
        for method in df_all["Method"].unique():
            sub = df_all[df_all["Method"] == method]
            best = sub["minimizedAffinity"].min()
            mean = sub["minimizedAffinity"].mean()
            print(f"  {method:8s}: best={best:.2f}, mean={mean:.2f} kcal/mol ({len(sub)} poses)")

    print(f"\n  Results folder: {results_dir}")
    print("  → Open .sdf in PyMOL")
    print("  → Open .csv in DataWarrior")


# ============================================================
# 5. Custom ligand docking
# ============================================================

def dock_custom_smiles(smiles, name, rec_qt, center, size, work_dir):
    """Dock a custom SMILES string."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"  Invalid SMILES: {smiles}")
        return None

    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
    mol.SetProp("_Name", name)

    sdf_path = os.path.join(work_dir, f"{name}.sdf")
    writer = Chem.SDWriter(sdf_path)
    writer.write(mol)
    writer.close()

    # Convert to PDBQT
    from openbabel import pybel
    obmol = list(pybel.readfile(format="sdf", filename=sdf_path))[0]
    pdbqt_path = sdf_path.replace(".sdf", ".pdbqt")
    out = pybel.Outputfile(filename=pdbqt_path, format="pdbqt", overwrite=True)
    out.write(obmol)
    out.close()

    result_sdf = run_smina(rec_qt, pdbqt_path, center, size,
                           exhaustiveness=64, n_poses=10, label=name)
    return result_sdf


# ============================================================
# 6. Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Molecular Docking Pipeline")
    parser.add_argument("--pdb", default="6nzp", help="PDB code (default: 6nzp)")
    parser.add_argument("--chain", default="A", help="Chain ID (default: A)")
    parser.add_argument("--exhaustiveness", type=int, default=64, help="Search depth (default: 64)")
    parser.add_argument("--n-poses", type=int, default=20, help="Number of poses (default: 20)")
    parser.add_argument("--smiles", default=None, help="Custom ligand SMILES to dock")
    parser.add_argument("--name", default="custom", help="Name for custom ligand")
    parser.add_argument("--output", default="./docking_output", help="Output directory")
    args = parser.parse_args()

    print("=" * 50)
    print("  Molecular Docking Pipeline")
    print("=" * 50)
    print(f"  Target: {args.pdb} (chain {args.chain})")
    print(f"  Output: {args.output}")
    print()

    # Check dependencies
    if not check_imports():
        sys.exit(1)

    # Install binary tools
    install_smina()
    install_adfrsuite()

    # Setup working directory
    work_dir = os.path.abspath(args.output)
    os.makedirs(work_dir, exist_ok=True)

    # --- Pipeline ---
    print("\n[1/6] Fetching & cleaning PDB...")
    clean_pdb, lig_mol2 = pdb_clean(args.pdb, args.chain, work_dir)

    print("\n[2/6] Fixing protein (add H)...")
    prot_H = os.path.join(work_dir, f"{args.pdb}_clean_H.pdb")
    fix_protein(clean_pdb, prot_H)

    print("\n[3/6] Preparing ligand...")
    lig_H = prep_ligand(lig_mol2)

    print("\n[4/6] Computing docking box...")
    center, size = get_docking_box(prot_H, lig_H)

    print("\n[5/6] Converting to PDBQT...")
    rec_qt, lig_qt = make_pdbqt(prot_H, lig_H)

    print(f"\n[6/6] Running docking (exhaustiveness={args.exhaustiveness})...")
    print("  Running Vina...")
    vina_sdf = run_vina(rec_qt, lig_qt, center, size, args.exhaustiveness, args.n_poses)
    print("  Running smina...")
    smina_sdf = run_smina(rec_qt, lig_qt, center, size, args.exhaustiveness, args.n_poses)

    # Custom ligand
    if args.smiles:
        print(f"\n[Extra] Docking custom ligand: {args.name}")
        dock_custom_smiles(args.smiles, args.name, rec_qt, center, size, work_dir)

    # Analyze & export
    print("\n[Analysis] Generating results for PyMOL & DataWarrior...")
    analyze_results(vina_sdf, smina_sdf, prot_H, lig_H, work_dir)

    print("\n" + "=" * 50)
    print("  DONE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
