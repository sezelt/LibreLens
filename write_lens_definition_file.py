import sys
import os
import json


def lens_to_entry(name, position, registers=[0.0, 0.0, 0.0]):
    return {
        "name": name,
        "HWND": 0xBAD0BAD0,
        "position": position,
        "registers": registers,
        "selected": False,
    }


lenses = [
    ["C1", 0],
    ["C2", 1],
    ["C3", 2],
    ["MC", 3],
    ["OL", 4],
    ["LL", 5],
    ["DL", 6],
    ["IL", 7],
    ["P1", 8],
    ["P2", 9],
]

gun_deflection = [
    ["ux", 10],
    ["uy", 11],
    ["lx", 12],
    ["ly", 13],
]

condenser_deflection = [
    ["ux", 14],
    ["uy", 15],
    ["lx", 16],
    ["ly", 17],
]

beam_deflection = [
    ["ux", 18],
    ["uy", 19],
    ["lx", 20],
    ["ly", 21],
]

image_deflection = [
    ["ux", 22],
    ["uy", 23],
    ["lx", 24],
    ["ly", 25],
]

stigmator_control = [
    ["Cx", 26],
    ["Cy", 27],
    ["Ox", 28],
    ["Oy", 29],
    ["Dx", 30],
    ["Dy", 31],
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
