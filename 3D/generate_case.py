#!/usr/bin/env python3
"""
3D Model Generator for ESP32 Wireless Stream Deck & Audio Mixer Enclosure
Generates 100% manifold, watertight STL files:
 - streamdeck_top_plate.stl
 - streamdeck_bottom_case.stl
"""

import math
import os
import sys

class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.vertex_map = {}

    def add_vertex(self, x, y, z):
        key = (round(x, 5), round(y, 5), round(z, 5))
        if key in self.vertex_map:
            return self.vertex_map[key]
        idx = len(self.vertices)
        self.vertices.append((x, y, z))
        self.vertex_map[key] = idx
        return idx

    def add_face(self, v0, v1, v2):
        if v0 != v1 and v1 != v2 and v2 != v0:
            self.faces.append((v0, v1, v2))

    def add_quad(self, v0, v1, v2, v3):
        # Two triangles with counter-clockwise winding (v0->v1->v2 and v0->v2->v3)
        self.add_face(v0, v1, v2)
        self.add_face(v0, v2, v3)

    def write_stl(self, file_path, solid_name="mesh"):
        print(f"Writing {len(self.faces)} facets to {file_path}...")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"solid {solid_name}\n")
            for face in self.faces:
                v0 = self.vertices[face[0]]
                v1 = self.vertices[face[1]]
                v2 = self.vertices[face[2]]
                # Normal vector via cross product: (v1 - v0) x (v2 - v0)
                ux, uy, uz = v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]
                vx, vy, vz = v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]
                nx = uy * vz - uz * vy
                ny = uz * vx - ux * vz
                nz = ux * vy - uy * vx
                length = math.sqrt(nx * nx + ny * ny + nz * nz)
                if length > 1e-9:
                    nx /= length
                    ny /= length
                    nz /= length
                else:
                    nx, ny, nz = 0.0, 0.0, 1.0

                f.write(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}\n")
                f.write("    outer loop\n")
                f.write(f"      vertex {v0[0]:.4f} {v0[1]:.4f} {v0[2]:.4f}\n")
                f.write(f"      vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}\n")
                f.write(f"      vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}\n")
                f.write("    endloop\n")
                f.write("  endfacet\n")
            f.write(f"endsolid {solid_name}\n")
        print(f"Successfully generated: {file_path}")


def add_prism_box(mesh, x0, x1, y0, y1, z0, z1):
    """Tilføjer en massiv rektangulær boks med udadpegende normaler."""
    # 8 hjørner
    v000 = mesh.add_vertex(x0, y0, z0)
    v100 = mesh.add_vertex(x1, y0, z0)
    v110 = mesh.add_vertex(x1, y1, z0)
    v010 = mesh.add_vertex(x0, y1, z0)

    v001 = mesh.add_vertex(x0, y0, z1)
    v101 = mesh.add_vertex(x1, y0, z1)
    v111 = mesh.add_vertex(x1, y1, z1)
    v011 = mesh.add_vertex(x0, y1, z1)

    # Bund (z = z0, normal -Z)
    mesh.add_quad(v000, v010, v110, v100)
    # Top (z = z1, normal +Z)
    mesh.add_quad(v001, v101, v111, v011)
    # Front (y = y0, normal -Y)
    mesh.add_quad(v000, v100, v101, v001)
    # Højre (x = x1, normal +X)
    mesh.add_quad(v100, v110, v111, v101)
    # Bagside (y = y1, normal +Y)
    mesh.add_quad(v110, v010, v011, v111)
    # Venstre (x = x0, normal -X)
    mesh.add_quad(v010, v000, v001, v011)


def build_top_plate():
    """
    Bygger top-pladen med præcise huller til:
      - 12 MX switches (14.2 x 14.2 mm) i 4x3 matrix
      - 4 Potentiometre (7.5 mm hul)
      - 1 OLED Display vindue (26.0 x 14.0 mm)
      - 4 Hjørneskruer (M3, 3.2 mm hul)
    Garanterer 100% manifold, lukket geometri uden indvendige flader.
    """
    mesh = Mesh()
    PLATE_W = 150.0
    PLATE_D = 84.0
    PLATE_T = 3.0

    # 1. Definer alle rektangulære udskæringer (xmin, xmax, ymin, ymax)
    cutouts = []

    # A. 12 MX Switches
    sw_w = 14.2
    sw_h = 14.2
    for r in range(3):
        y_c = 22.95 + r * 19.05
        for c in range(4):
            x_c = 16.0 + c * 19.05
            cutouts.append((x_c - sw_w/2, x_c + sw_w/2, y_c - sw_h/2, y_c + sw_h/2))

    # B. OLED Display Bezel Window
    oled_xc = 117.5
    oled_yc = 42.0
    oled_w = 26.0
    oled_h = 14.0
    cutouts.append((oled_xc - oled_w/2, oled_xc + oled_w/2, oled_yc - oled_h/2, oled_yc + oled_h/2))

    # C. 4 Potentiometer huller
    pot_coords = [
        (103.0, 61.05),
        (132.0, 61.05),
        (103.0, 22.95),
        (132.0, 22.95),
    ]
    pot_hole_size = 7.5
    for px, py in pot_coords:
        cutouts.append((px - pot_hole_size/2, px + pot_hole_size/2, py - pot_hole_size/2, py + pot_hole_size/2))

    # D. 4 Hjørneskruehuller
    screw_coords = [(5.5, 5.5), (144.5, 5.5), (5.5, 78.5), (144.5, 78.5)]
    screw_hole_size = 3.4
    for sx, sy in screw_coords:
        cutouts.append((sx - screw_hole_size/2, sx + screw_hole_size/2, sy - screw_hole_size/2, sy + screw_hole_size/2))

    # 2. Partitioner pladen i et 2D grid baseret på alle udskæringsgrænser
    x_splits = {0.0, PLATE_W}
    y_splits = {0.0, PLATE_D}

    for x0, x1, y0, y1 in cutouts:
        x_splits.add(round(x0, 4))
        x_splits.add(round(x1, 4))
        y_splits.add(round(y0, 4))
        y_splits.add(round(y1, 4))

    x_list = sorted(list(x_splits))
    y_list = sorted(list(y_splits))
    num_x = len(x_list) - 1
    num_y = len(y_list) - 1

    # Bestem for hver celle i gridet om den er solid eller et hul
    solid = [[True for _ in range(num_y)] for _ in range(num_x)]

    for i in range(num_x):
        x0, x1 = x_list[i], x_list[i+1]
        mid_x = (x0 + x1) / 2.0
        for j in range(num_y):
            y0, y1 = y_list[j], y_list[j+1]
            mid_y = (y0 + y1) / 2.0

            for cx0, cx1, cy0, cy1 in cutouts:
                if (cx0 <= mid_x <= cx1) and (cy0 <= mid_y <= cy1):
                    solid[i][j] = False
                    break

    # 3. Tilføj KUN udvendige flader
    for i in range(num_x):
        x0, x1 = x_list[i], x_list[i+1]
        for j in range(num_y):
            if not solid[i][j]:
                continue
            y0, y1 = y_list[j], y_list[j+1]

            # Hjørner for denne celle
            v000 = mesh.add_vertex(x0, y0, 0.0)
            v100 = mesh.add_vertex(x1, y0, 0.0)
            v110 = mesh.add_vertex(x1, y1, 0.0)
            v010 = mesh.add_vertex(x0, y1, 0.0)

            v001 = mesh.add_vertex(x0, y0, PLATE_T)
            v101 = mesh.add_vertex(x1, y0, PLATE_T)
            v111 = mesh.add_vertex(x1, y1, PLATE_T)
            v011 = mesh.add_vertex(x0, y1, PLATE_T)

            # Bund (altid udad mod -Z)
            mesh.add_quad(v000, v010, v110, v100)
            # Top (altid udad mod +Z)
            mesh.add_quad(v001, v101, v111, v011)

            # Front (-Y): tilføj kun hvis nabo mod -Y er tom/udenfor
            if j == 0 or not solid[i][j-1]:
                mesh.add_quad(v000, v100, v101, v001)

            # Bagside (+Y): tilføj kun hvis nabo mod +Y er tom/udenfor
            if j == num_y - 1 or not solid[i][j+1]:
                mesh.add_quad(v110, v010, v011, v111)

            # Venstre (-X): tilføj kun hvis nabo mod -X er tom/udenfor
            if i == 0 or not solid[i-1][j]:
                mesh.add_quad(v010, v000, v001, v011)

            # Højre (+X): tilføj kun hvis nabo mod +X er tom/udenfor
            if i == num_x - 1 or not solid[i+1][j]:
                mesh.add_quad(v100, v110, v111, v101)

    return mesh


def build_bottom_case():
    """
    Bygger bunden af kabinettet (Bottom Enclosure):
      - 150.0 x 84.0 x 24.0 mm ydermål
      - 2.5 mm vægtykkelse
      - 2.5 mm bundtykkelse
      - USB-port udskæring på bagvæggen (14.0 x 7.5 mm)
      - 4 indvendige hjørnetårne med skruehuller til montering
      - ESP32 monterings-forhøjninger i bunden
    Garanterer 100% manifold, lukket geometri.
    """
    mesh = Mesh()
    BOX_W = 150.0
    BOX_D = 84.0
    BOX_H = 24.0
    WALL = 2.5
    FLOOR = 2.5

    # USB udskæring på bagvæg
    usb_x0 = 47.0
    usb_x1 = 61.0
    usb_z_top = FLOOR + 7.5

    # 4 hjørnetårne (10x10 mm) med 3.4 mm skruehul
    towers = [
        (WALL, WALL + 9.0, WALL, WALL + 9.0, 5.5, 5.5),
        (BOX_W - WALL - 9.0, BOX_W - WALL, WALL, WALL + 9.0, 144.5, 5.5),
        (WALL, WALL + 9.0, BOX_D - WALL - 9.0, BOX_D - WALL, 5.5, 78.5),
        (BOX_W - WALL - 9.0, BOX_W - WALL, BOX_D - WALL - 9.0, BOX_D - WALL, 144.5, 78.5),
    ]

    # ESP32 skinner i bunden
    esp_x = 54.0
    esp_y = 48.0

    # 1. Saml alle opdelinger i X, Y, Z
    x_splits = {0.0, WALL, BOX_W - WALL, BOX_W, usb_x0, usb_x1}
    y_splits = {0.0, WALL, BOX_D - WALL, BOX_D}
    z_splits = {0.0, FLOOR, FLOOR + 3.0, usb_z_top, BOX_H}

    for tx0, tx1, ty0, ty1, hcx, hcy in towers:
        hw = 1.7
        for val in [tx0, tx1, hcx - hw, hcx + hw]:
            x_splits.add(round(val, 4))
        for val in [ty0, ty1, hcy - hw, hcy + hw]:
            y_splits.add(round(val, 4))

    # ESP32 skinner
    for val in [esp_x - 14.0, esp_x - 11.0, esp_x + 11.0, esp_x + 14.0]:
        x_splits.add(round(val, 4))
    for val in [esp_y - 25.0, esp_y + 25.0]:
        y_splits.add(round(val, 4))

    x_list = sorted(list(x_splits))
    y_list = sorted(list(y_splits))
    z_list = sorted(list(z_splits))

    nx = len(x_list) - 1
    ny = len(y_list) - 1
    nz = len(z_list) - 1

    # 3D grid over solid tilstand
    solid = [[[False for _ in range(nz)] for _ in range(ny)] for _ in range(nx)]

    for i in range(nx):
        x0, x1 = x_list[i], x_list[i+1]
        mx = (x0 + x1) / 2.0
        for j in range(ny):
            y0, y1 = y_list[j], y_list[j+1]
            my = (y0 + y1) / 2.0
            for k in range(nz):
                z0, z1 = z_list[k], z_list[k+1]
                mz = (z0 + z1) / 2.0

                is_solid = False

                # A. Bundplade (z < FLOOR)
                if mz <= FLOOR:
                    is_solid = True

                # B. Ydervægge (z > FLOOR)
                elif mz <= BOX_H:
                    # Venstre væg
                    if mx <= WALL:
                        is_solid = True
                    # Højre væg
                    elif mx >= BOX_W - WALL:
                        is_solid = True
                    # Front væg
                    elif my <= WALL:
                        is_solid = True
                    # Bagvæg (med USB port hul)
                    elif my >= BOX_D - WALL:
                        if usb_x0 <= mx <= usb_x1 and mz <= usb_z_top:
                            is_solid = False # USB port hul
                        else:
                            is_solid = True

                    # C. Hjørnetårne (z op til BOX_H)
                    if not is_solid:
                        for tx0, tx1, ty0, ty1, hcx, hcy in towers:
                            if tx0 <= mx <= tx1 and ty0 <= my <= ty1:
                                hw = 1.7
                                # Er det inde i skruehullet?
                                if (hcx - hw <= mx <= hcx + hw) and (hcy - hw <= my <= hcy + hw):
                                    is_solid = False
                                else:
                                    is_solid = True
                                break

                    # D. ESP32 forhøjnings-skinner i bunden (FLOOR til FLOOR+3.0)
                    if not is_solid and mz <= FLOOR + 3.0:
                        if (esp_y - 25.0 <= my <= esp_y + 25.0):
                            if (esp_x - 14.0 <= mx <= esp_x - 11.0) or (esp_x + 11.0 <= mx <= esp_x + 14.0):
                                is_solid = True

                solid[i][j][k] = is_solid

    # 2. Generer kun overflade-flader (hvor solid møder tomhed)
    for i in range(nx):
        x0, x1 = x_list[i], x_list[i+1]
        for j in range(ny):
            y0, y1 = y_list[j], y_list[j+1]
            for k in range(nz):
                if not solid[i][j][k]:
                    continue
                z0, z1 = z_list[k], z_list[k+1]

                v000 = mesh.add_vertex(x0, y0, z0)
                v100 = mesh.add_vertex(x1, y0, z0)
                v110 = mesh.add_vertex(x1, y1, z0)
                v010 = mesh.add_vertex(x0, y1, z0)

                v001 = mesh.add_vertex(x0, y0, z1)
                v101 = mesh.add_vertex(x1, y0, z1)
                v111 = mesh.add_vertex(x1, y1, z1)
                v011 = mesh.add_vertex(x0, y1, z1)

                # Bund (-Z)
                if k == 0 or not solid[i][j][k-1]:
                    mesh.add_quad(v000, v010, v110, v100)

                # Top (+Z)
                if k == nz - 1 or not solid[i][j][k+1]:
                    mesh.add_quad(v001, v101, v111, v011)

                # Front (-Y)
                if j == 0 or not solid[i][j-1][k]:
                    mesh.add_quad(v000, v100, v101, v001)

                # Bagside (+Y)
                if j == ny - 1 or not solid[i][j+1][k]:
                    mesh.add_quad(v110, v010, v011, v111)

                # Venstre (-X)
                if i == 0 or not solid[i-1][j][k]:
                    mesh.add_quad(v010, v000, v001, v011)

                # Højre (+X)
                if i == nx - 1 or not solid[i+1][j][k]:
                    mesh.add_quad(v100, v110, v111, v101)

    return mesh


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    top_stl = os.path.join(script_dir, "streamdeck_top_plate.stl")
    bottom_stl = os.path.join(script_dir, "streamdeck_bottom_case.stl")

    print("Genererer 3D modeller til ESP32 Wireless Stream Deck...")

    top_mesh = build_top_plate()
    top_mesh.write_stl(top_stl, "StreamdeckTopPlate")

    bottom_mesh = build_bottom_case()
    bottom_mesh.write_stl(bottom_stl, "StreamdeckBottomCase")

    print("\nFærdig! STL-filer genereret i:", script_dir)


if __name__ == "__main__":
    main()
