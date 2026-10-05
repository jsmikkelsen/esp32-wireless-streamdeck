// ===================================================================
// ESP32 Wireless Stream Deck & Audio Mixer - Parametric Enclosure
// OpenSCAD Model
// ===================================================================

// Hvad vil du vise? ("both", "top", "bottom")
part = "both"; // ["both", "top", "bottom"]

// --- Hoveddimensioner ---
case_width       = 150.0;
case_depth       = 84.0;
case_height      = 24.0;
wall_thickness   = 2.5;
floor_thickness  = 2.5;
plate_thickness  = 3.0;

// --- MX Taster (4 kolonner x 3 rækker) ---
switch_hole_size = 14.2;   // 14.0 mm nominel, 14.2 mm giver ideelt snap-fit i 3D print
switch_pitch_x   = 19.05;  // Standard 1U tastatur pitch
switch_pitch_y   = 19.05;
keys_origin_x    = 16.0;   // Første kolonne center
keys_origin_y    = 22.95;  // Første række center

// --- Potentiometre (4 stk) ---
pot_hole_d       = 7.5;    // M7 gevind med frigang
pot_x1           = 103.0;
pot_x2           = 132.0;
pot_y_top        = 61.05;  // På linje med øverste tasterække
pot_y_bottom     = 22.95;  // På linje med nederste tasterække

// --- 0.96" OLED Display (SSD1306) ---
oled_center_x    = 117.5;
oled_center_y    = 42.0;   // På linje med midterste tasterække
oled_window_w    = 26.0;
oled_window_h    = 14.0;

// --- Montage & Skruer ---
screw_hole_d     = 3.2;    // M3 gennemgående hul
tower_size       = 9.5;
tower_screw_d    = 2.8;    // M3 pilot hul i tårne
corner_inset     = 5.5;

// --- USB Port ---
usb_w            = 14.0;
usb_h            = 7.5;
usb_x            = 54.0;   // Centreret i forhold til ESP32

$fn = 40;

// ===================================================================
// MODULER
// ===================================================================

module top_plate() {
    difference() {
        // Hovedplade
        cube([case_width, case_depth, plate_thickness]);

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
        translate([corner_inset, corner_inset, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([case_width - corner_inset, corner_inset, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([corner_inset, case_depth - corner_inset, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
        translate([case_width - corner_inset, case_depth - corner_inset, -1]) cylinder(d = screw_hole_d, h = plate_thickness + 2);
    }
}

module bottom_case() {
    difference() {
        union() {
            // Yderboks
            cube([case_width, case_depth, case_height]);

            // 4 indvendige hjørnetårne
            translate([wall_thickness, wall_thickness, floor_thickness])
                cube([tower_size, tower_size, case_height - floor_thickness]);
            translate([case_width - wall_thickness - tower_size, wall_thickness, floor_thickness])
                cube([tower_size, tower_size, case_height - floor_thickness]);
            translate([wall_thickness, case_depth - wall_thickness - tower_size, floor_thickness])
                cube([tower_size, tower_size, case_height - floor_thickness]);
            translate([case_width - wall_thickness - tower_size, case_depth - wall_thickness - tower_size, floor_thickness])
                cube([tower_size, tower_size, case_height - floor_thickness]);

            // ESP32 skinner / standoffs på bunden
            translate([usb_x - 14.0, 25.0, floor_thickness])
                cube([3.0, 48.0, 3.0]);
            translate([usb_x + 11.0, 25.0, floor_thickness])
                cube([3.0, 48.0, 3.0]);
        }

        // Hovedhulrum
        translate([wall_thickness, wall_thickness, floor_thickness])
            cube([
                case_width - 2 * wall_thickness,
                case_depth - 2 * wall_thickness,
                case_height + 1
            ]);

        // 4x Skruehuller i hjørnetårne
        translate([corner_inset, corner_inset, floor_thickness])
            cylinder(d = tower_screw_d, h = case_height);
        translate([case_width - corner_inset, corner_inset, floor_thickness])
            cylinder(d = tower_screw_d, h = case_height);
        translate([corner_inset, case_depth - corner_inset, floor_thickness])
            cylinder(d = tower_screw_d, h = case_height);
        translate([case_width - corner_inset, case_depth - corner_inset, floor_thickness])
            cylinder(d = tower_screw_d, h = case_height);

        // USB-port åbning på bagvæggen
        translate([usb_x - usb_w / 2, case_depth - wall_thickness - 1, floor_thickness])
            cube([usb_w, wall_thickness + 2, usb_h]);
    }
}

// ===================================================================
// RENDER VALG
// ===================================================================

if (part == "both") {
    // Viser kassen samlet (top svævende lidt over bunden)
    color("DimGray") bottom_case();
    color("SteelBlue") translate([0, 0, case_height + 6]) top_plate();
} else if (part == "top") {
    top_plate();
} else if (part == "bottom") {
    bottom_case();
}
