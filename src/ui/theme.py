"""Theming: dark / light palettes with runtime switching.

Islamic green accent colour palette, same structural pattern as seko_cyber.
"""
from __future__ import annotations

# ---- shared semantic colours (cross-theme) --------------------------------
FAJR_COLOR    = "#818cf8"   # indigo   – pre-dawn
SUNRISE_COLOR = "#f59e0b"   # amber    – sunrise
DHUHA_COLOR   = "#fde047"   # yellow   – mid-morning
DHUHR_COLOR   = "#22c55e"   # green    – midday
ASR_COLOR     = "#38bdf8"   # sky      – afternoon
MAGHRIB_COLOR = "#f97316"   # orange   – sunset
ISHA_COLOR    = "#8b5cf6"   # violet   – night
GOOD          = "#22c55e"
WARN          = "#f59e0b"
DANGER        = "#ef4444"

PRAYER_COLORS = {
    "Fajr":    FAJR_COLOR,
    "Sunrise": SUNRISE_COLOR,
    "Dhuha":   DHUHA_COLOR,
    "Dhuhr":   DHUHR_COLOR,
    "Asr":     ASR_COLOR,
    "Maghrib": MAGHRIB_COLOR,
    "Isha":    ISHA_COLOR,
}

PALETTES: dict[str, dict[str, str]] = {
    "dark": {
        "BG":         "#0d1117",
        "SURFACE":    "#161b22",
        "SURFACE_2":  "#1c2128",
        "BORDER":     "#30363d",
        "TEXT":       "#e6edf3",
        "MUTED":      "#8b949e",
        "ACCENT":     "#4ade80",
        "ACCENT_DK":  "#16a34a",
        "HEADING":    "#ffffff",
        "BTN_HOVER":  "#21262d",
        "BTN_PRESSED":"#1a1f26",
        "SCROLL_HOVER":"#484f58",
        "DANGER_BG":  "#7f1d1d",
    },
    "light": {
        "BG":         "#f2fbf4",   # very faint mint instead of plain grey
        "SURFACE":    "#ffffff",   # pure white cards
        "SURFACE_2":  "#e6f4ea",   # soft green tint instead of grey
        "BORDER":     "#b8dfc0",   # green-tinted border instead of grey
        "TEXT":       "#1a2e1c",   # dark with subtle green
        "MUTED":      "#5a7360",   # green-grey muted instead of plain grey
        "ACCENT":     "#16a34a",
        "ACCENT_DK":  "#15803d",
        "HEADING":    "#0d1f0f",   # very dark green-black
        "BTN_HOVER":  "#d4edda",   # light green hover instead of grey
        "BTN_PRESSED":"#b8dfc0",   # green pressed
        "SCROLL_HOVER":"#8ec99a",  # green scroll bar
        "DANGER_BG":  "#b91c1c",
    },
}

# Module-level names updated by apply_theme()
BG = SURFACE = SURFACE_2 = BORDER = TEXT = MUTED = ACCENT = ACCENT_DK = ""
HEADING = BTN_HOVER = BTN_PRESSED = SCROLL_HOVER = DANGER_BG = ""
ACTIVE = "dark"
STYLESHEET = ""
FONT_SIZE = 13   # updated by apply_font_size() / apply_theme()


def _build_stylesheet() -> str:
    fs = FONT_SIZE
    return f"""
QWidget {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: {fs}px;
}}
QLabel {{ background: transparent; }}
QLabel#H1 {{ font-size: {fs + 11}px; font-weight: 700; color: {HEADING}; }}
QLabel#H2 {{ font-size: {fs + 5}px; font-weight: 600; color: {HEADING}; }}
QLabel#Muted {{ color: {MUTED}; font-size: {max(10, fs - 1)}px; }}
QCheckBox, QRadioButton {{ background: transparent; }}
QGroupBox {{
    border: 1px solid {BORDER}; border-radius: 10px;
    margin-top: 14px; font-weight: 600; color: {MUTED};
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 12px; padding: 0 4px;
}}

/* Sidebar */
QFrame#Sidebar {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}
QPushButton#NavButton {{
    background: transparent; border: none; border-radius: 9px;
    text-align: left; padding: 0; margin: 2px 0;
}}
QPushButton#NavButton:hover  {{ background: {SURFACE_2}; }}
QPushButton#NavButton:checked {{ background: {ACCENT_DK}; }}

/* Cards */
QFrame#Card {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px;
}}
QFrame#PrayerCard {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 14px;
}}
QFrame#PrayerCard[active="true"] {{
    border: 2px solid {ACCENT_DK};
    background: {SURFACE_2};
}}
QFrame#NextPrayerBanner {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

/* Inputs */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {{
    background: {SURFACE_2}; border: 1px solid {BORDER}; border-radius: 8px;
    padding: 8px 10px; selection-background-color: {ACCENT_DK}; color: {TEXT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {ACCENT};
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {SURFACE_2}; border: 1px solid {BORDER};
    selection-background-color: {ACCENT_DK}; color: {TEXT};
}}

/* Buttons */
QPushButton {{
    background: {SURFACE_2}; border: 1px solid {BORDER}; border-radius: 8px;
    padding: 9px 16px; color: {TEXT};
}}
QPushButton:hover   {{ background: {BTN_HOVER}; border-color: {ACCENT_DK}; }}
QPushButton:pressed {{ background: {BTN_PRESSED}; }}
QPushButton:disabled {{ color: {MUTED}; }}
QPushButton#Primary {{
    background: {ACCENT_DK}; border: none; color: #ffffff; font-weight: 600;
}}
QPushButton#Primary:hover {{ background: {ACCENT}; }}
QPushButton#Danger  {{ background: {DANGER_BG}; border: none; color: #ffffff; }}
QPushButton#Danger:hover  {{ background: {DANGER}; }}

/* Toggle switch styled as flat btn */
QPushButton#AlarmOn {{
    background: {ACCENT_DK}; border: none; border-radius: 6px;
    color: #ffffff; font-size: 12px; padding: 4px 10px;
}}
QPushButton#AlarmOn:hover {{ background: {ACCENT}; }}
QPushButton#AlarmOff {{
    background: transparent; border: 1px solid {BORDER}; border-radius: 6px;
    color: {MUTED}; font-size: 12px; padding: 4px 10px;
}}
QPushButton#AlarmOff:hover {{ background: {BTN_HOVER}; }}

/* Dzikir counter button */
QPushButton#DzikirBtn {{
    background: rgba(22,163,74,0.09); border: 2px solid rgba(22,163,74,0.30);
    border-radius: 12px; padding: 16px; color: {ACCENT};
    font-size: {fs + 4}px; font-weight: 700;
}}
QPushButton#DzikirBtn:hover {{ background: rgba(22,163,74,0.18); border-color: {ACCENT}; }}
QPushButton#DzikirBtn:pressed {{ background: {ACCENT_DK}; color: #ffffff; }}
QPushButton#DzikirDone {{
    background: {ACCENT_DK}; border: none; border-radius: 12px;
    padding: 16px; color: #ffffff; font-size: {fs + 4}px; font-weight: 700;
}}

/* Tables */
QTableWidget, QTableView {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;
    gridline-color: {BORDER}; selection-background-color: {ACCENT_DK};
}}
QHeaderView::section {{
    background: {SURFACE_2}; color: {MUTED}; padding: 8px; border: none;
    border-bottom: 1px solid {BORDER}; font-weight: 600;
}}
QTableWidget::item {{ padding: 6px; }}

/* Progress */
QProgressBar {{
    background: {SURFACE_2}; border: 1px solid {BORDER}; border-radius: 8px;
    text-align: center; height: 14px; color: {TEXT}; font-size: 11px;
}}
QProgressBar::chunk {{ background: {ACCENT_DK}; border-radius: 7px; }}

/* Scrollbars */
QScrollBar:vertical   {{ background: {BG}; width: 12px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 6px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {SCROLL_HOVER}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollArea {{ border: none; }}

/* Tabs */
QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 8px; top: -1px; }}
QTabBar::tab {{
    background: {SURFACE}; color: {MUTED}; padding: 8px 16px;
    border: 1px solid {BORDER}; border-bottom: none;
    border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px;
}}
QTabBar::tab:selected {{ background: {SURFACE_2}; color: {TEXT}; }}

QToolTip {{
    background: {SURFACE_2}; color: {TEXT}; border: 1px solid {BORDER};
    padding: 4px 8px; border-radius: 6px;
}}
QCheckBox {{ spacing: 8px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border: 1px solid {BORDER};
    border-radius: 4px; background: {SURFACE_2};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT_DK}; border-color: {ACCENT_DK};
}}
"""


def apply_theme(name: str, font_size: int | None = None) -> str:
    global BG, SURFACE, SURFACE_2, BORDER, TEXT, MUTED, ACCENT, ACCENT_DK
    global HEADING, BTN_HOVER, BTN_PRESSED, SCROLL_HOVER, DANGER_BG, STYLESHEET, ACTIVE, FONT_SIZE
    pal = PALETTES.get(name, PALETTES["dark"])
    ACTIVE     = name if name in PALETTES else "dark"
    BG         = pal["BG"];    SURFACE   = pal["SURFACE"]; SURFACE_2 = pal["SURFACE_2"]
    BORDER     = pal["BORDER"]; TEXT     = pal["TEXT"];    MUTED     = pal["MUTED"]
    ACCENT     = pal["ACCENT"]; ACCENT_DK = pal["ACCENT_DK"]; HEADING = pal["HEADING"]
    BTN_HOVER  = pal["BTN_HOVER"]; BTN_PRESSED = pal["BTN_PRESSED"]
    SCROLL_HOVER = pal["SCROLL_HOVER"]; DANGER_BG = pal["DANGER_BG"]
    if font_size is not None:
        FONT_SIZE = font_size
    STYLESHEET = _build_stylesheet()
    return STYLESHEET


def apply_font_size(size: int) -> str:
    """Update font size and rebuild stylesheet without changing theme."""
    global FONT_SIZE, STYLESHEET
    FONT_SIZE = size
    STYLESHEET = _build_stylesheet()
    return STYLESHEET


def resolve_system_theme() -> str:
    """Return 'dark' or 'light' based on system setting."""
    import sys
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"
        except Exception:
            pass
    return "dark"


apply_theme("dark")
