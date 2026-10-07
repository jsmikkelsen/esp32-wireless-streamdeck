#!/usr/bin/env python3
"""
3D Model Generator for ESP32 Wireless Stream Deck & Audio Mixer (Angled Wedge Enclosure)
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
        key = (round(x, 4), round(y, 4), round(z, 4))
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
        # Two counter-clockwise triangles: (v0, v1, v2) and (v0, v2, v3)
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


def build_top_plate():
    """
    Bygger top-pladen som passer ned i det vinklede kabinet:
      - 145.0 x 85.0 x 3.0 mm
      - 12x MX switches (14.2 x 14.2 mm) i 4x3 matrix til venstre
      - 4x Potentiometer huller (7.5 mm) til højre (2 øverst, 2 nederst)
      - 1x 0.96" OLED Display vindue (26.0 x 14.0 mm) i midten til højre
      - 4x Hjørneskruer (M3, 3.4 mm)
    100% manifold, lukket geometri.
    """
    mesh = Mesh()
    PLATE_W = 145.0
    PLATE_D = 85.0
    PLATE_T = 3.0

    cutouts = []

    # 1. 12 MX Switches (4 kolonner x 3 rækker)
    sw_w, sw_h = 14.2, 14.2
    for r in range(3):
        yc = 23.45 + r * 19.05
        for c in range(4):
            xc = 16.0 + c * 19.05
            cutouts.append((xc - sw_w/2, xc + sw_w/2, yc - sw_h/2, yc + sw_h/2))

    # 2. OLED Display vindue
    oled_xc, oled_yc = 114.0, 42.50
    cutouts.append((oled_xc - 13.0, oled_xc + 13.0, oled_yc - 7.0, oled_yc + 7.0))

    # 3. 4 Potentiometre
    pot_coords = [
        (100.0, 61.55), # Pot 0 (top-venstre)
        (128.0, 61.55), # Pot 1 (top-højre)
        (100.0, 23.45), # Pot 2 (bund-venstre)
        (128.0, 23.45), # Pot 3 (bund-højre)
    ]
    for px, py in pot_coords:
        cutouts.append((px - 3.75, px + 3.75, py - 3.75, py + 3.75))

    # 4. 4 Hjørneskruehuller
    screw_coords = [(5.5, 5.5), (139.5, 5.5), (5.5, 79.5), (139.5, 79.5)]
    for sx, sy in screw_coords:
        cutouts.append((sx - 1.7, sx + 1.7, sy - 1.7, sy + 1.7))

    # Partitioner i et 2D grid
    x_splits = {0.0, PLATE_W}
    y_splits = {0.0, PLATE_D}
    for x0, x1, y0, y1 in cutouts:
        x_splits.add(round(x0, 4))
        x_splits.add(round(x1, 4))
        y_splits.add(round(y0, 4))
        y_splits.add(round(y1, 4))

    x_list = sorted(list(x_splits))
    y_list = sorted(list(y_splits))
    nx, ny = len(x_list) - 1, len(y_list) - 1

    solid = [[True for _ in range(ny)] for _ in range(nx)]
    for i in range(nx):
        x0, x1 = x_list[i], x_list[i+1]
        mx = (x0 + x1) / 2.0
        for j in range(ny):
            y0, y1 = y_list[j], y_list[j+1]
            my = (y0 + y1) / 2.0
            for cx0, cx1, cy0, cy1 in cutouts:
                if (cx0 <= mx <= cx1) and (cy0 <= my <= cy1):
                    solid[i][j] = False
                    break

    # Generer flader
    for i in range(nx):
        x0, x1 = x_list[i], x_list[i+1]
        for j in range(ny):
            if not solid[i][j]:
                continue
            y0, y1 = y_list[j], y_list[j+1]

            v000 = mesh.add_vertex(x0, y0, 0.0)
            v100 = mesh.add_vertex(x1, y0, 0.0)
            v110 = mesh.add_vertex(x1, y1, 0.0)
            v010 = mesh.add_vertex(x0, y1, 0.0)

            v001 = mesh.add_vertex(x0, y0, PLATE_T)
            v101 = mesh.add_vertex(x1, y0, PLATE_T)
            v111 = mesh.add_vertex(x1, y1, PLATE_T)
            v011 = mesh.add_vertex(x0, y1, PLATE_T)

            # Bund (-Z) & Top (+Z)
            mesh.add_quad(v000, v010, v110, v100)
            mesh.add_quad(v001, v101, v111, v011)

            # Ydervægge / hulvægge
            if j == 0 or not solid[i][j-1]:
                mesh.add_quad(v000, v100, v101, v001)
            if j == ny - 1 or not solid[i][j+1]:
                mesh.add_quad(v110, v010, v011, v111)
            if i == 0 or not solid[i-1][j]:
                mesh.add_quad(v010, v000, v001, v011)
            if i == nx - 1 or not solid[i+1][j]:
                mesh.add_quad(v100, v110, v111, v101)

    return mesh


def build_wedge_case():
    """
    Bygger det vinklede wedge-kabinet (Stream Deck stil som i referencebilledet):
      - Fodprint: 152.0 x 86.0 mm
      - Forreste højde: 18.0 mm (lav ergonomisk forkant)
      - Bagerste højde: 50.0 mm (høj bagkant)
      - Hældningsvinkel: ~22 grader mod brugeren
      - Vægtykkelse: 3.0 mm
      - Bundtykkelse: 2.5 mm
      - Indvendig hylde for planforsænkning af toppladen (3.0 mm forsænkning)
      - USB-port udskæring på bagvæggen (14.0 x 8.0 mm)
    100% manifold, lukket geometri.
    """
    mesh = Mesh()
    W = 152.0
    D = 86.0
    Hf = 18.0
    Hb = 50.0
    Tw = 3.0
    Tf = 2.5
    Tp = 3.0       # Forsænkning til toppladen
    Sw = 4.0       # Hyldebredde
    Z_MID = 15.0   # Interface-plan mellem flad bundsektion og vinklet topsektion

    slope = (Hb - Hf) / D
    def z_top(y): return Hf + y * slope
    def z_shelf(y): return z_top(y) - Tp

    usb_x0, usb_x1 = W/2 - 7.0, W/2 + 7.0

    x_splits = sorted(list({
        0.0, Tw, Tw + Sw,
        usb_x0, usb_x1,
        W - Tw - Sw, W - Tw, W
    }))
    y_splits = sorted(list({
        0.0, Tw, Tw + Sw,
        D - Tw - Sw, D - Tw, D
    }))
    z_splits_lower = [0.0, Tf, Tf + 8.0, Z_MID]

    nx = len(x_splits) - 1
    ny = len(y_splits) - 1
    nz_lower = len(z_splits_lower) - 1

    # 1. Nedre sektion (0 til Z_MID)
    solid_lower = [[[False for _ in range(nz_lower)] for _ in range(ny)] for _ in range(nx)]

    for i in range(nx):
        x0, x1 = x_splits[i], x_splits[i+1]
        mx = (x0 + x1) / 2.0
        for j in range(ny):
            y0, y1 = y_splits[j], y_splits[j+1]
            my = (y0 + y1) / 2.0

            is_outer_wall = (mx <= Tw or mx >= W - Tw or my <= Tw or my >= D - Tw)
            is_shelf_col = not is_outer_wall and (mx <= Tw + Sw or mx >= W - Tw - Sw or my <= Tw + Sw or my >= D - Tw - Sw)
            is_usb = (my >= D - Tw) and (usb_x0 <= mx <= usb_x1)

            for k in range(nz_lower):
                z0, z1 = z_splits_lower[k], z_splits_lower[k+1]
                mz = (z0 + z1) / 2.0

                if mz <= Tf:
                    solid_lower[i][j][k] = True
                else:
                    if is_outer_wall:
                        if is_usb and (Tf <= mz <= Tf + 8.0):
                            solid_lower[i][j][k] = False # USB port hul
                        else:
                            solid_lower[i][j][k] = True
                    elif is_shelf_col:
                        solid_lower[i][j][k] = True
                    else:
                        solid_lower[i][j][k] = False

    # 2. Øvre sektion (Z_MID til z_top(y))
    # 0 = tom (hulrum), 1 = hylde, 2 = ydervæg
    type_upper = [[0 for _ in range(ny)] for _ in range(nx)]
    for i in range(nx):
        x0, x1 = x_splits[i], x_splits[i+1]
        mx = (x0 + x1) / 2.0
        for j in range(ny):
            y0, y1 = y_splits[j], y_splits[j+1]
            my = (y0 + y1) / 2.0
            if (mx <= Tw or mx >= W - Tw or my <= Tw or my >= D - Tw):
                type_upper[i][j] = 2
            elif (mx <= Tw + Sw or mx >= W - Tw - Sw or my <= Tw + Sw or my >= D - Tw - Sw):
                type_upper[i][j] = 1

    # --- Generer nedre sektion ---
    for i in range(nx):
        x0, x1 = x_splits[i], x_splits[i+1]
        for j in range(ny):
            y0, y1 = y_splits[j], y_splits[j+1]
            for k in range(nz_lower):
                if not solid_lower[i][j][k]:
                    continue
                z0, z1 = z_splits_lower[k], z_splits_lower[k+1]

                v000 = mesh.add_vertex(x0, y0, z0)
                v100 = mesh.add_vertex(x1, y0, z0)
                v110 = mesh.add_vertex(x1, y1, z0)
                v010 = mesh.add_vertex(x0, y1, z0)

                v001 = mesh.add_vertex(x0, y0, z1)
                v101 = mesh.add_vertex(x1, y0, z1)
                v111 = mesh.add_vertex(x1, y1, z1)
                v011 = mesh.add_vertex(x0, y1, z1)

                if k == 0 or not solid_lower[i][j][k-1]:
                    mesh.add_quad(v000, v010, v110, v100)

                if k == nz_lower - 1:
                    if type_upper[i][j] == 0:
                        mesh.add_quad(v001, v101, v111, v011)
                elif not solid_lower[i][j][k+1]:
                    mesh.add_quad(v001, v101, v111, v011)

                if j == 0 or not solid_lower[i][j-1][k]:
                    mesh.add_quad(v000, v100, v101, v001)
                if j == ny - 1 or not solid_lower[i][j+1][k]:
                    mesh.add_quad(v110, v010, v011, v111)
                if i == 0 or not solid_lower[i-1][j][k]:
                    mesh.add_quad(v010, v000, v001, v011)
                if i == nx - 1 or not solid_lower[i+1][j][k]:
                    mesh.add_quad(v100, v110, v111, v101)

    # --- Generer øvre sektion ---
    def get_upper_top(i, j, y):
        if i < 0 or i >= nx or j < 0 or j >= ny:
            return Z_MID
        t = type_upper[i][j]
        if t == 2:
            return z_top(y)
        elif t == 1:
            return z_shelf(y)
        return Z_MID

    for i in range(nx):
        x0, x1 = x_splits[i], x_splits[i+1]
        for j in range(ny):
            t = type_upper[i][j]
            if t == 0:
                continue
            y0, y1 = y_splits[j], y_splits[j+1]

            zt0 = get_upper_top(i, j, y0)
            zt1 = get_upper_top(i, j, y1)

            vt00 = mesh.add_vertex(x0, y0, zt0)
            vt10 = mesh.add_vertex(x1, y0, zt0)
            vt11 = mesh.add_vertex(x1, y1, zt1)
            vt01 = mesh.add_vertex(x0, y1, zt1)
            mesh.add_quad(vt00, vt10, vt11, vt01) # Skrå overflade (+Z)

            # Væg mod front (-Y)
            n_zt0 = get_upper_top(i, j-1, y0)
            if zt0 > n_zt0:
                v_b0 = mesh.add_vertex(x0, y0, n_zt0)
                v_b1 = mesh.add_vertex(x1, y0, n_zt0)
                mesh.add_quad(v_b0, v_b1, vt10, vt00)

            # Væg mod bagside (+Y)
            n_zt1 = get_upper_top(i, j+1, y1)
            if zt1 > n_zt1:
                v_b0 = mesh.add_vertex(x0, y1, n_zt1)
                v_b1 = mesh.add_vertex(x1, y1, n_zt1)
                mesh.add_quad(v_b1, v_b0, vt01, vt11)

            # Væg mod venstre (-X)
            n_zt0_l = get_upper_top(i-1, j, y0)
            n_zt1_l = get_upper_top(i-1, j, y1)
            if zt0 > n_zt0_l or zt1 > n_zt1_l:
                v_b0 = mesh.add_vertex(x0, y0, n_zt0_l)
                v_b1 = mesh.add_vertex(x0, y1, n_zt1_l)
                mesh.add_quad(v_b0, vt00, vt01, v_b1)

            # Væg mod højre (+X)
            n_zt0_r = get_upper_top(i+1, j, y0)
            n_zt1_r = get_upper_top(i+1, j, y1)
            if zt0 > n_zt0_r or zt1 > n_zt1_r:
                v_b0 = mesh.add_vertex(x1, y0, n_zt0_r)
                v_b1 = mesh.add_vertex(x1, y1, n_zt1_r)
                mesh.add_quad(v_b0, v_b1, vt11, vt10)

    return mesh


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    top_stl = os.path.join(script_dir, "streamdeck_top_plate.stl")
    bottom_stl = os.path.join(script_dir, "streamdeck_bottom_case.stl")

    print("Genererer 3D modeller til ESP32 Wireless Stream Deck (Wedge Enclosure)...")

    top_mesh = build_top_plate()
    top_mesh.write_stl(top_stl, "StreamdeckTopPlate")

    bottom_mesh = build_wedge_case()
    bottom_mesh.write_stl(bottom_stl, "StreamdeckWedgeCase")

    print("\nFærdig! STL-filer genereret i:", script_dir)


if __name__ == "__main__":
    main()
