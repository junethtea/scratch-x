# Scratch-X

**Fast, lightweight scratch geometry creation for QGIS.**

Scratch-X is a free QGIS plugin for quickly creating **Line, LineString routes, Point, Polygon, and customizable Shapes** directly on the QGIS map canvas, with live measurements, flexible styling, categorized symbols, and multiple export formats.

> **Current version: 2.1.3**

---

## Quick Navigation

<p align="center">
  <a href="#features"><strong>Features</strong></a> ·
  <a href="#geometry-tools"><strong>Geometry</strong></a> ·
  <a href="#point-symbol-library"><strong>Symbols</strong></a> ·
  <a href="#measurement-tools"><strong>Measurements</strong></a> ·
  <a href="#save-geometry"><strong>Save</strong></a> ·
  <a href="#google-earth"><strong>Google Earth</strong></a> ·
  <a href="#installation"><strong>Installation</strong></a> ·
  <a href="#support-development"><strong>Support</strong></a>
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/QGIS-3.34%20%7C%204.2-589632?style=for-the-badge&logo=qgis&logoColor=white" alt="QGIS 3.34 and 4.2"></a>
  <a href="#save-geometry"><img src="https://img.shields.io/badge/Formats-SHP%20%7C%20TAB%20%7C%20KML%20%7C%20GeoJSON-4C8BF5?style=for-the-badge" alt="Supported formats"></a>
  <a href="#features"><img src="https://img.shields.io/badge/Interface-English%20%7C%20Indonesia-8B5CF6?style=for-the-badge" alt="Bilingual interface"></a>
</p>

---

## What's New in v2.1.3

- **Automatic edge-pan while drawing** — the map automatically moves when the cursor reaches the canvas edge, allowing continuous drawing without switching to the QGIS Pan/Hand tool.
- **Edge-pan works while Scratch-X is minimized** — the active drawing session remains available while the floating window is minimized.
- **Automatic file saving** — when a File Path is selected, each completed geometry is written to the selected datasource automatically. Manual **Save Layer Edits** is not required.
- **Expanded attribute information** — saved features include geometry-related values such as longitude, latitude, distance, radius, or area where applicable.
- **Automatic layer-name labeling** — generated layers can display their layer name directly on the map using compact black text with a yellow buffer.
- **Improved Point labeling** — Point labels are positioned above the point symbol so the symbol remains visible.

---

<p align="center">
  <a href="https://github.com/junethtea/scratch-x"><strong>View Source Code & Repository</strong></a>
</p>

## Features

- **Line**
  - 2-point Line drawing
  - LineString / Route drawing
  - Dynamic segment distance
  - Dynamic route distance
  - Cumulative distance across completed lines in the current drawing session
  - `ESC` cancels the active drawing

- **Point**
  - Categorized point-symbol library
  - Quick symbol samples directly in the main panel
  - Extended **More Symbols** library
  - Symbol categories covering GIS, Telecom, Utilities, Infrastructure, Transportation, Safety, and other practical use cases
  - Custom SVG symbol loading
  - Load one symbol or multiple symbols at once
  - Adjustable symbol size

- **Polygon**
  - Free polygon drawing
  - Live area measurement
  - Area displayed in a dedicated measurement panel

- **Shape**
  - Circle
  - Square
  - Triangle
  - Pentagon
  - Hexagon
  - Octagon
  - Trapezoid
  - Heart
  - Ellipse
  - Rectangle
  - Semicircle
  - Star
  - Parallelogram
  - Crescent
  - Circle provides a live radius measurement while drawing

- **Styling**
  - Fill color
  - Border color
  - Transparency
  - Line width
  - Multiple line styles
  - Point symbol size
  - Custom color selection

- **Output**
  - ESRI Shapefile (`.shp`)
  - MapInfo TAB (`.tab`)
  - KML (`.kml`)
  - GeoJSON (`.geojson`)
  - Temporary QGIS layer workflow

- **Workflow**
  - Floating, modeless window
  - Resizable interface
  - Persistent user settings
  - Temporary Layer reset for each new geometry
  - Clear Scratch-X temporary layers
  - English / Indonesian interface
  - Help / How To
  - About dialog

---

## Geometry Tools

### Line

Choose between:

- **Line (2-point)** — create a single straight segment.
- **LineString (Route)** — create a multi-vertex route.

During drawing, Scratch-X provides live distance information.

For LineString routes, the distance continues from the first vertex through every subsequent vertex. Completed line distances can also be accumulated during the current layer session.

Press **`ESC`** at any time to cancel the current drawing.

### Point

Select a point symbol and click the QGIS map canvas to place it.

The main panel shows a compact set of frequently used symbols. Select **More Symbols...** to browse the larger categorized library.

Custom SVG symbols can also be loaded when the built-in library does not contain the symbol you need.

### Polygon

Click vertices on the map to build a polygon. Scratch-X calculates and displays the area dynamically.

The measurement panel reports the **Area** for the current polygon.

### Shape

The Shape tool provides predefined geometric forms without requiring a separate button for every shape.

Available shapes:

`Circle` · `Square` · `Triangle` · `Pentagon` · `Hexagon` · `Octagon` · `Trapezoid` · `Heart` · `Ellipse` · `Rectangle` · `Semicircle` · `Star` · `Parallelogram` · `Crescent`

For **Circle**, the radius is displayed dynamically while the circle is being created.

---

## Point Symbol Library

Scratch-X includes a categorized symbol library designed for practical GIS and field-work scenarios.

Example categories include:

- Basic
- GIS / Survey
- Telecom
- Utilities
- Infrastructure
- Transportation
- Safety / Facility

The main window intentionally displays only a compact sample of symbols.

Click **More Symbols...** to open the extended library, select a category, browse the available symbols, and choose the symbol you want to use.

### Custom Symbols

If your required symbol is not included:

1. Open **More Symbols...**
2. Choose the custom-symbol option.
3. Load a single SVG file or multiple SVG files.
4. Select the imported symbol.
5. Use it directly in Scratch-X.

Custom symbol selections are persisted between sessions.

---

## Measurement Tools

Scratch-X provides live measurements while geometry is being created. Saved metric values use **meters** for linear measurements and **square meters** for area.

| Geometry | Measurement | Unit |
|---|---|---|
| Line | Segment distance | m |
| LineString | Route distance | m |
| Polygon | Area | m² |
| Circle | Radius | m |

Measurements are calculated using QGIS geometry/measurement functionality rather than relying on a simple screen-pixel approximation.

### Attribute Information

Saved Scratch-X features include a compact attribute table with geometry-related information. The available metric field depends on the geometry type:

| Field | Description |
|---|---|
| `id` | Feature ID |
| `name` | Layer/file name |
| `longitude` | Longitude in WGS84 |
| `latitude` | Latitude in WGS84 |
| `distance` | Line / LineString length in meters |
| `radius` | Circle radius in meters |
| `area` | Polygon / Shape area in square meters |
| `notes` | Optional notes field |

---

## Save Geometry

Scratch-X supports two save modes: **Temporary Layer** and **File Path**.

### Temporary Layer

If File Path is left as:

`Temporary Layer`

Scratch-X creates a QGIS memory layer. The geometry remains part of the current QGIS project and is not automatically written to a file.

### Save to File

When a File Path is selected before **Create Layer**:

1. Select the output format.
2. Click the folder button.
3. Select the destination file.
4. Click **Create Layer**.
5. Draw the geometry.
6. Finish the geometry.
7. Scratch-X automatically saves the completed geometry to the selected file.

Manual **Save Layer Edits** from the QGIS layer context menu is not required.

Supported formats:

| Format | Extension |
|---|---|
| ESRI Shapefile | `.shp` |
| MapInfo TAB | `.tab` |
| Keyhole Markup Language | `.kml` |
| GeoJSON | `.geojson` |

### Save Behavior

Each completed geometry is automatically written to the selected datasource. The output path is intentionally **not carried over to the next geometry**. After **Create Layer**, Scratch-X resets the next operation to:

`Temporary Layer`

This prevents an old file path from accidentally becoming the destination for a new geometry.

---

## Google Earth

KML output is designed to retain the visual intent of the Scratch-X geometry as closely as practical.

- Line and polygon colors are preserved.
- Point symbols are exported for use in Google Earth.
- KML coordinates are written for Google Earth's geographic coordinate system.
- Feature naming follows the output/layer naming workflow rather than generic `Point 1`, `Point 2`, etc.

For example:

```text
Test_ABC123.kml
```

is represented in Google Earth using:

```text
Test_ABC123
```

instead of:

```text
Point 1
```

---

## Automatic Layer Labels

Scratch-X automatically applies a compact layer-name label to created geometry.

- Label text uses the layer/file name.
- Text color: **black**.
- Text buffer: **yellow**.
- No rectangular label background is used.
- Point labels are positioned above the point symbol so the symbol remains visible.
- Line, Polygon, and Shape labels are positioned around the geometry center where supported by QGIS labeling.

## Persistent Settings

Scratch-X remembers user preferences between sessions, including:

- Interface language
- Fill color
- Border color
- Transparency
- Line width
- Line style
- Point symbol
- Symbol size
- Shape selection
- Line drawing mode
- Output format
- Custom symbol configuration
- Window size

The **output File Path is intentionally not persisted**.

This keeps a previously selected save location from becoming an accidental destination for a future geometry.

---

## Automatic Map Edge-Pan

While drawing a multi-step geometry, move the cursor toward the edge of the QGIS map canvas. Scratch-X automatically pans the map so drawing can continue without switching to the Hand/Pan tool.

- Left edge → map moves left
- Right edge → map moves right
- Top edge → map moves downward
- Bottom edge → map moves upward

The active drawing session remains available even when the Scratch-X floating window is minimized.

## Keyboard

| Key | Action |
|---|---|
| `ESC` | Cancel the active drawing tool |

---

## User Interface

Scratch-X uses a compact floating window so it can remain open while the user works on the QGIS map canvas.

<img width="640" height="922" alt="image" src="https://github.com/user-attachments/assets/2fc21c97-2bd2-4218-a74c-5671071de87e" />


*Scratch-X main interface — a compact floating workspace for fast geometry creation, styling, measurement, and saving.*

The interface is designed around three main areas:

```text
1. GEOMETRY TYPE
   Line · Point · Polygon · Shape

2. STYLE
   Colors · Transparency · Width · Line Style
   Symbol / Shape options

3. SAVE GEOMETRY
   Format · File Path
```

The window can be resized and minimized independently of the main QGIS interface.

---

## Installation

### From the QGIS Plugin Manager

1. Open QGIS.
2. Go to **Plugins → Manage and Install Plugins...**
3. Search for **Scratch-X**.
4. Install the plugin.
5. Open Scratch-X from the QGIS Plugins menu or toolbar.

### Manual Installation

1. Download the Scratch-X plugin ZIP.
2. Open QGIS.
3. Go to **Plugins → Manage and Install Plugins...**
4. Select **Install from ZIP**.
5. Select the downloaded Scratch-X ZIP.
6. Enable Scratch-X after installation.

### Compatibility

Scratch-X targets:

- **QGIS 3.34**
- **QGIS 4.2**

The plugin includes Qt compatibility handling for the supported QGIS environments.

---

## Basic Workflow

```text
Select Geometry
      ↓
Configure Style
      ↓
Choose Symbol / Shape
      ↓
Choose Output Format
      ↓
Temporary Layer
      or
Select Save Path
      ↓
Create Layer
      ↓
Draw on QGIS Canvas
      ↓
Finish / Cancel with ESC
      ↓
Auto-save when a File Path is selected
```

---

## Why Scratch-X?

Scratch-X is intended for situations where you need to quickly sketch geometry on a QGIS map without going through a full layer-creation workflow every time.

Typical uses include:

- Quick GIS markup
- RF / Telecom planning
- Site planning
- Route sketching
- Coverage or service-area visualization
- Field survey preparation
- Infrastructure planning
- Temporary map annotation
- Rapid spatial analysis
- Exporting quick geometry to KML or other GIS formats

---

## Support Development

Scratch-X is **free for public use**.

If Scratch-X is useful to your work and you would like to support continued development, you can contribute through:

<p align="center">
  <a href="https://www.paypal.me/junjunan81">
    <img src="https://img.shields.io/badge/Support%20via-PayPal-0070BA?style=for-the-badge&logo=paypal&logoColor=white" alt="Support via PayPal">
  </a>
  <a href="https://buymeacoffee.com/juneth">
    <img src="https://img.shields.io/badge/Buy%20Me-a%20Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=000000" alt="Buy Me a Coffee">
  </a>
  <a href="https://saweria.co/juneth">
    <img src="https://img.shields.io/badge/Support%20via-Saweria-2ECC71?style=for-the-badge" alt="Support via Saweria">
  </a>
</p>

---

## Author

**Jujun Junaedi**

RF Engineer · RF Post-Processing · GIS & QGIS Enthusiast

Email: [jujun.junaedi@outlook.com](mailto:jujun.junaedi@outlook.com)

---

## License

Scratch-X is released under the **GNU General Public License v3.0 (GPL-3.0)**.

See the repository's [`LICENSE`](https://github.com/junethtea/scratch-x/blob/main/LICENSE) file for the complete license text.

---

<p align="center">
  <strong>Scratch-X</strong><br>
  Fast geometry. Simple workflow. Built for QGIS.
</p>

© 2025–2026 Jujun Junaedi
