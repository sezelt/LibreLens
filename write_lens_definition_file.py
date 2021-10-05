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
    ["C1", "000210EE"],
    ["C2", "000210EC"],
    ["C3", "000210EA"],
    ["MC", "000210E8"],
    ["OL", "000210E6"],
    ["LL", "000210A8"],
    ["DL", "000210E4"],
    ["IL", "000210E2"],
    ["P1", "000210E0"],
    ["P2", "000210DE"],
]

gun_deflection = [
    ["ux", "000210DC"],
    ["uy", "000210DA"],
    ["lx", "000210D8"],
    ["ly", "000210D6"],
]

condenser_deflection = [
    ["ux", "0002108C"],
    ["uy", "0002108A"],
    ["lx", "00021088"],
    ["ly", "00021086"],
]

beam_deflection = [
    ["ux", "000210D4"],
    ["uy", "000210D2"],
    ["lx", "000210D0"],
    ["ly", "000210CE"],
]

image_deflection = [
    ["ux", "000210CC"],
    ["uy", "000210CA"],
    ["lx", "000210C8"],
    ["ly", "000210C6"],
]

stigmator_control = [
    ["Cx", "000210C4"],
    ["Cy", "000210C2"],
    ["Ox", "000210C0"],
    ["Oy", "000210BE"],
    ["Dx", "000210BC"],
    ["Dy", "000210BA"],
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
