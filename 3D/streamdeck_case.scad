// ===================================================================
// ESP32 Wireless Stream Deck & Audio Mixer - Angled Wedge Enclosure
// OpenSCAD Parametric Model
// ===================================================================

// Hvad vil du vise? ("both", "top", "bottom")
part = "both"; // ["both", "top", "bottom"]

// --- Hoveddimensioner for Wedge Kabinet ---
case_width       = 152.0;
case_depth       = 86.0;
front_height     = 18.0;  // Lav forkant mod brugeren
back_height      = 50.0;  // Høj bagkant (giver ~22 graders ergonomisk vinkel)
wall_thickness   = 3.0;
floor_thickness  = 2.5;
plate_recess     = 3.0;   // Hvor dybt toppladen er planforsænket
shelf_width      = 4.0;   // Hyldebredde som toppladen hviler på

// --- Dimensioner for Toppladen ---
plate_width      = 145.0;
plate_length     = 85.0;
plate_thickness  = 3.0;

// --- MX Taster (4 kolonner x 3 rækker) ---
switch_hole_size = 14.2;   // 14.0 mm nominel, 14.2 mm giver ideelt snap-fit i 3D print
switch_pitch_x   = 19.05;  // Standard 1U tastatur pitch
switch_pitch_y   = 19.05;
keys_origin_x    = 16.0;   // Første kolonne center
keys_origin_y    = 23.45;  // Første række center

// --- Potentiometre (4 stk) ---
pot_hole_d       = 7.5;    // M7 gevind med frigang
pot_x1           = 100.0;
pot_x2           = 128.0;
pot_y_top        = 61.55;  // På linje med øverste tasterække
pot_y_bottom     = 23.45;  // På linje med nederste tasterække

// --- 0.96" OLED Display (SSD1306) ---
oled_center_x    = 114.0;
oled_center_y    = 42.50;  // På linje med midterste tasterække
oled_window_w    = 26.0;
oled_window_h    = 14.0;

// --- Montage & Skruer ---
screw_hole_d     = 3.4;    // M3 gennemgående hul
corner_inset_x   = 5.5;
corner_inset_y   = 5.5;

// --- USB Port (på bagvæggen) ---
usb_w            = 14.0;
usb_h            = 8.0;
usb_x            = case_width / 2; // Centreret bagpå

$fn = 40;

// Beregnet hældningsvinkel
tilt_angle = atan2(back_height - front_height, case_depth);

// ===================================================================
// MODULER
// ===================================================================

// Kile-polyeder (hollow eller solid)
module wedge_poly(w, d, hf, hb) {
    polyhedron(
        points = [
            [0, 0, 0],   [w, 0, 0],   [w, d, 0],   [0, d, 0],   // 0, 1, 2, 3 (Bund)
            [0, 0, hf],  [w, 0, hf],  [w, d, hb],  [0, d, hb]   // 4, 5, 6, 7 (Skrå top)
        ],
        faces = [
            [0, 3, 2, 1], // Bund
            [0, 1, 5, 4], // Front
            [1, 2, 6, 5], // Højre
            [2, 3, 7, 6], // Bagside
            [3, 0, 4, 7], // Venstre
            [4, 5, 6, 7]  // Skrå overside
        ]
    );
}

module top_plate() {
    difference() {
        // Hovedplade
        cube([plate_width, plate_length, plate_thickness]);

        // 12x MX Switch huller
        for (r = [0 : 2]) {
            for (c = [0 : 3]) {
                translate([
                    keys_origin_x + c * switch_pitch_x - switch_hole_size / 2,
                    keys_origin_y + r * switch_pitch_y - switch_hole_size / 2,
                    -1
                ])
                cube([switch_hole_size, switch_hole_size, plate_thickness + 2]);
            }
        }

        // 4x Potentiometer huller
        translate([pot_x1, pot_y_top, -1])    cylinder(d = pot_hole_d, h = plate_thickness + 2);
        translate([pot_x2, pot_y_top, -1])    cylinder(d = pot_hole_d, h = plate_thickness + 2);
        translate([pot_x1, pot_y_bottom, -1]) cylinder(d = pot_hole_d, h = plate_thickness + 2);
        translate([pot_x2, pot_y_bottom, -1]) cylinder(d = pot_hole_d, h = plate_thickness + 2);

        // OLED skærm vindue
        translate([
            oled_center_x - oled_window_w / 2,
            oled_center_y - oled_window_h / 2,
            -1
        ])
        cube([oled_window_w, oled_window_h, plate_thickness + 2]);

        // 4x Hjørneskruehuller
        translate([corner_inset_x, corner_inset_y, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([plate_width - corner_inset_x, corner_inset_y, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([corner_inset_x, plate_length - corner_inset_y, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([plate_width - corner_inset_x, plate_length - corner_inset_y, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
    }
}

module bottom_wedge_case() {
    slope = (back_height - front_height) / case_depth;

    difference() {
        // Ydre kile
        wedge_poly(case_width, case_depth, front_height, back_height);

        // Forsænket hylde til toppladen
        translate([wall_thickness, wall_thickness, 0]) {
            wedge_poly(
                case_width - 2 * wall_thickness,
                case_depth - 2 * wall_thickness,
                front_height + wall_thickness * slope - plate_recess,
                back_height - wall_thickness * slope - plate_recess
            );
        }

        // Indvendigt hulrum ned til bunden
        inner_margin = wall_thickness + shelf_width;
        translate([inner_margin, inner_margin, floor_thickness]) {
            cube([
                case_width - 2 * inner_margin,
                case_depth - 2 * inner_margin,
                back_height + 10
            ]);
        }

        // USB-port åbning på bagvæggen
        translate([usb_x - usb_w / 2, case_depth - wall_thickness - 1, floor_thickness])
            cube([usb_w, wall_thickness + 2, usb_h]);
    }
}

// ===================================================================
// RENDER VALG
// ===================================================================

if (part == "both") {
    // Viser kassen samlet med toppladen placeret skråt i kabinettet
    color("DimGray") bottom_wedge_case();
    
    // Toppladen placeret og vinklet ned i hylden
    translate([
        wall_thickness + (case_width - 2*wall_thickness - plate_width)/2,
        wall_thickness * cos(tilt_angle),
        front_height - plate_recess + 4.0 // Hævet lidt for visualisering
    ])
    rotate([tilt_angle, 0, 0])
    color("SteelBlue")
    top_plate();

} else if (part == "top") {
    // Printes fladt på byggepladen
    top_plate();
} else if (part == "bottom") {
    // Printes stående på sin flade bund uden supports
    bottom_wedge_case();
}
