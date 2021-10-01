import sys
import os
import json


def lens_to_entry(name, HWND="", registers=[0, 0, 0]):
    return {
        "name": name,
        "HWND": HWND,
        "registers": registers,
        "selected": False,
    }


lenses = [
    ["C1", ""],
    ["C2", ""],
    ["C3", ""],
    ["MC", ""],
    ["OL", ""],
    ["LL", ""],
    ["DL", ""],
    ["IL", ""],
    ["P1", ""],
    ["P2", ""],
]

gun_deflection = [
    ["ux", ""],
    ["uy", ""],
    ["lx", ""],
    ["ly", ""],
]

condenser_deflection = [
    ["ux", ""],
    ["uy", ""],
    ["lx", ""],
    ["ly", ""],
]

beam_deflection = [
    ["ux", ""],
    ["uy", ""],
    ["lx", ""],
    ["ly", ""],
]

image_deflection = [
    ["ux", ""],
    ["uy", ""],
    ["lx", ""],
    ["ly", ""],
]

stigmator_control = [
    ["Cx", ""],
    ["Cy", ""],
    ["Ox", ""],
    ["Oy", ""],
    ["Dx", ""],
    ["Dy", ""],
]

if __name__ == "__main__":
    entries = []

    entries.append(
        {"name": "Lenses", "lenses": [lens_to_entry(*ctrl) for ctrl in lenses]}
    )
    entries.append(
        {
            "name": "Gun deflection",
            "lenses": [lens_to_entry(*ctrl) for ctrl in gun_deflection],
        }
    )
    entries.append(
        {
            "name": "Condenser Deflection",
            "lenses": [lens_to_entry(*ctrl) for ctrl in condenser_deflection],
        }
    )
    entries.append(
        {
            "name": "Beam Deflection",
            "lenses": [lens_to_entry(*ctrl) for ctrl in beam_deflection],
        }
    )
    entries.append(
        {
            "name": "Image Deflection",
            "lenses": [lens_to_entry(*ctrl) for ctrl in image_deflection],
        }
    )
    entries.append(
        {
            "name": "Stigmator Control",
            "lenses": [lens_to_entry(*ctrl) for ctrl in stigmator_control],
        }
    )

    if len(sys.argv) > 1:
        path = os.path.abspath(sys.argv[1])
    else:
        path = "lens_definition_file.lens"

    with open(path, "w") as f:
        json.dump(entries, f)
