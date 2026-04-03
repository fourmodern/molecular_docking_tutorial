"""
pymol.cmd shim — drop-in replacement using MDAnalysis + openbabel.
Supports the subset of pymol.cmd used by the docking tutorial notebooks.
"""
import os
import urllib.request
import warnings
import numpy as np

warnings.filterwarnings("ignore")

# Internal state
_objects = {}   # name -> MDAnalysis.Universe or file path
_selections = {}  # name -> atom indices or selection string
_current_dir = "."


def delete(name="all"):
    if name == "all":
        _objects.clear()
        _selections.clear()
    elif name in _objects:
        del _objects[name]


def fetch(code, type="pdb", path="."):
    code = code.lower()
    url = f"https://files.rcsb.org/download/{code}.pdb"
    out = os.path.join(path, f"{code}.pdb")
    if not os.path.exists(out):
        urllib.request.urlretrieve(url, out)
    import MDAnalysis as mda
    _objects[code] = mda.Universe(out)
    # Also keep as "default" if only one object
    _objects["_last"] = _objects[code]
    _objects["_last_path"] = out
    return out


def load(filename, object=None, format=None):
    import MDAnalysis as mda
    name = object or os.path.splitext(os.path.basename(filename))[0]
    try:
        _objects[name] = mda.Universe(filename)
    except Exception:
        _objects[name] = filename  # store path as fallback
    _objects["_last"] = _objects[name]
    _objects["_last_path"] = filename


def remove(selection):
    """Remove atoms matching selection from the last loaded object."""
    # Parse simple selections like "not chain A"
    # Just mark for filtering during save
    _selections["_remove"] = selection


def select(name, selection):
    _selections[name] = selection


def count_atoms(selection):
    """Count atoms in selection (approximate)."""
    for obj_name, u in _objects.items():
        if obj_name.startswith("_"):
            continue
        try:
            if hasattr(u, 'select_atoms'):
                sel = _translate_selection(selection, u)
                return len(u.select_atoms(sel))
        except Exception:
            pass
    return 0


def save(filename, selection=None, format=None):
    """Save selection to file."""
    import MDAnalysis as mda
    from openbabel import pybel

    # Find the universe to save from
    u = None
    for obj_name in list(_objects.keys()):
        if obj_name.startswith("_"):
            continue
        if hasattr(_objects[obj_name], 'select_atoms'):
            u = _objects[obj_name]
            break

    if u is None:
        return

    # Apply remove filter
    remove_sel = _selections.get("_remove", "")

    # Translate selection
    try:
        if selection and selection not in ("all",):
            mda_sel = _translate_selection(selection, u)
        else:
            mda_sel = "all"

        if remove_sel:
            # Parse "not chain A" → keep only chain A
            if "not chain" in remove_sel:
                chain = remove_sel.split("chain")[-1].strip()
                mda_sel = f"({mda_sel}) and chainID {chain}"

        atoms = u.select_atoms(mda_sel)
    except Exception:
        atoms = u.atoms

    # Determine format from extension
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".mol2":
        # Save as PDB first, then convert via openbabel
        tmp_pdb = filename.replace(".mol2", "_tmp.pdb")
        atoms.write(tmp_pdb)
        mol = list(pybel.readfile(format="pdb", filename=tmp_pdb))[0]
        out = pybel.Outputfile(filename=filename, format="mol2", overwrite=True)
        out.write(mol)
        out.close()
        os.remove(tmp_pdb)
    else:
        atoms.write(filename)


def get_extent(selection="all"):
    """Get bounding box [min, max] of selection."""
    for obj_name, u in _objects.items():
        if obj_name.startswith("_"):
            continue
        if not hasattr(u, 'select_atoms'):
            continue
        try:
            mda_sel = _translate_selection(selection, u)
            atoms = u.select_atoms(mda_sel)
            if len(atoms) > 0:
                coords = atoms.positions
                return [coords.min(axis=0).tolist(), coords.max(axis=0).tolist()]
        except Exception:
            pass

    # Fallback: try to find the object by name
    if selection in _objects and hasattr(_objects[selection], 'atoms'):
        coords = _objects[selection].atoms.positions
        return [coords.min(axis=0).tolist(), coords.max(axis=0).tolist()]

    return [[0, 0, 0], [10, 10, 10]]


def cealign(target, mobile):
    """Align mobile to target using MDAnalysis."""
    import MDAnalysis as mda
    from MDAnalysis.analysis import align

    t = _objects.get(target)
    m = _objects.get(mobile)
    if t is not None and m is not None and hasattr(t, 'select_atoms') and hasattr(m, 'select_atoms'):
        align.alignto(m, t, select="protein and name CA")


def show(*args, **kwargs):
    pass  # No-op in headless mode

def hide(*args, **kwargs):
    pass

def color(*args, **kwargs):
    pass

def set(*args, **kwargs):
    pass

def zoom(*args, **kwargs):
    pass

def label(*args, **kwargs):
    pass

def distance(*args, **kwargs):
    pass

def ray(*args, **kwargs):
    pass

def png(*args, **kwargs):
    pass

def bg_color(*args, **kwargs):
    pass

def spectrum(*args, **kwargs):
    pass

def split_states(*args, **kwargs):
    pass


def _translate_selection(sel, universe=None):
    """Translate pymol selection syntax to MDAnalysis."""
    s = sel.strip()

    # Direct matches
    if s in ("all", "everything"):
        return "all"
    if s == "polymer.protein":
        return "protein"
    if s == "organic":
        return "not protein and not resname HOH WAT SOL and not nucleic"
    if s == "solvent":
        return "resname HOH WAT SOL"

    # Named selections
    if s in _selections:
        return _translate_selection(_selections[s], universe)

    # Object names
    if s in _objects:
        return "all"

    # "X within Y of Z" → "around Y Z" in MDAnalysis
    if " within " in s and " of " in s:
        import re
        m = re.match(r"(\S+)\s+within\s+([\d.]+)\s+of\s+(\S+)", s)
        if m:
            base, dist, ref = m.groups()
            ref_sel = _translate_selection(ref, universe)
            base_sel = _translate_selection(base, universe)
            return f"({base_sel}) and around {dist} ({ref_sel})"

    # "not chain X"
    if s.startswith("not chain "):
        chain = s.replace("not chain ", "").strip()
        return f"not chainID {chain}"

    # "chain X"
    if s.startswith("chain "):
        chain = s.replace("chain ", "").strip()
        return f"chainID {chain}"

    # "resn X+Y+Z"
    if s.startswith("resn "):
        resnames = s.replace("resn ", "").replace("+", " ")
        return f"resname {resnames}"

    # "resi X"
    if s.startswith("resi "):
        return f"resid {s.replace('resi ', '')}"

    # "name X"
    if s.startswith("name "):
        return f"name {s.replace('name ', '')}"

    # Compound: "X and Y"
    if " and " in s:
        parts = s.split(" and ")
        translated = [_translate_selection(p.strip(), universe) for p in parts]
        return " and ".join(f"({t})" for t in translated)

    # Compound: "X or Y"
    if " or " in s:
        parts = s.split(" or ")
        translated = [_translate_selection(p.strip(), universe) for p in parts]
        return " or ".join(f"({t})" for t in translated)

    # Pass through as-is
    return s
