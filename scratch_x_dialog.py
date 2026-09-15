"""Scratch-X — public QGIS scratch geometry tool.

Designed for QGIS 3.x / 4.x and kept Qt5/Qt6 compatible.
"""
import os
import math
import html

from qgis.PyQt.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QSlider, QComboBox,
    QFileDialog, QMessageBox, QFrame, QButtonGroup,
    QDoubleSpinBox, QColorDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QStackedWidget, QToolButton,
    QAbstractItemView, QSizePolicy, QScrollArea, QToolTip, QApplication, QStyle, QSpinBox
)
from qgis.PyQt.QtGui import (
    QColor, QPixmap, QPainter, QPen, QBrush, QPainterPath,
    QPolygonF, QCursor, QFont, QIcon, QDesktopServices, QImage
)
try:
    from qgis.PyQt.QtSvg import QSvgRenderer
except Exception:
    QSvgRenderer = None

from qgis.PyQt.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSize, QUrl, QSettings, QEvent, QMetaType, QByteArray

from qgis.core import (
    QgsVectorLayer, QgsProject, QgsField,
    QgsVectorFileWriter, QgsSimpleMarkerSymbolLayer,
    QgsMarkerSymbol, QgsSvgMarkerSymbolLayer, QgsLineSymbol, QgsFillSymbol,
    QgsSingleSymbolRenderer, QgsFeature, QgsGeometry,
    QgsPointXY, QgsWkbTypes, QgsEditFormConfig, QgsDistanceArea, QgsCoordinateReferenceSystem, QgsCoordinateTransform
)
from qgis.gui import QgsMapTool, QgsRubberBand

BG      = "#12131A"
PANEL   = "#1A1B26"
CARD    = "#20212E"
HOV     = "#2A2B3D"
BORDER  = "#2D2E42"
TEXT    = "#E2E8F0"
MUTED   = "#64748B"
DIM     = "#94A3B8"
PRI     = "#6366F1"
A_L     = "#4ADE80"
A_P     = "#60A5FA"
A_PL    = "#FBBF24"
A_S     = "#A78BFA"

QC_FILL = ["#4ADE80", "#60A5FA", "#FBBF24", "#F472B6"]
QC_BDR  = ["#FFFFFF", "#94A3B8", "#EF4444", "#000000"]

# Built-in symbols. More Symbols exposes the complete library below.
SYMBOL_CATEGORIES = {
    "Basic": [
        ("circle", "Circle", "Lingkaran"), ("square", "Square", "Kotak"),
        ("diamond", "Diamond", "Diamond"), ("tri_u", "Triangle", "Segitiga"),
        ("penta", "Pentagon", "Pentagon"), ("hexa", "Hexagon", "Hexagon"),
        ("octa", "Octagon", "Oktagon"), ("star", "Star", "Bintang"),
        ("cross", "Cross", "Plus"), ("cross_x", "X", "Silang"),
        ("arrow", "Arrow", "Panah"), ("heart", "Heart", "Hati"),
        ("semi", "Semicircle", "Setengah Lingkaran"),
    ],
    "GIS / Survey": [
        ("pin", "Map Pin", "Pin Peta"), ("target", "Survey Target", "Target Survey"),
        ("benchmark", "Benchmark", "Benchmark"), ("waypoint", "Waypoint", "Waypoint"),
        ("flag", "Flag", "Bendera"), ("crosshair", "Crosshair", "Bidik"),
        ("camera", "Camera", "Kamera"), ("info", "Information", "Informasi"),
    ],
    "Telecom": [
        ("tower", "Cell Tower", "Tower BTS"), ("antenna", "Antenna", "Antena"),
        ("sector", "Sector", "Sektor"), ("smallcell", "Small Cell", "Small Cell"),
        ("repeater", "Repeater", "Repeater"), ("microwave", "Microwave", "Microwave"),
        ("satellite", "Satellite", "Satelit"), ("wifi", "Wi-Fi", "Wi-Fi"),
        ("router", "Router", "Router"), ("server", "Server", "Server"),
    ],
    "Utilities": [
        ("powerpole", "Power Pole", "Tiang Listrik"), ("substation", "Substation", "Gardu"),
        ("transformer", "Transformer", "Trafo"), ("water", "Water", "Air"),
        ("watertank", "Water Tank", "Tangki Air"), ("pipeline", "Pipeline", "Pipa"),
        ("gas", "Gas", "Gas"), ("hydrant", "Hydrant", "Hydrant"),
    ],
    "Infrastructure": [
        ("building", "Building", "Gedung"), ("house", "House", "Rumah"),
        ("factory", "Factory", "Pabrik"), ("warehouse", "Warehouse", "Gudang"),
        ("bridge", "Bridge", "Jembatan"), ("tunnel", "Tunnel", "Terowongan"),
        ("road", "Road", "Jalan"), ("parking", "Parking", "Parkir"),
    ],
    "Transportation": [
        ("car", "Car", "Mobil"), ("bus", "Bus", "Bus"), ("truck", "Truck", "Truk"),
        ("train", "Train", "Kereta"), ("motorcycle", "Motorcycle", "Motor"),
        ("ship", "Ship", "Kapal"), ("airplane", "Airplane", "Pesawat"),
    ],
    "Safety / Facility": [
        ("hospital", "Hospital", "Rumah Sakit"), ("school", "School", "Sekolah"),
        ("police", "Police", "Polisi"), ("fire", "Fire Station", "Pemadam"),
        ("cctv", "CCTV", "CCTV"), ("emergency", "Emergency", "Darurat"),
        ("warning", "Warning", "Peringatan"), ("check", "Check", "Centang"),
    ],
}

# First 12 are shown directly in the main panel.
QUICK_SYMBOLS = [x[0] for x in SYMBOL_CATEGORIES["Basic"][:12]]
ALL_SYMBOLS = []
for _cat, _items in SYMBOL_CATEGORIES.items():
    for _sid, _en, _id in _items:
        ALL_SYMBOLS.append((_sid, _en, _id, _cat))

# QGIS simple-marker mapping where an exact marker exists.
SIMPLE_MARKERS = {
    "circle": "Circle", "square": "Square", "diamond": "Diamond",
    "tri_u": "Triangle", "penta": "Pentagon", "hexa": "Hexagon",
    "octa": "Octagon", "star": "Star", "cross": "Cross",
    "cross_x": "Cross2", "arrow": "Arrow", "heart": "Heart",
    "semi": "SemiCircle",
}

LINE_STYLES = [
    ("solid", "Solid", Qt.SolidLine, "solid", []),
    ("dash", "Dash", Qt.DashLine, "dash", [6, 3]),
    ("dot", "Dot", Qt.DotLine, "dot", [1, 3]),
    ("dashdot", "Dash-Dot", Qt.DashDotLine, "dash dot", [6, 2, 1, 2]),
    ("dashdotdot", "Dash-Dot-Dot", Qt.DashDotDotLine, "dash dot dot", [6, 2, 1, 2, 1, 2]),
    ("longdash", "Long Dash", Qt.DashLine, "dash", [12, 4]),
]

SHAPES = [
    ("circle", "Circle", "Lingkaran"), ("square", "Square", "Kotak"),
    ("triangle", "Triangle", "Segitiga"), ("pentagon", "Pentagon", "Pentagon"),
    ("hexagon", "Hexagon", "Hexagon"), ("octagon", "Octagon", "Oktagon"),
    ("trapezoid", "Trapezoid", "Trapesium"), ("heart", "Heart", "Hati"),
    ("ellipse", "Ellipse", "Elips"), ("rectangle", "Rectangle", "Persegi Panjang"),
    ("semicircle", "Semicircle", "Setengah Lingkaran"), ("star", "Star", "Bintang"),
    ("parallelogram", "Parallelogram", "Jajar Genjang"), ("crescent", "Crescent", "Bulan Sabit"),
]

CIRCLE_SEGMENTS = 72

# QGIS 3.38+ / QGIS 4.x uses QMetaType for QgsField types.
# Keep the enum lookup Qt5/Qt6 compatible while avoiding the deprecated
# QgsField(..., QVariant.Type) constructor.
try:
    _QTYPE_INT = QMetaType.Type.Int
    _QTYPE_STRING = QMetaType.Type.QString
except AttributeError:
    _QTYPE_INT = QMetaType.Int
    _QTYPE_STRING = QMetaType.QString

# Central Qt5/Qt6 enum compatibility layer. UI/UX is intentionally unchanged
# from the v3.1.7 baseline.
_QT6 = hasattr(Qt, "MouseButton")
if _QT6:
    QT_LEFT = Qt.MouseButton.LeftButton
    QT_RIGHT = Qt.MouseButton.RightButton
else:
    QT_LEFT = Qt.LeftButton
    QT_RIGHT = Qt.RightButton

if _QT6:
    QT_SOLID = Qt.PenStyle.SolidLine
    QT_DASH = Qt.PenStyle.DashLine
    QT_DOT = Qt.PenStyle.DotLine
    QT_DASHDOT = Qt.PenStyle.DashDotLine
    QT_DASHDOTDOT = Qt.PenStyle.DashDotDotLine
    QT_CUSTOM_DASH = Qt.PenStyle.CustomDashLine
    QT_ROUND_CAP = Qt.PenCapStyle.RoundCap
    QT_ROUND_JOIN = Qt.PenJoinStyle.RoundJoin
    QT_NO_BRUSH = Qt.BrushStyle.NoBrush
    QT_NO_PEN = Qt.PenStyle.NoPen
    QT_TRANSPARENT = Qt.GlobalColor.transparent
    QT_POINTING = Qt.CursorShape.PointingHandCursor
    QT_CROSS = Qt.CursorShape.CrossCursor
    QT_ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    QT_HORIZONTAL = Qt.Orientation.Horizontal
    QT_TOOLTIP_WINDOW = Qt.WindowType.ToolTip
    QT_FRAMELESS_WINDOW = Qt.WindowType.FramelessWindowHint
    QT_WA_TRANSPARENT = Qt.WidgetAttribute.WA_TransparentForMouseEvents
    QT_WINDOW = Qt.WindowType.Window
    QT_WINDOW_TITLE = Qt.WindowType.WindowTitleHint
    QT_WINDOW_SYSTEM_MENU = Qt.WindowType.WindowSystemMenuHint
    QT_WINDOW_MINIMIZE = Qt.WindowType.WindowMinimizeButtonHint
    QT_WINDOW_CLOSE = Qt.WindowType.WindowCloseButtonHint
    QT_USER_ROLE = Qt.ItemDataRole.UserRole
    QT_ESC = Qt.Key.Key_Escape
    QFRAME_HLINE = QFrame.Shape.HLine
    QFRAME_NOFRAME = QFrame.Shape.NoFrame
    QSP_EXPANDING = QSizePolicy.Policy.Expanding
    QSP_FIXED = QSizePolicy.Policy.Fixed
    QABSTRACT_SINGLE = QAbstractItemView.SelectionMode.SingleSelection
    QLIST_ICON_MODE = QListWidget.ViewMode.IconMode
    QLIST_ADJUST = QListWidget.ResizeMode.Adjust
    QDBB_OK = QDialogButtonBox.StandardButton.Ok
    QDBB_CANCEL = QDialogButtonBox.StandardButton.Cancel
    QMB_OK = QMessageBox.StandardButton.Ok
    QSTYLE_DIR_OPEN = QStyle.StandardPixmap.SP_DirOpenIcon
    QPAINTER_ANTIALIASING = QPainter.RenderHint.Antialiasing
else:
    QT_SOLID = Qt.SolidLine
    QT_DASH = Qt.DashLine
    QT_DOT = Qt.DotLine
    QT_DASHDOT = Qt.DashDotLine
    QT_DASHDOTDOT = Qt.DashDotDotLine
    QT_CUSTOM_DASH = Qt.CustomDashLine
    QT_ROUND_CAP = Qt.RoundCap
    QT_ROUND_JOIN = Qt.RoundJoin
    QT_NO_BRUSH = Qt.NoBrush
    QT_NO_PEN = Qt.NoPen
    QT_TRANSPARENT = Qt.transparent
    QT_POINTING = Qt.PointingHandCursor
    QT_CROSS = Qt.CrossCursor
    QT_ALIGN_CENTER = Qt.AlignCenter
    QT_HORIZONTAL = Qt.Horizontal
    QT_TOOLTIP_WINDOW = Qt.ToolTip
    QT_FRAMELESS_WINDOW = Qt.FramelessWindowHint
    QT_WA_TRANSPARENT = Qt.WA_TransparentForMouseEvents
    QT_WINDOW = Qt.Window
    QT_WINDOW_TITLE = Qt.WindowTitleHint
    QT_WINDOW_SYSTEM_MENU = Qt.WindowSystemMenuHint
    QT_WINDOW_MINIMIZE = Qt.WindowMinimizeButtonHint
    QT_WINDOW_CLOSE = Qt.WindowCloseButtonHint
    QT_USER_ROLE = Qt.UserRole
    QT_ESC = Qt.Key_Escape
    QFRAME_HLINE = QFrame.HLine
    QFRAME_NOFRAME = QFrame.NoFrame
    QSP_EXPANDING = QSizePolicy.Expanding
    QSP_FIXED = QSizePolicy.Fixed
    QABSTRACT_SINGLE = QAbstractItemView.SingleSelection
    QLIST_ICON_MODE = QListWidget.IconMode
    QLIST_ADJUST = QListWidget.Adjust
    QDBB_OK = QDialogButtonBox.Ok
    QDBB_CANCEL = QDialogButtonBox.Cancel
    QMB_OK = QMessageBox.Ok
    QSTYLE_DIR_OPEN = QStyle.SP_DirOpenIcon
    QPAINTER_ANTIALIASING = QPainter.Antialiasing


def _qcolor_alpha(c, alpha):
    out = QColor(c)
    out.setAlpha(alpha)
    return out


def _fmt_distance(meters):
    if meters < 1000:
        return f"{meters:.1f} m"
    return f"{meters / 1000.0:.3f} km"


def _fmt_area(square_meters):
    if square_meters < 10000:
        return f"{square_meters:.1f} m²"
    if square_meters < 1000000:
        return f"{square_meters / 10000.0:.3f} ha"
    return f"{square_meters / 1000000.0:.3f} km²"


def _measurement_table(rows):
    parts=["<table cellspacing='0' cellpadding='1' style='border-collapse:collapse;'>"]
    for label,value in rows:
        parts.append(f"<tr><td style='color:{DIM};padding:2px 8px 2px 4px;'>{_xml_text(label)}</td><td style='color:{TEXT};font-weight:700;padding:2px 4px;text-align:right;'>{_xml_text(value)}</td></tr>")
    parts.append("</table>")
    return "".join(parts)


def _kml_color(c):
    c=QColor(c)
    return f"{c.alpha():02x}{c.blue():02x}{c.green():02x}{c.red():02x}"


def _xml_text(value):
    return html.escape(str(value), quote=True)


def _safe_asset_name(value):
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(value))


def draw_symbol(p, sid, rect, fill=QColor(A_P), stroke=QColor("white")):
    """Draw a consistent preview icon for the symbol picker and quick grid."""
    p.save(); p.setRenderHint(QPAINTER_ANTIALIASING)
    cx, cy = rect.center().x(), rect.center().y()
    r = min(rect.width(), rect.height()) * 0.34
    p.setBrush(QBrush(fill)); p.setPen(QPen(stroke, max(1.2, r * 0.13), QT_SOLID, QT_ROUND_CAP, QT_ROUND_JOIN))

    if sid == "circle": p.drawEllipse(QPointF(cx, cy), r, r)
    elif sid == "square": p.drawRect(QRectF(cx-r, cy-r, 2*r, 2*r))
    elif sid == "diamond": p.drawPolygon(QPolygonF([QPointF(cx,cy-r*1.25),QPointF(cx+r,cy),QPointF(cx,cy+r*1.25),QPointF(cx-r,cy)]))
    elif sid == "tri_u": p.drawPolygon(QPolygonF([QPointF(cx,cy-r*1.25),QPointF(cx+r*1.1,cy+r*.8),QPointF(cx-r*1.1,cy+r*.8)]))
    elif sid in ("penta", "hexa", "octa"):
        n = {"penta":5,"hexa":6,"octa":8}[sid]; pts=QPolygonF()
        for i in range(n):
            a=-math.pi/2+i*2*math.pi/n; pts.append(QPointF(cx+r*1.15*math.cos(a),cy+r*1.15*math.sin(a)))
        p.drawPolygon(pts)
    elif sid == "star":
        pts=QPolygonF()
        for i in range(10):
            a=-math.pi/2+i*math.pi/5; rr=r*1.25 if i%2==0 else r*.52
            pts.append(QPointF(cx+rr*math.cos(a),cy+rr*math.sin(a)))
        p.drawPolygon(pts)
    elif sid == "cross":
        t=r*.30; path=QPainterPath(); path.addRect(cx-t,cy-r,2*t,2*r); path.addRect(cx-r,cy-t,2*r,2*t); p.drawPath(path)
    elif sid == "cross_x":
        p.setBrush(QT_NO_BRUSH); p.setPen(QPen(fill,r*.34,QT_SOLID,QT_ROUND_CAP)); p.drawLine(QPointF(cx-r,cy-r),QPointF(cx+r,cy+r)); p.drawLine(QPointF(cx+r,cy-r),QPointF(cx-r,cy+r))
    elif sid == "arrow":
        p.drawPolygon(QPolygonF([QPointF(cx,cy-r*1.35),QPointF(cx+r,cy),QPointF(cx+r*.35,cy),QPointF(cx+r*.35,cy+r*1.1),QPointF(cx-r*.35,cy+r*1.1),QPointF(cx-r*.35,cy),QPointF(cx-r,cy)]))
    elif sid == "heart":
        s=r*.85; path=QPainterPath(); path.moveTo(cx,cy+s*1.25); path.cubicTo(cx-s*2.0,cy,cx-s*1.9,cy-s*1.55,cx,cy-s*.45); path.cubicTo(cx+s*1.9,cy-s*1.55,cx+s*2.0,cy,cx,cy+s*1.25); p.drawPath(path)
    elif sid == "semi":
        path=QPainterPath(); path.moveTo(cx-r,cy); path.arcTo(QRectF(cx-r,cy-r,2*r,2*r),0,180); path.closeSubpath(); p.drawPath(path)
    elif sid == "pin":
        path=QPainterPath(); path.moveTo(cx,cy+r*1.45); path.cubicTo(cx-r*1.5,cy-r*.2,cx-r,cy-r*1.2,cx,cy-r*1.2); path.cubicTo(cx+r,cy-r*1.2,cx+r*1.5,cy-r*.2,cx,cy+r*1.45); p.drawPath(path); p.setBrush(QColor(CARD)); p.drawEllipse(QPointF(cx,cy-r*.45),r*.28,r*.28)
    elif sid in ("target","crosshair"):
        p.setBrush(QT_NO_BRUSH); p.drawEllipse(QPointF(cx,cy),r,r); p.drawEllipse(QPointF(cx,cy),r*.48,r*.48); p.drawLine(QPointF(cx-r*1.25,cy),QPointF(cx+r*1.25,cy)); p.drawLine(QPointF(cx,cy-r*1.25),QPointF(cx,cy+r*1.25))
    elif sid == "benchmark":
        p.drawPolygon(QPolygonF([QPointF(cx-r,cy+r),QPointF(cx+r,cy+r),QPointF(cx+r*.65,cy-r*.6),QPointF(cx-r*.65,cy-r*.6)])); p.drawLine(QPointF(cx,cy-r*.6),QPointF(cx,cy+r*.75))
    elif sid == "waypoint":
        p.drawEllipse(QPointF(cx,cy),r*.9,r*.9); p.drawLine(QPointF(cx,cy-r*1.25),QPointF(cx,cy+r*1.25)); p.drawLine(QPointF(cx-r*1.25,cy),QPointF(cx+r*1.25,cy))
    elif sid == "flag":
        p.setBrush(QT_NO_BRUSH); p.drawLine(QPointF(cx-r*.65,cy-r*1.3),QPointF(cx-r*.65,cy+r*1.25)); p.setBrush(fill); p.drawPolygon(QPolygonF([QPointF(cx-r*.6,cy-r*1.2),QPointF(cx+r*1.15,cy-r*.65),QPointF(cx-r*.6,cy-r*.1)]))
    elif sid == "camera":
        p.drawRoundedRect(QRectF(cx-r*1.2,cy-r*.55,2.4*r,1.35*r),3,3); p.drawEllipse(QPointF(cx,cy),r*.38,r*.38)
    elif sid == "info":
        p.drawEllipse(QPointF(cx,cy),r,r); p.setBrush(stroke); p.drawEllipse(QPointF(cx,cy-r*.45),r*.10,r*.10); p.drawRect(QRectF(cx-r*.1,cy-r*.1,r*.2,r*.75))
    elif sid in ("tower","antenna"):
        p.setBrush(QT_NO_BRUSH); p.drawLine(QPointF(cx,cy-r*1.2),QPointF(cx,cy+r*1.2)); p.drawLine(QPointF(cx,cy-r*1.1),QPointF(cx-r*.75,cy+r*1.2)); p.drawLine(QPointF(cx,cy-r*1.1),QPointF(cx+r*.75,cy+r*1.2)); p.drawLine(QPointF(cx-r*.8,cy+r*.75),QPointF(cx+r*.8,cy+r*.75)); p.drawArc(QRectF(cx-r*1.05,cy-r*1.15,2.1*r,1.0*r),25*16,130*16); p.drawArc(QRectF(cx-r*1.45,cy-r*1.5,2.9*r,1.45*r),25*16,130*16)
    elif sid == "sector":
        p.drawArc(QRectF(cx-r,cy-r,2*r,2*r),20*16,140*16); p.drawLine(QPointF(cx,cy),QPointF(cx+r*.95,cy-r*.35)); p.drawLine(QPointF(cx,cy),QPointF(cx+r*.8,cy+r*.65))
    elif sid == "smallcell":
        p.drawRoundedRect(QRectF(cx-r*.7,cy-r*.8,1.4*r,1.6*r),2,2); p.drawArc(QRectF(cx-r*1.2,cy-r*1.3,2.4*r,1.4*r),30*16,120*16)
    elif sid == "repeater":
        p.drawRect(QRectF(cx-r*.6,cy-r*.55,1.2*r,1.1*r)); p.drawLine(QPointF(cx-r*.35,cy-r*1.2),QPointF(cx-r*.35,cy-r*.55)); p.drawLine(QPointF(cx+r*.35,cy-r*1.2),QPointF(cx+r*.35,cy-r*.55))
    elif sid == "microwave":
        p.drawEllipse(QPointF(cx,cy),r*.72,r*.72); p.drawLine(QPointF(cx,cy),QPointF(cx+r*.95,cy-r*.35)); p.drawLine(QPointF(cx,cy),QPointF(cx+r*.95,cy+r*.35))
    elif sid == "satellite":
        p.drawEllipse(QPointF(cx,cy),r*.35,r*.35); p.drawLine(QPointF(cx,cy),QPointF(cx-r*.85,cy-r*.65)); p.drawLine(QPointF(cx,cy),QPointF(cx+r*.85,cy-r*.65)); p.drawLine(QPointF(cx,cy),QPointF(cx,cy+r))
    elif sid == "wifi":
        p.setBrush(QT_NO_BRUSH); p.drawArc(QRectF(cx-r,cy-r*.65,2*r,1.4*r),25*16,130*16); p.drawArc(QRectF(cx-r*.62,cy-r*.25,1.24*r,.9*r),25*16,130*16); p.setBrush(fill); p.drawEllipse(QPointF(cx,cy+r*.5),r*.14,r*.14)
    elif sid in ("router","server"):
        p.drawRoundedRect(QRectF(cx-r*1.15,cy-r*.55,2.3*r,1.1*r),3,3); p.drawLine(QPointF(cx-r*.65,cy-r*1.0),QPointF(cx-r*.65,cy-r*.55)); p.drawLine(QPointF(cx+r*.65,cy-r*1.0),QPointF(cx+r*.65,cy-r*.55))
    elif sid in ("powerpole","substation","transformer","hydrant","watertank","pipeline","gas"):
        p.drawRect(QRectF(cx-r*.55,cy-r*.65,1.1*r,1.3*r)); p.drawLine(QPointF(cx-r*.9,cy-r*.9),QPointF(cx+r*.9,cy-r*.9)); p.drawLine(QPointF(cx-r*.75,cy-r*.9),QPointF(cx-r*.75,cy-r*1.25)); p.drawLine(QPointF(cx+r*.75,cy-r*.9),QPointF(cx+r*.75,cy-r*1.25))
    elif sid in ("building","house","factory","warehouse"):
        p.drawRect(QRectF(cx-r,cy-r*.65,2*r,1.65*r)); p.drawPolygon(QPolygonF([QPointF(cx-r*1.1,cy-r*.65),QPointF(cx,cy-r*1.35),QPointF(cx+r*1.1,cy-r*.65)])); p.setBrush(QColor(CARD)); p.drawRect(QRectF(cx-r*.2,cy+r*.15,r*.4,r*.85))
    elif sid in ("bridge","tunnel","road","parking"):
        p.drawRoundedRect(QRectF(cx-r*1.2,cy-r*.65,2.4*r,1.3*r),4,4); p.setPen(QPen(QColor(CARD),max(2,r*.15))); p.drawLine(QPointF(cx-r*.8,cy),QPointF(cx+r*.8,cy))
    elif sid in ("car","bus","truck","motorcycle"):
        p.drawRoundedRect(QRectF(cx-r*1.2,cy-r*.45,2.4*r,.9*r),3,3); p.setBrush(QColor(CARD)); p.drawEllipse(QPointF(cx-r*.7,cy+r*.45),r*.22,r*.22); p.drawEllipse(QPointF(cx+r*.7,cy+r*.45),r*.22,r*.22)
    elif sid in ("train","ship","airplane"):
        p.drawLine(QPointF(cx-r*1.2,cy+r*.6),QPointF(cx+r*1.2,cy+r*.6)); p.drawPolygon(QPolygonF([QPointF(cx-r,cy),QPointF(cx+r,cy),QPointF(cx+r*.35,cy-r*.55),QPointF(cx-r*.35,cy-r*.55)]))
    elif sid in ("hospital","school","police","fire","cctv","emergency","warning","check"):
        p.drawRect(QRectF(cx-r,cy-r,2*r,2*r))
        if sid == "check":
            p.setBrush(QT_NO_BRUSH); p.setPen(QPen(stroke,r*.2,QT_SOLID,QT_ROUND_CAP)); p.drawLine(QPointF(cx-r*.6,cy),QPointF(cx-r*.1,cy+r*.55)); p.drawLine(QPointF(cx-r*.1,cy+r*.55),QPointF(cx+r*.75,cy-r*.55))
        elif sid == "warning":
            p.setBrush(fill); p.drawPolygon(QPolygonF([QPointF(cx,cy-r*1.15),QPointF(cx+r,cy+r*.9),QPointF(cx-r,cy+r*.9)])); p.setPen(QPen(stroke,r*.14)); p.drawLine(QPointF(cx,cy-r*.55),QPointF(cx,cy+r*.35))
        else:
            p.setBrush(QColor(CARD)); p.drawRect(QRectF(cx-r*.2,cy-r*.65,.4*r,1.3*r)); p.drawRect(QRectF(cx-r*.65,cy-r*.2,1.3*r,.4*r))
    else:
        p.drawEllipse(QPointF(cx,cy),r,r)
    p.restore()


def draw_shape_preview(p, sid, rect, fc=QColor(A_S), sc=QColor("white")):
    cx, cy = rect.center().x(), rect.center().y(); rx, ry = rect.width()*.36, rect.height()*.36
    p.save(); p.setRenderHint(QPAINTER_ANTIALIASING); p.setBrush(QBrush(fc)); p.setPen(QPen(sc, 1.8, QT_SOLID, QT_ROUND_CAP, QT_ROUND_JOIN))
    if sid == "circle": p.drawEllipse(QPointF(cx,cy),min(rx,ry),min(rx,ry))
    elif sid == "ellipse": p.drawEllipse(QPointF(cx,cy),rx,ry)
    elif sid == "rectangle": p.drawRect(QRectF(cx-rx,cy-ry,2*rx,2*ry))
    elif sid == "square":
        r=min(rx,ry); p.drawRect(QRectF(cx-r,cy-r,2*r,2*r))
    elif sid in ("triangle","pentagon","hexagon","octagon","star"):
        if sid == "triangle": n=3
        elif sid == "pentagon": n=5
        elif sid == "hexagon": n=6
        elif sid == "octagon": n=8
        else: n=10
        pts=QPolygonF()
        for i in range(n):
            a=-math.pi/2+i*2*math.pi/n
            rr=min(rx,ry)*(1.05 if sid!="star" or i%2==0 else .48)
            pts.append(QPointF(cx+rr*math.cos(a),cy+rr*math.sin(a)))
        p.drawPolygon(pts)
    elif sid == "trapezoid": p.drawPolygon(QPolygonF([QPointF(cx-rx*.55,cy-ry),QPointF(cx+rx*.55,cy-ry),QPointF(cx+rx,cy+ry),QPointF(cx-rx,cy+ry)]))
    elif sid == "parallelogram": p.drawPolygon(QPolygonF([QPointF(cx-rx*.55,cy-ry),QPointF(cx+rx,cy-ry),QPointF(cx+rx*.55,cy+ry),QPointF(cx-rx,cy+ry)]))
    elif sid == "semicircle":
        path=QPainterPath(); path.moveTo(cx-rx,cy+ry*.25); path.arcTo(QRectF(cx-rx,cy-ry,2*rx,2*ry),0,180); path.closeSubpath(); p.drawPath(path)
    elif sid == "heart":
        s=min(rx,ry)*.8; path=QPainterPath(); path.moveTo(cx,cy+s*1.25); path.cubicTo(cx-s*2,cy,cx-s*1.9,cy-s*1.55,cx,cy-s*.45); path.cubicTo(cx+s*1.9,cy-s*1.55,cx+s*2,cy,cx,cy+s*1.25); p.drawPath(path)
    elif sid == "crescent":
        path=QPainterPath(); path.moveTo(cx+rx*.15,cy-ry); path.arcTo(QRectF(cx-rx,cy-ry,2*rx,2*ry),90,180); path.arcTo(QRectF(cx-rx*.15,cy-ry,2*rx,2*ry),270,-180); path.closeSubpath(); p.drawPath(path)
    p.restore()


class Divider(QFrame):
    def __init__(self, p=None):
        super().__init__(p); self.setFrameShape(QFRAME_HLINE); self.setFixedHeight(1); self.setStyleSheet(f"background:{BORDER};border:none;")


def _custom_color_dialog(parent, initial, title):
    """Dark-theme-safe QColorDialog with readable labels and numeric fields."""
    dlg = QColorDialog(QColor(initial), parent)
    try:
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
    except Exception:
        dlg.setOption(QColorDialog.DontUseNativeDialog, True)
    dlg.setStyleSheet(
        f"QColorDialog{{background:{BG};color:{TEXT};}}"
        f"QColorDialog QLabel{{color:#FFFFFF;background:transparent;}}"
        f"QColorDialog QSpinBox,QColorDialog QDoubleSpinBox,QColorDialog QLineEdit{{background:{CARD};color:#FFFFFF;border:1px solid {BORDER};border-radius:4px;padding:3px;}}"
        f"QColorDialog QPushButton{{background:{CARD};color:#FFFFFF !important;border:1px solid {BORDER};border-radius:5px;padding:5px 10px;}}"
        f"QColorDialog QPushButton:enabled{{color:#FFFFFF !important;}}"
        f"QColorDialog QPushButton:hover{{background:{HOV};color:#FFFFFF !important;border-color:{PRI};}}"
        f"QColorDialog QDialogButtonBox QPushButton{{background:{CARD};color:#FFFFFF !important;min-width:64px;}}"
        f"QColorDialog QDialogButtonBox QPushButton:hover{{background:{HOV};color:#FFFFFF !important;}}"
        f"QColorDialog QGroupBox{{color:#FFFFFF;border:1px solid {BORDER};margin-top:8px;padding-top:8px;}}"
        f"QColorDialog QAbstractSpinBox{{color:#FFFFFF;}}"
        f"QColorDialog QToolTip{{background:{CARD};color:#FFFFFF;border:1px solid {BORDER};}}"
    )
    dlg.setWindowTitle(title)
    # QGIS 3.x / Qt5 can let the native button palette override the dialog
    # stylesheet. Apply the foreground directly to the actual OK/Cancel
    # buttons as a second layer of protection.
    try:
        bb = dlg.findChild(QDialogButtonBox)
        if bb:
            for btn in bb.buttons():
                btn.setStyleSheet(
                    f"QPushButton{{background:{CARD};color:#FFFFFF !important;border:1px solid {BORDER};border-radius:5px;padding:5px 10px;}}"
                    f"QPushButton:hover{{background:{HOV};color:#FFFFFF !important;border-color:{PRI};}}"
                )
    except Exception:
        pass
    return dlg.selectedColor() if dlg.exec() else QColor()


class QuickColorRow(QWidget):
    picked = pyqtSignal(QColor)
    def __init__(self, swatches, parent=None):
        super().__init__(parent); lay=QHBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(4)
        for hx in swatches:
            b=QPushButton(); b.setFixedSize(19,19); b.setCursor(QCursor(QT_POINTING)); b.setToolTip(hx)
            b.setStyleSheet(f"QPushButton{{background:{hx};border:2px solid rgba(255,255,255,.12);border-radius:4px;}}QPushButton:hover{{border:2px solid white;}}")
            b.clicked.connect(lambda _,h=hx:self.picked.emit(QColor(h))); lay.addWidget(b)
        lay.addStretch(); cb=QPushButton("Custom…"); cb.setFixedHeight(20); cb.setCursor(QCursor(QT_POINTING)); cb.setStyleSheet(f"QPushButton{{background:{PRI};border:none;border-radius:4px;color:white;font-size:9px;font-weight:600;padding:0 8px;}}QPushButton:hover{{background:#4F46E5;}}")
        cb.clicked.connect(self._custom); lay.addWidget(cb)
    def _custom(self):
        c=_custom_color_dialog(self, QColor("#FFFFFF"), "Warna Custom")
        if c.isValid(): self.picked.emit(c)


class ColorBlock(QWidget):
    changed=pyqtSignal(QColor)
    def __init__(self,label,init_hex,swatches,no_fill=False,parent=None):
        super().__init__(parent); self._c=QColor(init_hex); vl=QVBoxLayout(self); vl.setContentsMargins(0,0,0,0); vl.setSpacing(2)
        top=QHBoxLayout(); top.setSpacing(4); lbl=QLabel(label); lbl.setStyleSheet(f"color:{DIM};font-size:10px;font-weight:500;"); top.addWidget(lbl); top.addStretch()
        self._sw=QPushButton(); self._sw.setFixedSize(28,20); self._sw.setCursor(QCursor(QT_POINTING)); self._sw.clicked.connect(self._pick); self._refresh(); top.addWidget(self._sw)
        if no_fill:
            nf=QPushButton("∅"); nf.setFixedSize(22,22); nf.setToolTip("Tanpa fill / No fill"); nf.setStyleSheet(f"background:{CARD};border:1px solid {BORDER};border-radius:4px;color:{MUTED};font-size:11px;"); nf.clicked.connect(lambda:self._emit(QColor(0,0,0,0))); top.addWidget(nf)
        vl.addLayout(top); qr=QuickColorRow(swatches,self); qr.picked.connect(self._emit); vl.addWidget(qr)
    def _pick(self):
        c=_custom_color_dialog(self, self._c, "Warna Custom")
        if c.isValid(): self._emit(c)
    def _emit(self,c): self._c=c; self._refresh(); self.changed.emit(c)
    def _refresh(self):
        r,g,b,a=self._c.red(),self._c.green(),self._c.blue(),self._c.alpha()
        if a==0: self._sw.setStyleSheet(f"QPushButton{{background:transparent;border:2px dashed {MUTED};border-radius:4px;}}")
        else: self._sw.setStyleSheet(f"QPushButton{{background:rgba({r},{g},{b},{a});border:2px solid rgba(255,255,255,.2);border-radius:4px;}}QPushButton:hover{{border-color:white;}}")
    def color(self): return self._c


class SymBtn(QPushButton):
    def __init__(self, sid, tip, parent=None):
        super().__init__(parent)
        self.sid = sid
        self.svg_path = None
        self.setFixedSize(32, 30)
        self.setToolTip(tip)
        self.setCheckable(True)
        self.setCursor(QCursor(QT_POINTING))
        self.toggled.connect(lambda _: self.update())

    def set_symbol(self, sid, tip, svg_path=None):
        self.sid = sid
        self.svg_path = svg_path
        self.setToolTip(tip)
        self.update()

    def paintEvent(self, ev):
        p=QPainter(self)
        bg=QColor("#2A2B50") if self.isChecked() else (QColor(HOV) if self.underMouse() else QColor(CARD))
        p.fillRect(self.rect(),bg)
        bd=QColor(PRI if self.isChecked() or self.underMouse() else BORDER)
        p.setPen(QPen(bd,1.5));p.drawRoundedRect(QRectF(.5,.5,self.width()-1,self.height()-1),5,5)
        if self.svg_path and os.path.exists(self.svg_path):
            pm=QIcon(self.svg_path).pixmap(24,24)
            p.drawPixmap((self.width()-pm.width())//2,(self.height()-pm.height())//2,pm)
        else:
            draw_symbol(p,self.sid,QRectF(3,3,self.width()-6,self.height()-6),QColor(PRI if self.isChecked() else A_P),QColor("white" if self.isChecked() else DIM))
        p.end()


class ShapeBtn(QPushButton):
    def __init__(self,sid,tip,parent=None):
        super().__init__(parent); self.sid=sid; self.setFixedSize(32,28); self.setCheckable(True); self.setToolTip(tip); self.setCursor(QCursor(QT_POINTING)); self.toggled.connect(lambda _:self.update())
    def paintEvent(self,ev):
        p=QPainter(self); p.fillRect(self.rect(),QColor("#2A2B50") if self.isChecked() else (QColor(HOV) if self.underMouse() else QColor(CARD))); p.setPen(QPen(QColor(PRI if self.isChecked() or self.underMouse() else BORDER),1.5)); p.drawRoundedRect(QRectF(.5,.5,self.width()-1,self.height()-1),4,4); draw_shape_preview(p,self.sid,QRectF(3,3,self.width()-6,self.height()-6),QColor(PRI if self.isChecked() else A_S),QColor("white" if self.isChecked() else DIM)); p.end()


class GeomBtn(QPushButton):
    def __init__(self,name,icon,accent,parent=None):
        super().__init__(parent); self.icon=icon; self.accent=accent; self.setCheckable(True); self.setFixedHeight(44); self.setText(f"  {name}"); self.setCursor(QCursor(QT_POINTING)); self.toggled.connect(lambda _:self._s()); self._s()
    def _rgb(self,h): c=QColor(h); return f"{c.red()},{c.green()},{c.blue()}"
    def _s(self):
        if self.isChecked(): self.setStyleSheet(f"QPushButton{{background:rgba({self._rgb(self.accent)},.15);border:2px solid {self.accent};border-radius:7px;color:{TEXT};font-size:11px;font-weight:600;text-align:left;padding-left:10px;}}")
        else: self.setStyleSheet(f"QPushButton{{background:{CARD};border:1.5px solid {BORDER};border-radius:7px;color:{DIM};font-size:11px;font-weight:500;text-align:left;padding-left:10px;}}QPushButton:hover{{background:{HOV};border-color:rgba({self._rgb(self.accent)},.5);color:{TEXT};}}")
    def paintEvent(self,ev):
        super().paintEvent(ev); p=QPainter(self); p.setRenderHint(QPAINTER_ANTIALIASING); p.setPen(QColor(self.accent if self.isChecked() else MUTED)); f=QFont(); f.setPointSize(12); p.setFont(f); p.drawText(QRectF(self.width()-36,0,30,self.height()),QT_ALIGN_CENTER,self.icon); p.end()


class LsBtn(QPushButton):
    def __init__(self,nm,qt_s,qgis_s,dp,parent=None):
        super().__init__(parent); self.nm=nm; self.qt_s=qt_s; self.qgis_s=qgis_s; self.dp=dp; self.setFixedSize(64,20); self.setCheckable(True); self.setCursor(QCursor(QT_POINTING)); self.toggled.connect(lambda _:self.update())
    def paintEvent(self,ev):
        p=QPainter(self); chk=self.isChecked(); p.fillRect(self.rect(),QColor("#2A2B50") if chk else (QColor(HOV) if self.underMouse() else QColor(CARD))); p.setPen(QPen(QColor(PRI if chk else BORDER),1.5)); p.drawRoundedRect(QRectF(.5,.5,self.width()-1,self.height()-1),3,3); pen=QPen(QColor("white" if chk else DIM),1.8); 
        if self.dp: pen.setStyle(QT_CUSTOM_DASH); pen.setDashPattern(self.dp)
        else: pen.setStyle(self.qt_s)
        p.setPen(pen); cy=self.height()//2; p.drawLine(7,cy,self.width()-7,cy); p.end()


class MeasurementOverlay(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent, QT_TOOLTIP_WINDOW | QT_FRAMELESS_WINDOW); self.setAttribute(QT_WA_TRANSPARENT); self.setStyleSheet(f"QFrame{{background:{CARD};border:1px solid {PRI};border-radius:7px;}} QLabel{{color:{TEXT};background:transparent;font-size:10px;font-weight:600;padding:2px 7px;}}"); self.lab=QLabel(); l=QVBoxLayout(self); l.setContentsMargins(3,3,3,3); l.setSpacing(0); l.addWidget(self.lab); self.hide()
    def show_measure(self,text,pos): self.lab.setText(text); self.adjustSize(); self.move(pos); self.show()
    def clear(self): self.hide()


class MeasurementOverlay(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, QT_TOOLTIP_WINDOW | QT_FRAMELESS_WINDOW)
        self.setAttribute(QT_WA_TRANSPARENT)
        self.setStyleSheet(
            f"QFrame{{background:{CARD};border:1px solid {PRI};border-radius:7px;}}"
            f"QLabel{{color:{TEXT};background:transparent;font-size:10px;font-weight:600;padding:2px 7px;}}"
        )
        self.lab = QLabel()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(0)
        lay.addWidget(self.lab)
        self.hide()

    def show_measure(self, text, pos):
        self.lab.setText(text)
        self.adjustSize()
        self.move(pos)
        self.show()

    def clear(self):
        self.hide()


class ScratchXLineMapTool(QgsMapTool):
    """Route digitizer supporting two-point Line and multi-vertex LineString."""
    def __init__(self, canvas, iface, layer, parent_dialog, mode="LineString"):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.layer = layer
        self.dialog = parent_dialog
        self.mode = mode
        self.points = []
        self.rb = None
        self.distance = QgsDistanceArea()
        self.distance.setSourceCrs(layer.crs(), QgsProject.instance().transformContext())
        self.distance.setEllipsoid(QgsProject.instance().ellipsoid() or "WGS84")
        self.total = parent_dialog._line_total
        self.overlay = MeasurementOverlay(canvas.parent() or canvas.window())
        try:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        except AttributeError:
            self.setCursor(QCursor(QT_CROSS))

    def _meters(self, a, b):
        try:
            return abs(self.distance.measureLine(a, b))
        except Exception:
            return math.hypot(b.x() - a.x(), b.y() - a.y())

    def _route_distance(self, pts):
        return sum(self._meters(pts[i - 1], pts[i]) for i in range(1, len(pts)))

    def canvasPressEvent(self, event):
        left = QT_LEFT
        right = QT_RIGHT
        pt = self.toMapCoordinates(event.pos())
        if event.button() == right:
            self._cancel_route()
            return
        if event.button() != left:
            return
        # For LineString, double-click finishes without adding a duplicate point.
        if event.type() == QEvent.MouseButtonDblClick:
            if self.points:
                self._finish_route(pt if not self._same_point(pt, self.points[-1]) else None)
            return
        if self.mode == "Line":
            if not self.points:
                self.points = [pt]
            else:
                self.points.append(pt)
                self._finish_route()
        else:
            self.points.append(pt)
            self._update_measure(event.pos())

    def canvasDoubleClickEvent(self, event):
        pt = self.toMapCoordinates(event.pos())
        if self.points:
            self._finish_route(pt if not self._same_point(pt, self.points[-1]) else None)

    def canvasMoveEvent(self, event):
        if not self.points:
            return
        pt = self.toMapCoordinates(event.pos())
        preview = list(self.points) + [pt]
        self._draw_rb(preview)
        segment = self._meters(self.points[-1], pt)
        route = self._route_distance(preview)
        self._show(segment, route, event.pos())

    def keyPressEvent(self, event):
        esc = QT_ESC
        if event.key() == esc:
            self._cancel_route()
            event.accept()
            return
        try:
            super().keyPressEvent(event)
        except Exception:
            pass

    def _same_point(self, a, b):
        return abs(a.x() - b.x()) < 1e-12 and abs(a.y() - b.y()) < 1e-12

    def _show(self, segment, route, screen_pos):
        if self.dialog.lang == "en":
            rows=[("Segment", _fmt_distance(segment)), ("Distance", _fmt_distance(route)), ("Total", _fmt_distance(self.total + route))]
        else:
            rows=[("Segmen", _fmt_distance(segment)), ("Jarak", _fmt_distance(route)), ("Total", _fmt_distance(self.total + route))]
        txt = _measurement_table(rows)
        self.overlay.show_measure(
            txt,
            self.canvas.mapToGlobal(screen_pos) + QPointF(14, 14).toPoint()
        )

    def _update_measure(self, screen_pos):
        route = self._route_distance(self.points)
        self._show(0, route, screen_pos)

    def _draw_rb(self, pts):
        if len(pts) < 2:
            return
        if self.rb is None:
            self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
            self.rb.setColor(QColor(PRI))
            self.rb.setWidth(3)
        self.rb.reset(QgsWkbTypes.LineGeometry)
        for p in pts:
            self.rb.addPoint(p, False)
        self.rb.addPoint(pts[-1], True)

    def _finish_route(self, final_pt=None):
        pts = list(self.points)
        if final_pt is not None:
            if not pts or not self._same_point(final_pt, pts[-1]):
                pts.append(final_pt)
        if len(pts) < 2:
            self._cancel_route()
            return
        d = self._route_distance(pts)
        if d <= 0:
            self._cancel_route()
            return
        feat = QgsFeature(self.layer.fields())
        feat.setGeometry(QgsGeometry.fromPolylineXY(pts))
        idx = self.layer.featureCount() + 1
        feat.setAttribute("id", idx)
        feat.setAttribute("name", self.layer.name())
        if self.layer.addFeature(feat):
            self.total += d
            self.dialog._line_total = self.total
            self.dialog._save_settings()
            self.points = []
            self._clear_rb()
            self.overlay.clear()
            self.canvas.refresh()
            label = "LineString" if self.mode == "LineString" else "Line"
            self.iface.statusBarIface().showMessage(
                f"Scratch-X: {label} {_fmt_distance(d)} | Total {_fmt_distance(self.total)}"
            )

    def _cancel_route(self):
        self.points = []
        self._clear_rb()
        self.overlay.clear()
        self.iface.statusBarIface().showMessage("Scratch-X: drawing cancelled / gambar dibatalkan.")

    def _clear_rb(self):
        if self.rb is not None:
            self.rb.reset()
            self.rb = None

    def deactivate(self):
        self._cancel_route()
        super().deactivate()


class ScratchXShapeMapTool(QgsMapTool):
    """Two-click shape engine for all Scratch-X shapes."""
    def __init__(self, canvas, iface, layer, shape_type, dialog=None):
        super().__init__(canvas)
        self.canvas = canvas
        self.iface = iface
        self.layer = layer
        self.shape_type = shape_type
        self.dialog = dialog
        self.anchor = None
        self.rb = None
        self.overlay = MeasurementOverlay(canvas.parent() or canvas.window())
        try:
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        except AttributeError:
            self.setCursor(QCursor(QT_CROSS))

    def canvasPressEvent(self, event):
        left = QT_LEFT
        right = QT_RIGHT
        pt = self.toMapCoordinates(event.pos())
        if event.button() == right:
            self._cancel()
            return
        if event.button() != left:
            return
        if self.anchor is None:
            self.anchor = pt
            self._show_measure(pt, event.pos())
        else:
            self._finish(pt)

    def canvasMoveEvent(self, event):
        if self.anchor is None:
            return
        pt = self.toMapCoordinates(event.pos())
        pts = self._points(self.anchor, pt)
        if pts:
            self._draw_rb(pts)
            self._show_measure(pt, event.pos())

    def keyPressEvent(self, event):
        esc = QT_ESC
        if event.key() == esc:
            self._cancel()
            event.accept()
            return
        try:
            super().keyPressEvent(event)
        except Exception:
            pass

    def _show_measure(self, pt, screen_pos):
        if self.shape_type == "circle" and self.anchor is not None:
            r = math.hypot(pt.x() - self.anchor.x(), pt.y() - self.anchor.y())
            da = QgsDistanceArea()
            da.setSourceCrs(self.layer.crs(), QgsProject.instance().transformContext())
            da.setEllipsoid(QgsProject.instance().ellipsoid() or "WGS84")
            try:
                r_m = abs(da.measureLine(self.anchor, pt))
            except Exception:
                r_m = r
            label = "Radius" if not self.dialog or self.dialog.lang == "en" else "Radius"
            self.overlay.show_measure(
                _measurement_table([(label, _fmt_distance(r_m))]),
                self.canvas.mapToGlobal(screen_pos) + QPointF(14, 14).toPoint()
            )

    def _points(self, a, b):
        x1, y1, x2, y2 = a.x(), a.y(), b.x(), b.y()
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        rx, ry = abs(x2 - x1) / 2, abs(y2 - y1) / 2
        sid = self.shape_type
        if sid in ("rectangle", "square"):
            if sid == "square":
                s = min(abs(x2 - x1), abs(y2 - y1))
                x2 = x1 + (s if x2 >= x1 else -s)
                y2 = y1 + (s if y2 >= y1 else -s)
            return [QgsPointXY(x1,y1), QgsPointXY(x2,y1), QgsPointXY(x2,y2), QgsPointXY(x1,y2), QgsPointXY(x1,y1)]
        if sid == "circle":
            r = math.hypot(x2-x1, y2-y1)
            return self._ellipse(a, r, r)
        if sid == "ellipse":
            return self._ellipse(QgsPointXY(cx,cy), rx, ry)
        nmap = {"triangle":3,"pentagon":5,"hexagon":6,"octagon":8}
        if sid in nmap:
            return self._regular(QgsPointXY(cx,cy), min(rx,ry), nmap[sid])
        if sid == "star":
            pts=[]; r=min(rx,ry)
            for i in range(10):
                ang=-math.pi/2+i*math.pi/5
                rr=r if i%2==0 else r*.45
                pts.append(QgsPointXY(cx+rr*math.cos(ang),cy+rr*math.sin(ang)))
            pts.append(pts[0]); return pts
        if sid == "trapezoid":
            return [QgsPointXY(cx-rx*.55,cy-ry),QgsPointXY(cx+rx*.55,cy-ry),QgsPointXY(cx+rx,cy+ry),QgsPointXY(cx-rx,cy+ry),QgsPointXY(cx-rx*.55,cy-ry)]
        if sid == "parallelogram":
            return [QgsPointXY(x1+(x2-x1)*.25,y1),QgsPointXY(x2,y1),QgsPointXY(x2-(x2-x1)*.25,y2),QgsPointXY(x1,y2),QgsPointXY(x1+(x2-x1)*.25,y1)]
        if sid == "semicircle":
            pts=[QgsPointXY(cx+rx*math.cos(math.pi*i/32),cy+ry*math.sin(math.pi*i/32)) for i in range(33)]
            pts += [QgsPointXY(cx-rx,cy),QgsPointXY(cx+rx,cy)]
            return pts
        if sid == "heart":
            pts=[]; r=min(rx,ry)
            for i in range(73):
                t=2*math.pi*i/72
                xx=16*math.sin(t)**3
                yy=-(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))
                pts.append(QgsPointXY(cx+xx*r/34,cy+yy*r/34))
            pts.append(pts[0]); return pts
        if sid == "crescent":
            pts=[]; r=min(rx,ry)
            for i in range(73):
                t=math.pi/2-math.pi*i/72
                pts.append(QgsPointXY(cx+r*math.cos(t),cy+r*math.sin(t)))
            for i in range(72,-1,-1):
                t=math.pi/2-math.pi*i/72
                pts.append(QgsPointXY(cx+r*.45+r*.45*math.cos(t),cy+r*.45*math.sin(t)))
            pts.append(pts[0]); return pts
        return None

    def _ellipse(self, c, rx, ry):
        return [QgsPointXY(c.x()+rx*math.cos(2*math.pi*i/CIRCLE_SEGMENTS), c.y()+ry*math.sin(2*math.pi*i/CIRCLE_SEGMENTS)) for i in range(CIRCLE_SEGMENTS)] + [QgsPointXY(c.x()+rx,c.y())]

    def _regular(self, c, r, n):
        return [QgsPointXY(c.x()+r*math.cos(-math.pi/2+2*math.pi*i/n), c.y()+r*math.sin(-math.pi/2+2*math.pi*i/n)) for i in range(n)] + [QgsPointXY(c.x(),c.y()-r)]

    def _draw_rb(self, pts):
        if self.rb is None:
            self.rb=QgsRubberBand(self.canvas,QgsWkbTypes.PolygonGeometry)
            self.rb.setColor(QColor(PRI)); self.rb.setWidth(2)
            fill=QColor(PRI); fill.setAlpha(40); self.rb.setFillColor(fill)
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        for p in pts: self.rb.addPoint(p,False)
        self.rb.addPoint(pts[-1],True)

    def _clear_rb(self):
        if self.rb is not None:
            self.rb.reset(); self.rb=None

    def _cancel(self):
        self.anchor=None; self._clear_rb(); self.overlay.clear()
        self.iface.statusBarIface().showMessage("Scratch-X: drawing cancelled / gambar dibatalkan.")

    def _finish(self, pt):
        pts=self._points(self.anchor,pt); self._clear_rb(); self.overlay.clear(); self.anchor=None
        if pts and len(pts)>=4:
            feat=QgsFeature(self.layer.fields())
            feat.setGeometry(QgsGeometry.fromPolygonXY([pts]))
            idx=self.layer.featureCount()+1
            feat.setAttribute("id",idx); feat.setAttribute("name",self.layer.name())
            self.layer.addFeature(feat); self.canvas.refresh()

    def deactivate(self):
        self._cancel(); super().deactivate()


class ScratchXPointMapTool(QgsMapTool):
    def __init__(self, canvas, iface, layer, dialog):
        super().__init__(canvas); self.canvas=canvas; self.iface=iface; self.layer=layer; self.dialog=dialog
        try: self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        except AttributeError: self.setCursor(QCursor(QT_CROSS))
    def canvasPressEvent(self,event):
        left=QT_LEFT
        if event.button()!=left:return
        pt=self.toMapCoordinates(event.pos()); feat=QgsFeature(self.layer.fields()); feat.setGeometry(QgsGeometry.fromPointXY(pt)); idx=self.layer.featureCount()+1; feat.setAttribute("id",idx); feat.setAttribute("name",self.layer.name()); self.layer.addFeature(feat); self.canvas.refresh()
    def keyPressEvent(self,event):
        esc=QT_ESC
        if event.key()==esc:
            self.iface.mapCanvas().unsetMapTool(self); event.accept()
    def deactivate(self):
        super().deactivate()


class ScratchXPolygonMapTool(QgsMapTool):
    def __init__(self, canvas, iface, layer, dialog=None):
        super().__init__(canvas); self.canvas=canvas; self.iface=iface; self.layer=layer; self.dialog=dialog; self.points=[]; self.rb=None
        self.distance=QgsDistanceArea(); self.distance.setSourceCrs(layer.crs(), QgsProject.instance().transformContext()); self.distance.setEllipsoid(QgsProject.instance().ellipsoid() or "WGS84")
        self.overlay=MeasurementOverlay(canvas.parent() or canvas.window())
        try:self.setCursor(QCursor(QT_CROSS))
        except Exception:self.setCursor(QCursor(Qt.CrossCursor))
    def canvasPressEvent(self,event):
        left=QT_LEFT; right=QT_RIGHT; pt=self.toMapCoordinates(event.pos())
        if event.button()==right: self._cancel(); return
        if event.button()!=left:return
        self.points.append(pt); self._draw(self.points); self._show_measure(event.pos(), self.points)
    def canvasDoubleClickEvent(self,event):
        pt=self.toMapCoordinates(event.pos())
        if not self.points or not self._same(pt,self.points[-1]):self.points.append(pt)
        self._finish()
    def canvasMoveEvent(self,event):
        if not self.points:return
        pt=self.toMapCoordinates(event.pos()); pts=self.points+[pt]; self._draw(pts); self._show_measure(event.pos(),pts)
    def keyPressEvent(self,event):
        if event.key()==QT_ESC:self._cancel();event.accept();return
        try:super().keyPressEvent(event)
        except Exception:pass
    def _same(self,a,b):return abs(a.x()-b.x())<1e-12 and abs(a.y()-b.y())<1e-12
    def _area(self,pts):
        if len(pts)<3:return 0.0
        closed=list(pts)
        if not self._same(closed[0],closed[-1]):closed.append(closed[0])
        try:return abs(self.distance.measureArea(QgsGeometry.fromPolygonXY([closed])))
        except Exception:return 0.0
    def _show_measure(self,screen_pos,pts):
        label = "Total Area" if not self.dialog or self.dialog.lang == "en" else "Luas Total"
        self.overlay.show_measure(_measurement_table([(label,_fmt_area(self._area(pts)))]), self.canvas.mapToGlobal(screen_pos)+QPointF(14,14).toPoint())
    def _draw(self,pts):
        if len(pts)<2:return
        if self.rb is None:
            self.rb=QgsRubberBand(self.canvas,QgsWkbTypes.PolygonGeometry); self.rb.setColor(QColor(PRI)); self.rb.setWidth(2); f=QColor(PRI); f.setAlpha(40); self.rb.setFillColor(f)
        self.rb.reset(QgsWkbTypes.PolygonGeometry)
        for p in pts:self.rb.addPoint(p,False)
        self.rb.addPoint(pts[-1],True)
    def _finish(self):
        if len(self.points)<3:self._cancel();return
        pts=list(self.points);pts.append(pts[0]);feat=QgsFeature(self.layer.fields());feat.setGeometry(QgsGeometry.fromPolygonXY([pts]));idx=self.layer.featureCount()+1;feat.setAttribute("id",idx);feat.setAttribute("name",self.layer.name());self.layer.addFeature(feat);self.canvas.refresh();self._cancel()
    def _cancel(self):
        self.points=[]
        if self.rb is not None:self.rb.reset();self.rb=None
        self.overlay.clear(); self.iface.statusBarIface().showMessage("Scratch-X: drawing cancelled / gambar dibatalkan.")
    def deactivate(self):self._cancel();super().deactivate()


class SymbolPickerDialog(QDialog):
    selected = pyqtSignal(str)
    category_selected = pyqtSignal(str)

    def __init__(self, current, lang, parent=None, custom_symbols=None):
        super().__init__(parent)
        self.current = current
        self.lang = lang
        self.custom_symbols = custom_symbols if custom_symbols is not None else {}
        self.custom_category = self.t("Custom", "Custom")
        self.setWindowTitle(self.t("More Symbols", "Simbol Lainnya"))
        self.resize(760, 500)
        self._build()

    def t(self, en, idn):
        return en if self.lang == "en" else idn

    def _build(self):
        self.setStyleSheet(
            f"QDialog{{background:{BG};color:{TEXT};}}"
            f"QLabel{{color:{TEXT};}}"
            f"QLineEdit,QListWidget{{background:{CARD};border:1px solid {BORDER};color:{TEXT};border-radius:5px;}}"
            f"QListWidget::item{{padding:6px;color:{TEXT};}}"
            f"QListWidget::item:selected{{background:{PRI};color:white;}}"
            f"QPushButton{{background:{CARD};border:1px solid {BORDER};color:{TEXT};border-radius:5px;padding:6px 12px;}}"
            f"QPushButton:hover{{background:{HOV};border-color:{PRI};}}"
            f"QToolTip{{background:{CARD};color:{TEXT};border:1px solid {BORDER};}}"
        )
        l = QHBoxLayout(self)
        self.cats = QListWidget()
        self.cats.setFixedWidth(165)
        self.cats.setSelectionMode(QABSTRACT_SINGLE)
        for c in SYMBOL_CATEGORIES:
            self.cats.addItem(c)
        self.cats.addItem(self.custom_category)
        l.addWidget(self.cats)

        right = QVBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText(self.t("Search symbol…", "Cari simbol…"))
        right.addWidget(self.search)
        self.list = QListWidget()
        self.list.setViewMode(QLIST_ICON_MODE)
        self.list.setGridSize(QSize(110, 88))
        self.list.setIconSize(QSize(46, 46))
        self.list.setResizeMode(QLIST_ADJUST)
        right.addWidget(self.list, 1)

        actions = QHBoxLayout()
        self.load_btn = QPushButton(self.t("Load Custom Symbols…", "Muat Simbol Custom…"))
        self.load_btn.setToolTip(self.t("Load one or multiple SVG symbol files.", "Muat satu atau banyak file simbol SVG."))
        self.load_btn.clicked.connect(self._load_custom)
        actions.addWidget(self.load_btn)
        actions.addStretch()
        right.addLayout(actions)

        bb = QDialogButtonBox(QDBB_OK | QDBB_CANCEL)
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        right.addWidget(bb)
        l.addLayout(right, 1)

        self.cats.currentRowChanged.connect(self._category)
        self.search.textChanged.connect(self._filter)
        self.cats.setCurrentRow(0)

    def _category(self, row):
        item = self.cats.item(row)
        cat = item.text() if item else None
        if cat:
            self.category_selected.emit(cat)
        self._fill(cat)

    def _fill(self, cat):
        self.list.clear()
        if cat == self.custom_category:
            items = [(sid, sid, path) for sid, path in self.custom_symbols.items()]
        else:
            items = [(sid, en, idn) for sid, en, idn in SYMBOL_CATEGORIES.get(cat, [])]
        for sid, label, extra in items:
            item = QListWidgetItem(label)
            item.setData(QT_USER_ROLE, sid)
            pm = QPixmap(46, 46)
            pm.fill(QT_TRANSPARENT)
            if cat == self.custom_category and os.path.exists(extra):
                icon = QIcon(extra)
                item.setIcon(icon)
            else:
                painter = QPainter(pm)
                draw_symbol(painter, sid, QRectF(2, 2, 42, 42))
                painter.end()
                item.setIcon(QIcon(pm))
            self.list.addItem(item)
        for i in range(self.list.count()):
            if self.list.item(i).data(QT_USER_ROLE) == self.current:
                self.list.setCurrentRow(i)
                break

    def _filter(self, text):
        q = text.lower().strip()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(bool(q and q not in item.text().lower()))

    def _load_custom(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.t("Load Custom Symbols", "Muat Simbol Custom"),
            "",
            self.t("SVG Symbols (*.svg)", "Simbol SVG (*.svg)")
        )
        if not files:
            return
        for path in files:
            base = os.path.splitext(os.path.basename(path))[0]
            sid = "custom_" + base
            n = 2
            while sid in self.custom_symbols and self.custom_symbols[sid] != path:
                sid = f"custom_{base}_{n}"
                n += 1
            self.custom_symbols[sid] = path
        self.cats.setCurrentRow(self.cats.count() - 1)
        self._fill(self.custom_category)
        if self.list.count():
            self.list.setCurrentRow(self.list.count() - 1)

    def _accept(self):
        it = self.list.currentItem()
        if it:
            self.selected.emit(it.data(QT_USER_ROLE))
        self.accept()


class AboutDialog(QDialog):
    def __init__(self,lang,version,parent=None):
        super().__init__(parent); self.setWindowTitle("About Scratch-X"); self.resize(560,450); self.lang=lang; self.version=version; self._build()
    def _build(self):
        self.setStyleSheet(f"QDialog{{background:{BG};}} QLabel{{color:{TEXT};}} QPushButton{{background:{CARD};border:1px solid {BORDER};border-radius:6px;color:{TEXT};padding:7px 12px;}} QPushButton:hover{{background:{HOV};}}")
        l=QVBoxLayout(self);title=QLabel("Scratch-X");title.setStyleSheet(f"color:{TEXT};font-size:20px;font-weight:700;");l.addWidget(title)
        sub=QLabel("Fast and flexible scratch geometry tool for QGIS." if self.lang=="en" else "Tool gambar geometri scratch yang cepat dan fleksibel untuk QGIS.");sub.setWordWrap(True);l.addWidget(sub)
        info=QLabel(f"<b>Version:</b> {self.version}<br><b>Author:</b> Jujun Junaedi<br><b>Contact:</b> <a href='mailto:jujun.junaedi@outlook.com'>jujun.junaedi@outlook.com</a>");info.setOpenExternalLinks(True);l.addWidget(info);l.addWidget(Divider())
        body=("Create Line, LineString, Point, Polygon and customizable Shapes directly on the QGIS map canvas. Includes dynamic measurements, categorized point symbols, custom symbols and saving to SHP, TAB, KML or GeoJSON." if self.lang=="en" else "Buat Line, LineString, Point, Polygon dan Shape yang dapat dikustomisasi langsung di kanvas peta QGIS. Mendukung pengukuran dinamis, kategori simbol Point, simbol custom dan penyimpanan ke SHP, TAB, KML atau GeoJSON.")
        lb=QLabel(body);lb.setWordWrap(True);l.addWidget(lb)
        support=QLabel("<b>Support Scratch-X Development</b><br>If Scratch-X is useful for your work, you can support its continued development." if self.lang=="en" else "<b>Dukung Pengembangan Scratch-X</b><br>Jika Scratch-X bermanfaat untuk pekerjaan Anda, Anda dapat mendukung pengembangan plugin ini.");support.setWordWrap(True);l.addWidget(support)
        row=QHBoxLayout()
        for txt,url in [("PayPal","https://paypal.me/junjunan81"),("Buy Me a Coffee","https://buymeacoffee.com/juneth"),("Saweria (IDN)","https://saweria.co/juneth")]:
            b=QPushButton(txt);b.clicked.connect(lambda _,u=url:QDesktopServices.openUrl(QUrl(u)));row.addWidget(b)
        l.addLayout(row);l.addStretch();l.addWidget(QLabel("© 2025–2026 Jujun Junaedi"));close=QPushButton("OK");close.clicked.connect(self.accept);l.addWidget(close,0,Qt.AlignRight)


class ScratchXDialog(QDialog):
    VERSION="2.1.1"
    SETTINGS_ORG="ScratchX"
    SETTINGS_APP="ScratchX"
    def __init__(self,iface,parent=None):
        super().__init__(parent or iface.mainWindow());self.iface=iface;self.settings=QSettings(self.SETTINGS_ORG,self.SETTINGS_APP)
        self.lang=self.settings.value("language","id")
        self._fill_c=QColor(self.settings.value("fill_color","#4ADE80"));self._bdr_c=QColor(self.settings.value("border_color","#FFFFFF"));self._trans=int(self.settings.value("transparency",40));self._bw=float(self.settings.value("line_width",2.0));self._sym_size=float(self.settings.value("symbol_size",12.0));self._ls=self.settings.value("line_style","solid");self._sym_sid=self.settings.value("symbol","circle");self._symbol_category=self.settings.value("symbol_category","Basic");self._geom="Line";self._line_mode=self.settings.value("line_mode","LineString");self._shape=self.settings.value("shape","circle");self._fmt=self.settings.value("format","shp");self._path="";self._active_tool=None;self._line_total=0.0;self._temp_layer_ids=[];self._custom_symbols=self._load_custom_symbols()
        self.setWindowTitle("Scratch-X");self.setWindowFlags(QT_WINDOW|QT_WINDOW_TITLE|QT_WINDOW_SYSTEM_MENU|QT_WINDOW_MINIMIZE|QT_WINDOW_CLOSE);self.setModal(False);self.setMinimumSize(380,500)
        layout_rev="3.1.7"
        saved_rev=str(self.settings.value("layout_version",""))
        if saved_rev!=layout_rev:
            self._initial_w=430; self._initial_h=560
        else:
            self._initial_w=max(380,min(620,int(self.settings.value("width",430,type=int))))
            self._initial_h=max(500,min(760,int(self.settings.value("height",560,type=int))))
        self.resize(self._initial_w,self._initial_h);self._apply_theme();self._build();self._wire();self._retranslate();self._sel_geom(self._geom)
    def showEvent(self,event):
        super().showEvent(event)
        try:
            self._position_tool_window()
        except Exception:
            pass

    def tr(self,en,idn):return en if self.lang=="en" else idn
    def _apply_theme(self):
        self.setStyleSheet(f"QDialog{{background:{BG};color:{TEXT};font-family:'Segoe UI','Inter',sans-serif;font-size:11px;}} QLabel{{color:{TEXT};background:transparent;}} QLineEdit,QComboBox,QDoubleSpinBox{{background:{CARD};border:1.5px solid {BORDER};border-radius:6px;color:{TEXT};padding:4px 8px;font-size:11px;}} QLineEdit:focus,QComboBox:focus,QDoubleSpinBox:focus{{border-color:{PRI};}} QComboBox QAbstractItemView{{background:{PANEL};color:{TEXT};selection-background-color:{PRI};}} QToolTip{{background:{CARD};color:{TEXT};border:1px solid {BORDER};padding:5px 8px;}} QPushButton{{font-family:'Segoe UI','Inter',sans-serif;}}")
    def _build(self):
        # Compact independent tool window. Geometry is one row; only STYLE scrolls.
        # SAVE GEOMETRY and the footer are fixed/always visible.
        root=QVBoxLayout(self);root.setContentsMargins(0,0,0,0);root.setSpacing(0)
        root.addWidget(self._mkTitle())
        body=QWidget();bl=QVBoxLayout(body);bl.setContentsMargins(10,4,10,4);bl.setSpacing(2)
        geom=self._mkGeomCol();geom.setSizePolicy(QSP_EXPANDING,QSP_FIXED);bl.addWidget(geom)
        style_scroll=QScrollArea();style_scroll.setWidgetResizable(True);style_scroll.setFrameShape(QFRAME_NOFRAME);style_scroll.setSizePolicy(QSP_EXPANDING,QSP_EXPANDING);style_scroll.viewport().setStyleSheet(f"background:{BG};border:none;")
        style_scroll.setStyleSheet(f"QScrollArea{{background:{BG};border:none;}}QScrollBar:vertical{{background:{PANEL};width:7px;border:none;}}QScrollBar::handle:vertical{{background:{BORDER};border-radius:3px;min-height:22px;}}QScrollBar::handle:vertical:hover{{background:{PRI};}}")
        style_widget=self._mkStyleCol();style_scroll.setWidget(style_widget);bl.addWidget(style_scroll,1)
        save=self._mkSaveCol();save.setSizePolicy(QSP_EXPANDING,QSP_FIXED);bl.addWidget(save,0)
        root.addWidget(body,1);root.addWidget(self._mkFooter())
        self._scroll=style_scroll; self._content=style_widget
        self._position_tool_window()

    def _position_tool_window(self):
        """Place Scratch-X as a compact floating toolbox on the right side of the QGIS work area, never below the taskbar."""
        try:
            mw=self.iface.mainWindow()
            screen=mw.screen() if hasattr(mw,"screen") else QApplication.primaryScreen()
            if screen is None: return
            ag=screen.availableGeometry()
            margin=8
            x=ag.right()-self.width()-margin
            y=ag.top()+8
            y=min(y,ag.bottom()-self.height()-margin)
            y=max(ag.top()+margin,y)
            self.move(max(ag.left()+margin,x),y)
        except Exception:
            pass
    def _mkTitle(self):
        bar=QWidget();bar.setFixedHeight(46);bar.setStyleSheet(f"background:{PANEL};border-bottom:1px solid {BORDER};");l=QHBoxLayout(bar);l.setContentsMargins(12,0,10,0);logo=QLabel();logo.setPixmap(self._logoPx(28,28));logo.setFixedSize(28,28);l.addWidget(logo);l.addSpacing(7);self._title=QLabel("Scratch-X");self._title.setStyleSheet(f"color:{TEXT};font-size:15px;font-weight:700;");l.addWidget(self._title);l.addStretch();self._lang=QComboBox();self._lang.addItems(["Indonesia","English"]);self._lang.setFixedWidth(92);self._lang.setCurrentIndex(1 if self.lang=="en" else 0);self._lang.setToolTip(self.tr("Change language","Ganti bahasa"));l.addWidget(self._lang);l.addSpacing(6);self._ver=QLabel("v"+self.VERSION);self._ver.setStyleSheet(f"color:{MUTED};font-size:9px;");l.addWidget(self._ver);l.addSpacing(7);self._help=QPushButton("?");self._help.setFixedSize(30,30);self._help.setToolTip(self.tr("How to use Scratch-X","Cara menggunakan Scratch-X"));self._help.setStyleSheet(self._round_icon_style());self._help.clicked.connect(self._show_help);l.addWidget(self._help);self._about=QPushButton("i");self._about.setFixedSize(30,30);self._about.setToolTip(self.tr("About Scratch-X","Tentang Scratch-X"));self._about.setStyleSheet(self._round_icon_style());self._about.clicked.connect(self._show_about);l.addWidget(self._about);return bar
    def _round_icon_style(self):return f"QPushButton{{background:{CARD};border:1px solid {BORDER};border-radius:15px;color:{DIM};font-weight:700;font-size:12px;}}QPushButton:hover{{background:{HOV};color:white;border-color:{PRI};}}"
    def _logoPx(self,w,h):
        px=QPixmap(w,h);px.fill(QT_TRANSPARENT);p=QPainter(px);p.setRenderHint(QPAINTER_ANTIALIASING);p.setBrush(QBrush(QColor(PRI)));p.setPen(QT_NO_PEN);p.drawRoundedRect(0,0,w,h,6,6);p.setPen(QPen(QColor("white"),2,QT_SOLID,QT_ROUND_CAP));m=6;p.drawLine(m,m,w-m,h-m);p.drawLine(w-m,m,m,h-m);p.setBrush(QBrush(QColor(A_L)));p.setPen(QT_NO_PEN);p.drawEllipse(w//2-3,h//2-3,6,6);p.end();return px
    def _mkGeomCol(self):
        w=QWidget();w.setMinimumWidth(0);l=QVBoxLayout(w);l.setContentsMargins(0,0,0,0);l.setSpacing(3);self._gh=QLabel();self._gh.setStyleSheet(f"color:{MUTED};font-size:8px;font-weight:700;");l.addWidget(self._gh);self._ggrp=QButtonGroup(self);self._gbtns={};self._geom_specs=[("Line","⌁",A_L),("Point","◆",A_P),("Polygon","⬟",A_PL),("Shape","◇",A_S)]
        row=QHBoxLayout();row.setContentsMargins(0,0,0,0);row.setSpacing(5)
        for nm,ic,ac in self._geom_specs:
            b=GeomBtn(nm,ic,ac);b.setFixedHeight(34);b.setSizePolicy(QSP_EXPANDING,QSP_FIXED);self._ggrp.addButton(b);row.addWidget(b);self._gbtns[nm]=b;b.setToolTip(self.tr({"Line":"Line / LineString route","Point":"Place point symbols","Polygon":"Draw polygon","Shape":"Draw geometric shapes"}[nm],{"Line":"Gambar Line / LineString sebagai rute","Point":"Tempatkan simbol point","Polygon":"Gambar polygon","Shape":"Gambar bentuk geometri"}[nm]))
        l.addLayout(row);self._gtip=QLabel();self._gtip.setWordWrap(True);self._gtip.setMinimumHeight(22);self._gtip.setMaximumHeight(25);self._gtip.setStyleSheet(f"background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.25);border-radius:6px;color:{MUTED};font-size:8px;padding:4px;");l.addWidget(self._gtip);return w

    def _mkStyleCol(self):
        outer=QWidget();outer.setStyleSheet(f"background:{BG};");ol=QVBoxLayout(outer);ol.setContentsMargins(0,0,0,0);ol.setSpacing(1);self._sh=QLabel();self._sh.setStyleSheet(f"color:{MUTED};font-size:8px;font-weight:700;");ol.addWidget(self._sh);pan=QWidget();pan.setStyleSheet(f"background:{BG};border:1px solid {BORDER};border-radius:7px;");pl=QVBoxLayout(pan);pl.setContentsMargins(8,4,8,4);pl.setSpacing(2)
        self._fill_blk=ColorBlock(self.tr("Fill Color","Warna Fill"),self._fill_c.name(),QC_FILL,True);pl.addWidget(self._fill_blk);pl.addWidget(Divider());tr=QHBoxLayout();self._translab=QLabel();tr.addWidget(self._translab);self._tsl=QSlider(QT_HORIZONTAL);self._tsl.setRange(0,100);self._tsl.setValue(self._trans);self._tvl=QLabel();self._tvl.setFixedWidth(34);tr.addWidget(self._tsl,1);tr.addWidget(self._tvl);pl.addLayout(tr);pl.addWidget(Divider());self._bdr_blk=ColorBlock(self.tr("Border Color","Warna Border"),self._bdr_c.name(),QC_BDR);pl.addWidget(self._bdr_blk);pl.addWidget(Divider());br=QHBoxLayout();self._bwl=QLabel();br.addWidget(self._bwl);self._bwspin=QDoubleSpinBox();self._bwspin.setRange(.1,20);self._bwspin.setSingleStep(.25);self._bwspin.setValue(self._bw);self._bwspin.setSuffix(" px");self._bwspin.setFixedWidth(82);br.addWidget(self._bwspin);pl.addLayout(br);self._sym_size_row=QWidget();ssr=QHBoxLayout(self._sym_size_row);ssr.setContentsMargins(0,0,0,0);self._symsizel=QLabel();ssr.addWidget(self._symsizel);self._sym_sizespin=QDoubleSpinBox();self._sym_sizespin.setRange(2,64);self._sym_sizespin.setSingleStep(1);self._sym_sizespin.setValue(self._sym_size);self._sym_sizespin.setSuffix(" px");self._sym_sizespin.setFixedWidth(82);ssr.addWidget(self._sym_sizespin);pl.addWidget(self._sym_size_row);pl.addWidget(Divider());lr=QVBoxLayout();self._lsl=QLabel();lr.addWidget(self._lsl);lg=QGridLayout();lg.setSpacing(3);self._lsgrp=QButtonGroup(self);self._lsbtns={};
        for i,(sid,en,qt,qgis,dp) in enumerate(LINE_STYLES):
            b=LsBtn(sid,qt,qgis,dp);self._lsgrp.addButton(b);lg.addWidget(b,i//3,i%3);self._lsbtns[sid]=b;b.clicked.connect(lambda _,n=sid:self._set_line_style(n));
        self._lsbtns.get(self._ls,self._lsbtns["solid"]).setChecked(True);lr.addLayout(lg);pl.addLayout(lr);self._line_mode_row=QWidget();_lm=QHBoxLayout(self._line_mode_row);_lm.setContentsMargins(0,0,0,0);_lm.setSpacing(5);self._linemode=QLabel();_lm.addWidget(self._linemode);self._line_mode_combo=QComboBox();self._line_mode_combo.addItems(["Line (2-point)","LineString (Route)"]);self._line_mode_combo.setCurrentIndex(1 if self._line_mode=="LineString" else 0);_lm.addWidget(self._line_mode_combo,1);pl.addWidget(self._line_mode_row)
        self._sym_sec=QWidget();ssl=QVBoxLayout(self._sym_sec);ssl.setContentsMargins(0,0,0,0);ssl.setSpacing(3);self._syml=QLabel();ssl.addWidget(self._syml);sg=QGridLayout();sg.setSpacing(3);self._sgrp=QButtonGroup(self);self._sbtns=[]
        for i,sid in enumerate(QUICK_SYMBOLS[:8]):
            label=next((x[1] for x in SYMBOL_CATEGORIES["Basic"] if x[0]==sid),sid);b=SymBtn(sid,label);self._sgrp.addButton(b);sg.addWidget(b,i//8,i%8);self._sbtns.append(b);b.clicked.connect(lambda _,btn=b:self._set_symbol(btn.sid))
        self._refresh_quick_symbols(self._symbol_category);ssl.addLayout(sg);self._more_sym=QPushButton();self._more_sym.setFixedHeight(32);self._more_sym.setStyleSheet(f"QPushButton{{background:{CARD};border:1px solid {BORDER};border-radius:6px;color:{TEXT};font-size:10px;font-weight:600;}}QPushButton:hover{{background:{HOV};border-color:{PRI};color:white;}}");self._more_sym.clicked.connect(self._open_symbols);ssl.addWidget(self._more_sym);pl.addWidget(self._sym_sec)
        self._shape_sec=QWidget();shl=QVBoxLayout(self._shape_sec);shl.setContentsMargins(0,0,0,0);shl.setSpacing(3);self._shapel=QLabel();shl.addWidget(self._shapel);sg2=QGridLayout();sg2.setSpacing(3);self._shapegrp=QButtonGroup(self);self._shape_btns=[]
        for i,(sid,en,idn) in enumerate(SHAPES):
            b=ShapeBtn(sid,en if self.lang=="en" else idn);self._shapegrp.addButton(b);sg2.addWidget(b,i//5,i%5);self._shape_btns.append(b);b.clicked.connect(lambda _,s=sid:self._set_shape(s))
        self._shape_btns[0].setChecked(True);shl.addLayout(sg2);pl.addWidget(self._shape_sec);self._shape_sec.setVisible(False);self._sym_size_row.setVisible(False);ol.addWidget(pan,1);return outer
    def _mkSaveCol(self):
        w=QWidget();w.setMinimumWidth(180);w.setMinimumHeight(96);l=QVBoxLayout(w);l.setContentsMargins(0,0,0,0);l.setSpacing(5);self._saveh=QLabel();self._saveh.setStyleSheet(f"color:{MUTED};font-size:8px;font-weight:700;letter-spacing:.8px;");l.addWidget(self._saveh);self._formatl=QLabel();self._formatl.setStyleSheet(f"color:{MUTED};font-size:9px;");l.addWidget(self._formatl);self._fcombo=QComboBox();self._fcombo.addItems(["ESRI Shapefile (*.shp)","MapInfo TAB (*.tab)","Keyhole Markup Language (*.kml)","GeoJSON (*.geojson)"]);self._fcombo.setCurrentIndex(["shp","tab","kml","geojson"].index(self._fmt) if self._fmt in ["shp","tab","kml","geojson"] else 0);l.addWidget(self._fcombo);self._pathl=QLabel();self._pathl.setStyleSheet(f"color:{MUTED};font-size:9px;");l.addWidget(self._pathl);row=QHBoxLayout();row.setSpacing(4);self._pedit=QLineEdit();self._pedit.setReadOnly(True);self._pedit.setText(self.tr("Temporary Layer","Temporary Layer"));self._pedit.setToolTip(self.tr("No path selected: the next layer is temporary.","Belum ada lokasi: layer berikutnya bersifat temporary."));row.addWidget(self._pedit,1);self._browsebtn=QPushButton();self._browsebtn.setIcon(QApplication.style().standardIcon(QSTYLE_DIR_OPEN));self._browsebtn.setIconSize(QSize(18,18));self._browsebtn.setFixedSize(32,28);self._browsebtn.setToolTip(self.tr("Choose output file/folder","Pilih file/folder penyimpanan"));self._browsebtn.setStyleSheet(f"QPushButton{{background:{CARD};border:1px solid {BORDER};border-radius:6px;color:{TEXT};font-size:14px;}}QPushButton:hover{{background:{HOV};border-color:{PRI};}}QPushButton:pressed{{background:{PRI};}}");self._browsebtn.clicked.connect(self._browse);row.addWidget(self._browsebtn);l.addLayout(row);self._savehint=QLabel();self._savehint.setWordWrap(True);self._savehint.setStyleSheet(f"color:{MUTED};font-size:8px;padding-top:2px;");l.addWidget(self._savehint);return w
    def _mkFooter(self):
        f=QWidget();f.setFixedHeight(42);f.setStyleSheet(f"background:{PANEL};border-top:1px solid {BORDER};");l=QHBoxLayout(f);l.setContentsMargins(12,0,12,0);self._footerhint=QLabel();self._footerhint.setVisible(False);self._footerhint.setMaximumWidth(0);l.addWidget(self._footerhint);l.addStretch();self._clearbtn=QPushButton();self._clearbtn.setFixedSize(72,32);self._clearbtn.setToolTip(self.tr("Remove Scratch-X temporary layers from the current QGIS project.","Hapus layer temporary Scratch-X dari project QGIS saat ini."));self._clearbtn.clicked.connect(self._clear_temp_layers);self._clearbtn.setStyleSheet(f"QPushButton{{background:{CARD};border:1.5px solid {BORDER};border-radius:7px;color:{DIM};font-size:11px;}}QPushButton:hover{{background:{HOV};color:white;border-color:#EF4444;}}");l.addWidget(self._clearbtn);self._closebtn=QPushButton();self._closebtn.setFixedSize(64,32);self._closebtn.clicked.connect(self.hide);self._closebtn.setStyleSheet(f"QPushButton{{background:{CARD};border:1.5px solid {BORDER};border-radius:7px;color:{DIM};font-size:11px;}}QPushButton:hover{{background:{HOV};color:white;}}");l.addWidget(self._closebtn);self._mkbtn=QPushButton();self._mkbtn.setFixedSize(118,32);self._mkbtn.setStyleSheet(f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {PRI},stop:1 #8B5CF6);border:none;border-radius:7px;color:white;font-size:11px;font-weight:600;}}QPushButton:hover{{background:#7C3AED;}}");self._mkbtn.clicked.connect(self._create);l.addWidget(self._mkbtn);return f
    def _wire(self):
        for nm,b in self._gbtns.items():b.clicked.connect(lambda _,n=nm:self._sel_geom(n))
        self._fill_blk.changed.connect(lambda c:self._set_and_save("fill_color",c.name(),"_fill_c"));self._bdr_blk.changed.connect(lambda c:self._set_and_save("border_color",c.name(),"_bdr_c"));self._tsl.valueChanged.connect(self._on_trans);self._bwspin.valueChanged.connect(lambda v:self._set_and_save("line_width",v,"_bw"));self._sym_sizespin.valueChanged.connect(lambda v:self._set_and_save("symbol_size",v,"_sym_size"));self._fcombo.currentIndexChanged.connect(self._on_format);self._lang.currentIndexChanged.connect(self._change_lang);self._line_mode_combo.currentIndexChanged.connect(self._on_line_mode)
    def _set_and_save(self,key,value,attr):
        if attr in ("_fill_c","_bdr_c"):
            value = QColor(value) if not isinstance(value,QColor) else value
        setattr(self,attr,value)
        self.settings.setValue(key,value.name() if isinstance(value,QColor) else value)
    def _set_line_style(self,n):self._ls=n;self.settings.setValue("line_style",n)
    def _on_line_mode(self,i):self._line_mode="LineString" if i==1 else "Line";self.settings.setValue("line_mode",self._line_mode)
    def _change_lang(self,i):self.lang="en" if i==1 else "id";self.settings.setValue("language",self.lang);self._retranslate()
    def _retranslate(self):
        self._gh.setText(self.tr("1. GEOMETRY TYPE","1. JENIS GEOMETRI"));self._sh.setText(self.tr("2. STYLE","2. STYLE"));self._saveh.setText(self.tr("3. SAVE GEOMETRY","3. SIMPAN GEOMETRI"));self._formatl.setText(self.tr("Format","Format"));self._pathl.setText(self.tr("File Path","File Path"));self._savehint.setText(self.tr("After Create Layer, the next geometry starts with Temporary Layer. Choose a path only when you want to save the next geometry.","Setelah Buat Layer, geometri berikutnya kembali ke Temporary Layer. Pilih lokasi hanya jika geometri berikutnya ingin disimpan."));self._footerhint.setText(self.tr("Select geometry → configure style → create layer → draw on canvas.","Pilih geometri → atur style → buat layer → gambar di kanvas."));self._clearbtn.setText(self.tr("Clear","Bersihkan"));self._closebtn.setText(self.tr("Close","Tutup"));self._mkbtn.setText(self.tr("  +  Create Layer","  +  Buat Layer"));self._translab.setText(self.tr("Transparency","Transparansi"));self._bwl.setText(self.tr("Line Width","Lebar Garis"));self._symsizel.setText(self.tr("Symbol Size","Ukuran Simbol"));self._lsl.setText(self.tr("Line Style","Gaya Garis"));self._syml.setText(self.tr("Point Symbol","Simbol Point"));self._more_sym.setText(self.tr("More Symbols…","Simbol Lainnya…"));self._shapel.setText(self.tr("Shape","Bentuk"));self._linemode.setText(self.tr("Draw mode","Mode gambar"));self._line_mode_combo.setItemText(0,self.tr("Line (2-point)","Line (2-titik)"));self._line_mode_combo.setItemText(1,self.tr("LineString (Route)","LineString (Rute)"));self._pedit.setText(self._path if self._path else "Temporary Layer");self._help.setToolTip(self.tr("How to use Scratch-X","Cara menggunakan Scratch-X"));self._about.setToolTip(self.tr("About Scratch-X","Tentang Scratch-X"));self._browsebtn.setToolTip(self.tr("Choose output file/folder","Pilih file/folder penyimpanan"));self._update_shape_tips()
    def _on_trans(self,v):self._trans=v;self._tvl.setText(f"{v} %");self.settings.setValue("transparency",v)
    def _sel_geom(self,nm):
        self._geom=nm
        for n,b in self._gbtns.items():b.setChecked(n==nm)
        self._sym_sec.setVisible(nm=="Point");self._sym_size_row.setVisible(nm=="Point");self._shape_sec.setVisible(nm=="Shape");self._line_mode_row.setVisible(nm=="Line");self._update_shape_tips()
    def _update_shape_tips(self):
        if self._geom=="Line":self._gtip.setText(self.tr("Line: choose 2-point Line or LineString Route. Press ESC to cancel the current drawing.","Line: pilih Line 2-titik atau LineString Rute. Tekan ESC untuk membatalkan gambar."))
        elif self._geom=="Point":self._gtip.setText(self.tr("Choose a symbol, then click the map. Press ESC to cancel the tool.","Pilih simbol, lalu klik peta. Tekan ESC untuk membatalkan tool."))
        elif self._geom=="Polygon":self._gtip.setText(self.tr("Click vertices and double-click to finish. Press ESC to cancel.","Klik titik-titik dan double-click untuk selesai. Tekan ESC untuk membatalkan."))
        else:self._gtip.setText(self.tr("Choose a shape, then use two clicks. Circle shows its radius dynamically. Press ESC to cancel.","Pilih shape, lalu gunakan dua klik. Circle menampilkan radius secara dinamis. Tekan ESC untuk membatalkan."))
    def _open_symbols(self):
        dlg=SymbolPickerDialog(self._sym_sid,self.lang,self,self._custom_symbols)
        dlg.selected.connect(self._set_symbol)
        dlg.category_selected.connect(self._refresh_quick_symbols)
        dlg.exec()
        self._save_custom_symbols()

    def _refresh_quick_symbols(self, category):
        # The category click in More Symbols immediately changes the sample
        # symbols shown in the main Point Symbol panel.
        self._symbol_category = category
        self.settings.setValue("symbol_category", category)
        if category == "Custom":
            items=[(sid,sid,self._custom_symbols.get(sid)) for sid in self._custom_symbols.keys()]
        else:
            items=[(sid, (en if self.lang=="en" else idn), None) for sid,en,idn in SYMBOL_CATEGORIES.get(category, [])]
        if not items:
            return
        for i,b in enumerate(self._sbtns):
            if i < len(items):
                sid,label,path=items[i]
                b.set_symbol(sid,label,path);b.show();b.setChecked(sid==self._sym_sid);b.update()
            else:
                b.hide()
        if self._sym_sid not in [sid for sid,_,_ in items]:
            self._set_symbol(items[0][0])

    def _set_symbol(self,sid):
        self._sym_sid=sid;self.settings.setValue("symbol",sid)
        for b in self._sbtns:b.setChecked(b.sid==sid);b.update()
    def _set_shape(self,sid):self._shape=sid;self.settings.setValue("shape",sid);[b.setChecked(b.sid==sid) for b in self._shape_btns]
    def _on_format(self,i):
        self._fmt=["shp","tab","kml","geojson"][i];self.settings.setValue("format",self._fmt)
    def _browse(self):
        filters={"shp":"ESRI Shapefile (*.shp)","tab":"MapInfo TAB (*.tab)","kml":"Keyhole Markup Language (*.kml)","geojson":"GeoJSON (*.geojson)"};base="scratch_"+self._geom.lower();path,_=QFileDialog.getSaveFileName(self,self.tr("Save Geometry","Simpan Geometri"),base,filters[self._fmt]);
        if path:
            ext="."+self._fmt
            if not path.lower().endswith(ext):path+=ext
            self._path=path;self._pedit.setText(path)
    def _unique_temp_name(self,base):
        names={l.name() for l in QgsProject.instance().mapLayers().values()};n=base;i=2
        while n in names:n=f"{base}_{i}";i+=1
        return n
    def _create(self):
        gmap={"Line":"LineString","Point":"Point","Polygon":"Polygon","Shape":"Polygon"};gs=gmap[self._geom]
        current_path=self._path
        nm=os.path.splitext(os.path.basename(current_path))[0] if current_path else self._unique_temp_name("scratch_"+self._geom.lower())
        proj_crs=QgsProject.instance().crs().authid() or "EPSG:4326";vl=QgsVectorLayer(f"{gs}?crs={proj_crs}",nm,"memory")
        if not vl.isValid():QMessageBox.critical(self,self.tr("Error","Error"),self.tr("Failed to create layer.","Gagal membuat layer."));return
        vl.dataProvider().addAttributes([QgsField("id", _QTYPE_INT), QgsField("name", _QTYPE_STRING), QgsField("notes", _QTYPE_STRING)]);vl.updateFields();self._apply_sym(vl,gs);QgsProject.instance().addMapLayer(vl)
        vl.setCustomProperty("ScratchX/temporary", not bool(current_path))
        vl.setCustomProperty("ScratchX/version", self.VERSION)
        if not current_path:self._temp_layer_ids.append(vl.id())
        self._line_total=0.0;self._activate(vl,gs,current_path)
        # Critical: the next Create Layer operation ALWAYS starts from Temporary Layer.
        self._path="";self._pedit.setText("Temporary Layer");self._save_settings()
    def _apply_sym(self,layer,gs):
        alpha=int((1-self._trans/100.0)*255);fc=QColor(self._fill_c);fc.setAlpha(alpha);bc=QColor(self._bdr_c);bw_mm=self._bw*.25;qgis_ls={"solid":"solid","dash":"dash","dot":"dot","dashdot":"dash dot","dashdotdot":"dash dot dot","longdash":"dash"}.get(self._ls,"solid")
        def ca(c):return f"{c.red()},{c.green()},{c.blue()},{c.alpha()}"
        try:
            if gs=="Point":
                svg_path=self._custom_symbols.get(self._sym_sid) or os.path.join(os.path.dirname(__file__),"symbols",self._sym_sid+".svg")
                if os.path.exists(svg_path) and self._sym_sid not in SIMPLE_MARKERS:
                    try:
                        ml=QgsSvgMarkerSymbolLayer(svg_path,self._sym_size,0.0);sym=QgsMarkerSymbol([ml]);
                        try:ml.setColor(fc);ml.setStrokeColor(bc);ml.setStrokeWidth(bw_mm)
                        except Exception:pass
                    except Exception:sym=QgsMarkerSymbol.createSimple({})
                else:
                    sym=QgsMarkerSymbol.createSimple({});ml=sym.symbolLayer(0);attr=SIMPLE_MARKERS.get(self._sym_sid,"Circle")
                    try:ml.setShape(getattr(QgsSimpleMarkerSymbolLayer,attr))
                    except Exception:ml.setShape(QgsSimpleMarkerSymbolLayer.Circle)
                    ml.setColor(fc);ml.setStrokeColor(bc);ml.setStrokeWidth(bw_mm);ml.setSize(self._sym_size)
                layer.setRenderer(QgsSingleSymbolRenderer(sym))
            elif gs=="LineString":layer.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"color":ca(fc),"line_style":qgis_ls,"line_width":str(bw_mm),"line_width_unit":"MM"})))
            else:layer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({"color":ca(fc),"outline_color":ca(bc),"outline_width":str(bw_mm),"outline_width_unit":"MM","style":"solid","outline_style":qgis_ls})))
            layer.triggerRepaint()
        except Exception as e:print("[ScratchX] renderer:",e)
    def _activate(self,layer,gs,path):
        try:
            self.iface.setActiveLayer(layer);layer.startEditing();canvas=self.iface.mapCanvas()
            if self._active_tool:
                try:canvas.unsetMapTool(self._active_tool)
                except Exception:pass
            if path:
                def stopped():
                    try:layer.editingStopped.disconnect(stopped)
                    except Exception:pass
                    self._auto_save(layer,path)
                layer.editingStopped.connect(stopped)
            if self._geom=="Line":self._active_tool=ScratchXLineMapTool(canvas,self.iface,layer,self,self._line_mode);canvas.setMapTool(self._active_tool)
            elif self._geom=="Shape":self._active_tool=ScratchXShapeMapTool(canvas,self.iface,layer,self._shape,self);canvas.setMapTool(self._active_tool)
            elif self._geom=="Point":self._active_tool=ScratchXPointMapTool(canvas,self.iface,layer,self);canvas.setMapTool(self._active_tool)
            else:self._active_tool=ScratchXPolygonMapTool(canvas,self.iface,layer,self);canvas.setMapTool(self._active_tool)
            if path:msg=self.tr("Layer ready. Finish drawing, then click Stop Editing to write the geometry to the selected file.","Layer siap. Selesaikan gambar, lalu klik Stop Editing untuk menulis geometri ke file yang dipilih.")
            else:msg=self.tr("Temporary Layer ready. The next Create Layer operation will start again as Temporary Layer.","Temporary Layer siap. Pembuatan layer berikutnya akan kembali ke Temporary Layer.")
            self.iface.statusBarIface().showMessage(msg)
        except Exception as e:QMessageBox.critical(self,self.tr("Activation Error","Error Aktivasi"),str(e))
    def _kml_symbol_svg(self):
        """Return an SVG string suitable for Google Earth icon rasterization."""
        sid=self._sym_sid
        svg_path=self._custom_symbols.get(sid) or os.path.join(os.path.dirname(__file__),"symbols",sid+".svg")
        if os.path.exists(svg_path):
            try:
                data=open(svg_path,"r",encoding="utf-8").read()
                data=data.replace("param(fill)",self._fill_c.name()).replace("param(outline)",self._bdr_c.name()).replace("param(outline-width)",str(max(1.0,self._bw*1.5)))
                return data
            except Exception:
                pass
        # Basic marker fallback: create a clean SVG with the same geometry used by Scratch-X.
        fc=self._fill_c.name();bc=self._bdr_c.name();sw=max(1.0,self._bw*1.5)
        shapes={
            "circle":f'<circle cx="50" cy="50" r="35" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "square":f'<rect x="15" y="15" width="70" height="70" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "diamond":f'<polygon points="50,10 90,50 50,90 10,50" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "tri_u":f'<polygon points="50,10 90,80 10,80" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "penta":f'<polygon points="50,8 90,38 75,88 25,88 10,38" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "hexa":f'<polygon points="50,7 87,28 87,72 50,93 13,72 13,28" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "octa":f'<polygon points="30,8 70,8 92,30 92,70 70,92 30,92 8,70 8,30" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "star":f'<polygon points="50,7 60,38 93,38 67,57 77,90 50,70 23,90 33,57 7,38 40,38" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "cross":f'<path d="M35 8H65V35H92V65H65V92H35V65H8V35H35Z" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "cross_x":f'<path d="M18 18L82 82M82 18L18 82" fill="none" stroke="{fc}" stroke-width="12" stroke-linecap="round"/>',
            "arrow":f'<polygon points="50,5 90,45 65,45 65,92 35,92 35,45 10,45" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "heart":f'<path d="M50 90C5 55 10 20 32 20C43 20 49 28 50 33C51 28 57 20 68 20C90 20 95 55 50 90Z" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
            "semi":f'<path d="M12 55A38 38 0 0 1 88 55L50 55Z" fill="{fc}" stroke="{bc}" stroke-width="{sw}"/>',
        }
        body=shapes.get(sid,shapes["circle"])
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">{body}</svg>'

    def _write_kml_icon(self, asset_dir):
        os.makedirs(asset_dir,exist_ok=True)
        name=_safe_asset_name(self._sym_sid)+".png"
        out=os.path.join(asset_dir,name)
        svg=self._kml_symbol_svg()
        if QSvgRenderer is not None:
            try:
                renderer=QSvgRenderer(); renderer.load(QByteArray(svg.encode("utf-8")))
                image=QImage(128,128,QImage.Format.Format_ARGB32)
                image.fill(0)
                painter=QPainter(image);renderer.render(painter);painter.end();image.save(out,"PNG")
                return name
            except Exception:
                pass
        # Fallback keeps a usable local SVG reference if SVG rasterization is unavailable.
        svg_name=_safe_asset_name(self._sym_sid)+".svg"
        open(os.path.join(asset_dir,svg_name),"w",encoding="utf-8").write(svg)
        return svg_name

    def _geom_coords(self,geom,ct):
        g=QgsGeometry(geom)
        try:g.transform(ct)
        except Exception:pass
        if QgsWkbTypes.isSingleType(g.wkbType()):
            pass
        return g

    def _write_kml(self,layer,path):
        """Write a self-contained-style KML plus local icon assets preserving Scratch-X colors/symbols."""
        target=QgsCoordinateReferenceSystem("EPSG:4326")
        ct=QgsCoordinateTransform(layer.crs(),target,QgsProject.instance().transformContext())
        base=os.path.splitext(path)[0]
        asset_dir=base+"_assets"
        icon_name=self._write_kml_icon(asset_dir) if layer.geometryType()==QgsWkbTypes.PointGeometry else None
        fc=QColor(self._fill_c);fc.setAlpha(int((1-self._trans/100.0)*255))
        bc=QColor(self._bdr_c)
        width=max(0.1,float(self._bw))
        style_id="scratchx_style"
        xml=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2">','<Document>',f'<name>{_xml_text(os.path.basename(path))}</name>']
        xml.append(f'<Style id="{style_id}">')
        if layer.geometryType()==QgsWkbTypes.PointGeometry:
            scale=max(0.25,min(3.0,self._sym_size/12.0))
            xml.append(f'<IconStyle><color>ffffffff</color><scale>{scale:.3f}</scale><Icon><href>{_xml_text(os.path.basename(asset_dir))}/{_xml_text(icon_name)}</href></Icon><hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/></IconStyle>')
            xml.append(f'<LabelStyle><scale>0.8</scale></LabelStyle>')
        elif layer.geometryType()==QgsWkbTypes.LineGeometry:
            xml.append(f'<LineStyle><color>{_kml_color(fc)}</color><width>{width:.2f}</width></LineStyle>')
        else:
            xml.append(f'<LineStyle><color>{_kml_color(bc)}</color><width>{width:.2f}</width></LineStyle><PolyStyle><color>{_kml_color(fc)}</color><fill>1</fill><outline>1</outline></PolyStyle>')
        xml.append('</Style>')
        for feat in layer.getFeatures():
            geom=self._geom_coords(feat.geometry(),ct)
            name=feat.attribute("name") or layer.name() or f"Feature {feat.id()}"
            xml.append('<Placemark>')
            xml.append(f'<name>{_xml_text(name)}</name><styleUrl>#{style_id}</styleUrl>')
            if layer.geometryType()==QgsWkbTypes.PointGeometry:
                p=geom.asPoint();xml.append(f'<Point><coordinates>{p.x():.8f},{p.y():.8f},0</coordinates></Point>')
            elif layer.geometryType()==QgsWkbTypes.LineGeometry:
                lines=geom.asMultiPolyline() if QgsWkbTypes.isMultiType(geom.wkbType()) else [geom.asPolyline()]
                if len(lines)==1:
                    coords=" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in lines[0]);xml.append(f'<LineString><tessellate>1</tessellate><coordinates>{coords}</coordinates></LineString>')
                else:
                    xml.append('<MultiGeometry>')
                    for line in lines:
                        coords=" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in line);xml.append(f'<LineString><tessellate>1</tessellate><coordinates>{coords}</coordinates></LineString>')
                    xml.append('</MultiGeometry>')
            else:
                polys=geom.asMultiPolygon() if QgsWkbTypes.isMultiType(geom.wkbType()) else [geom.asPolygon()]
                if len(polys)==1:
                    xml.append('<Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>')
                    xml.append(" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in polys[0][0]));xml.append('</coordinates></LinearRing></outerBoundaryIs>')
                    for ring in polys[0][1:]:xml.append('<innerBoundaryIs><LinearRing><coordinates>'+" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in ring)+'</coordinates></LinearRing></innerBoundaryIs>')
                    xml.append('</Polygon>')
                else:
                    xml.append('<MultiGeometry>')
                    for poly in polys:
                        xml.append('<Polygon><tessellate>1</tessellate><outerBoundaryIs><LinearRing><coordinates>'+" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in poly[0])+'</coordinates></LinearRing></outerBoundaryIs>')
                        for ring in poly[1:]:xml.append('<innerBoundaryIs><LinearRing><coordinates>'+" ".join(f"{p.x():.8f},{p.y():.8f},0" for p in ring)+'</coordinates></LinearRing></innerBoundaryIs>')
                        xml.append('</Polygon>')
                    xml.append('</MultiGeometry>')
            xml.append('</Placemark>')
        xml.extend(['</Document>','</kml>'])
        with open(path,"w",encoding="utf-8") as f:f.write("\n".join(xml))

    def _auto_save(self,layer,path):
        try:
            if os.path.splitext(path)[1].lower()==".kml":
                self._write_kml(layer,path)
                extra=self.tr("Point symbols are stored in the adjacent _assets folder so Google Earth can render the same symbol.","Simbol Point disimpan di folder _assets di sebelah file KML agar Google Earth menampilkan simbol yang sama.") if layer.geometryType()==QgsWkbTypes.PointGeometry else ""
                QMessageBox.information(self,self.tr("Geometry Saved","Geometri Tersimpan"),self.tr(f"Geometry saved to:\n{path}\n\n{extra}",f"Geometri berhasil disimpan ke:\n{path}\n\n{extra}"))
                return
            drv={"shp":"ESRI Shapefile","tab":"MapInfo File","geojson":"GeoJSON"}.get(os.path.splitext(path)[1].lstrip('.').lower(),"ESRI Shapefile")
            opts=QgsVectorFileWriter.SaveVectorOptions();opts.driverName=drv;opts.fileEncoding="UTF-8";err=QgsVectorFileWriter.writeAsVectorFormatV3(layer,path,QgsProject.instance().transformContext(),opts);code=err[0] if isinstance(err,(tuple,list)) else err;msg=err[1] if isinstance(err,(tuple,list)) and len(err)>1 else ""
            if code==QgsVectorFileWriter.NoError:QMessageBox.information(self,self.tr("Geometry Saved","Geometri Tersimpan"),self.tr(f"Geometry saved to:\n{path}",f"Geometri berhasil disimpan ke:\n{path}"))
            else:QMessageBox.critical(self,self.tr("Save Failed","Gagal Simpan"),f"{msg}\n\n{path}")
        except Exception as e:QMessageBox.critical(self,self.tr("Save Error","Error Simpan"),str(e))
    def _clear_temp_layers(self):
        project=QgsProject.instance();removed=0
        # Clear all Scratch-X temporary layers in the current project, including
        # layers created by an earlier dialog instance. Saved-to-file layers are never touched.
        ids=set(self._temp_layer_ids)
        for layer in project.mapLayers().values():
            try:
                if layer.customProperty("ScratchX/temporary", False) is True or layer.customProperty("ScratchX/temporary", False) == "true":
                    ids.add(layer.id())
            except Exception:
                pass
        for lid in list(ids):
            if project.mapLayer(lid):
                project.removeMapLayer(lid);removed+=1
        self._temp_layer_ids=[]
        if self._active_tool:
            try:self.iface.mapCanvas().unsetMapTool(self._active_tool)
            except Exception:pass
            self._active_tool=None
        self.iface.statusBarIface().showMessage(self.tr(f"Scratch-X: {removed} temporary layer(s) cleared.",f"Scratch-X: {removed} layer temporary dibersihkan."))
    def _load_custom_symbols(self):
        raw=self.settings.value("custom_symbols",{})
        if isinstance(raw,dict):return raw
        return {}
    def _save_custom_symbols(self):self.settings.setValue("custom_symbols",self._custom_symbols)
    def _save_settings(self):
        self.settings.setValue("language",self.lang);self.settings.setValue("fill_color",self._fill_c.name());self.settings.setValue("border_color",self._bdr_c.name());self.settings.setValue("transparency",self._trans);self.settings.setValue("line_width",self._bw);self.settings.setValue("symbol_size",self._sym_size);self.settings.setValue("line_style",self._ls);self.settings.setValue("symbol",self._sym_sid);self.settings.setValue("shape",self._shape);self.settings.setValue("format",self._fmt);self.settings.setValue("line_mode",self._line_mode);self.settings.setValue("width",max(390,min(620,self.width())));self.settings.setValue("height",max(540,min(820,self.height())));self.settings.setValue("layout_version","3.1.7");self._save_custom_symbols()
    def closeEvent(self,event):self._save_settings();event.accept()
    def hideEvent(self,event):self._save_settings();super().hideEvent(event)
    def _show_help(self):
        title=self.tr("How To","Cara Menggunakan");text=("<h3>How to use Scratch-X</h3><ol><li>Select Geometry.</li><li>Configure Style.</li><li>Choose a format and optionally select a file path.</li><li>Click Create Layer.</li><li>Draw directly on the QGIS canvas.</li><li>Press ESC to cancel the current drawing.</li></ol><b>Line / LineString:</b> Line creates a 2-point feature. LineString creates a multi-vertex route; double-click finishes. Live segment, route and cumulative distance are shown.<br><b>Circle:</b> draw from the center; the radius is shown dynamically.<br><b>Point:</b> choose a symbol, More Symbols, or load custom SVG symbols.<br><b>Polygon:</b> click vertices and double-click to finish.<br><b>Save:</b> after Create Layer, the next geometry always resets to Temporary Layer." if self.lang=="en" else "<h3>Cara menggunakan Scratch-X</h3><ol><li>Pilih Geometri.</li><li>Atur Style.</li><li>Pilih format dan, bila perlu, pilih lokasi file.</li><li>Klik Buat Layer.</li><li>Gambar langsung di kanvas QGIS.</li><li>Tekan ESC untuk membatalkan gambar yang sedang berjalan.</li></ol><b>Line / LineString:</b> Line membuat feature 2 titik. LineString membuat rute dengan banyak titik; double-click untuk selesai. Segment, route dan total kumulatif tampil dinamis.<br><b>Circle:</b> gambar dari titik tengah; radius tampil dinamis.<br><b>Point:</b> pilih simbol, Simbol Lainnya, atau muat SVG custom.<br><b>Polygon:</b> klik titik-titik lalu double-click untuk selesai.<br><b>Simpan:</b> setelah Buat Layer, geometri berikutnya selalu kembali ke Temporary Layer.")
        m=QMessageBox(self);m.setWindowTitle(title);m.setTextFormat(Qt.RichText);m.setText(text);m.setStandardButtons(QMB_OK);m.exec()
    def _show_about(self):AboutDialog(self.lang,self.VERSION,self).exec()
