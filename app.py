# -*- coding: utf-8 -*-
"""
================================================================================
TRỢ LÝ AI QUẢNG CÁO & IN ẤN - V4 (tích hợp Gemini thật)
Chạy: streamlit run app.py
Khoá API: đặt GEMINI_API_KEY MỘT LẦN trong Streamlit Cloud > Settings > Secrets.
          Khách vào bằng Chrome dùng luôn, KHÔNG phải nhập khoá hay đăng nhập.
          Không có khoá / hết lượt AI vẫn chạy: bộ đọc yêu cầu, tối ưu prompt, slogan,
          chat FAQ, tính LED, báo giá Excel đều có chế độ offline.
================================================================================
"""
import io
import json
import math
import re
import textwrap
import threading
from datetime import datetime, timedelta, timezone
from fractions import Fraction

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Trợ lý AI Quảng cáo & In ấn v4", page_icon="🖨️", layout="wide")

# ==============================================================================
# 0. DỮ LIỆU CẤU HÌNH
# ==============================================================================
PRODUCTS = {  # tên ấn phẩm: (rộng cm, cao cm)
    "Biển hiệu (Signboard)": (320.0, 96.0),
    "Standee (Cuốn / Khung X)": (60.0, 160.0),
    "Bảng vẫy (Hanging Sign)": (100.0, 100.0),
    "Băng rôn (Banner)": (500.0, 100.0),
    "Menu (Bảng giá)": (21.0, 29.7),
    "Tem nhãn Decal": (10.0, 10.0),
}
STYLES = ["Hiện đại & Trẻ trung", "Sang trọng & VIP", "Cổ điển / Vintage", "Tối giản & Tinh tế", "Nổi bật & Rực rỡ"]
MATERIALS = {
    "Bảng LED Module": "outdoor LED matrix module display board, bright illuminated text and graphics, waterproof aluminum cabinet frame",
    "Nhôm Tổ Ong (Aluminum Honeycomb)": "ultra-flat premium aluminum honeycomb panels, seamless metallic joint lines, modern metallic finish, 3D raised letters",
    "Alu + Mica nổi đèn LED": "aluminum composite panel with 3D raised acrylic mica lettering, glowing internal LED illumination",
    "Inox mạ vàng 3D + Neon": "luxurious 3D gold mirror stainless steel letters, backlit warm neon halo glow",
    "Bạt Hiflex / Flex Banner": "heavy-duty outdoor vinyl flex banner, vivid printed graphics, matte finish",
    "Bạt Không Gân Khung Sắt": "seamless high-definition flex banner stretched taut on square iron frame",
    "Gỗ Vintage / Khắc Laser": "rustic polished dark wood board with laser-engraved typography, warm amber lighting",
    "Decal Sắc Nét / Màng Mờ": "ultra-sharp die-cut vinyl sticker sheet, premium matte lamination, vibrant colors",
}
LED_SPECS = {  # module 32x16cm
    "P10 Outdoor": dict(w=32, h=16, px_w=32, px_h=16, pmax=30, pavg=18),
    "P5 Outdoor": dict(w=32, h=16, px_w=64, px_h=32, pmax=32, pavg=20),
    "P3.08 Indoor": dict(w=32, h=16, px_w=104, px_h=52, pmax=25, pavg=15),
    "P2.5 Indoor": dict(w=32, h=16, px_w=128, px_h=64, pmax=25, pavg=15),
}
ROUND_MODES = ["Làm tròn gần nhất", "Làm tròn lên (đủ kích thước)"]
NEGATIVE = ("blurry text, distorted logo, misspelled letters, misaligned layout, low resolution, "
            "crowded text at bottom edge, chaotic layout, dark illegible background")

PROMPTS = {  # khoá = tên ấn phẩm bỏ phần trong ngoặc
    "Biển hiệu": "Commercial storefront outdoor signboard design for '{brand}'. Text reads '{title}'. Color theme: {colors}. Style: {style}, modern facade background, eye-level street view. Made of {mat}. Layout: bold logo on left, large centered title, services '{sub}' and phone '{contact}' clearly readable in footer. Professional advertising design, clean grid alignment, photorealistic 8k render.",
    "Standee": "Vertical roll-up standee banner design for '{brand}'. Promoting '{title}'. Details: '{sub}'. Colors: {colors}. Style: {style}. Made with {mat}. Layout: top 20% bold '{brand}' logo, middle hero illustration with headline '{title}', lower section contact '{contact}', bottom 15% left clear for the standee base. Clean corporate marketing design, high contrast, studio lighting.",
    "Bảng vẫy": "Double-sided outdoor hanging blade sign on a shop exterior wall. Brand '{brand}', icon/title '{title}'. Palette: {colors}. Style: {style}. Material: {mat}, on ornate wrought iron bracket. Glowing LED edge lighting, high day/night visibility, photorealistic street view.",
    "Băng rôn": "Wide horizontal outdoor promotional banner for '{brand}'. Title '{title}'. Key message '{sub}'. Palette: {colors}. Style: {style}, energetic and eye-catching. Material: {mat}. Huge bold type readable from 50 meters, prominent offer box, hotline '{contact}' in a footer box. Print-ready, sharp vector graphics.",
    "Menu": "Professional food and beverage menu board for '{brand}'. Title '{title}'. Items: '{sub}'. Colors: {colors}. Style: {style}. Header with logo, structured 2-column item list with elegant prices, appetizing hero food photos. Print-ready, immaculate typography, clear hierarchy.",
    "Tem nhãn Decal": "Die-cut packaging sticker label design for '{brand}'. Product '{title}'. Info '{sub}'. Colors: {colors}. Style: {style}. Finish: {mat}. Central product illustration, sharp logo on top, clear cutlines, high-contrast readable text. Flat lay mockup on neutral surface, ultra-detailed vector render.",
}

TOOLKIT = [
    ("Dựng phối cảnh 3D từ phác thảo 2D", "Photorealistic 3D architectural mockup of a store signboard based on a 2D flat sketch. Convert the flat layout into 3D acrylic letters 5cm deep on a dark textured aluminum composite wall. Eye-level street view, natural sunlight, subtle drop shadows."),
    ("Mockup sản phẩm thực tế", "Professional realistic product mockup of {x} inside a modern brightly lit retail showroom. Soft studio light, shallow depth of field, realistic reflections, 8k."),
    ("Biển hiệu ban đêm / LED / Neon", "Nighttime urban street photo of a glowing store signboard for {x}. Backlit LED halo around 3D stainless channel letters and an outdoor LED matrix panel. Twilight, wet pavement reflections, cinematic lighting."),
    ("Mô phỏng chất liệu thi công", "Close-up macro photo of advertising materials for {x}: 3D gold mirror stainless letters on matte black aluminum honeycomb panels with an LED display. Crisp metallic reflections, tactile texture detail, 8k."),
    ("Chuẩn hoá ghi chú tay thành bố cục", "Clean graphic layout extracted from handwritten customer notes for {x}. Crisp typography hierarchy, aligned grid, bold branding, white background, print-ready."),
]

# ==============================================================================
# 1. TÍNH TOÁN
# ==============================================================================
def calc_led(w, h, mod="P10 Outdoor", mode=ROUND_MODES[0]):
    s = LED_SPECS.get(mod, LED_SPECS["P10 Outdoor"])
    rnd = math.ceil if mode == ROUND_MODES[1] else (lambda x: math.floor(x + 0.5))
    cols, rows = max(1, int(rnd(w / s["w"]))), max(1, int(rnd(h / s["h"])))
    n = cols * rows
    pxw, pxh = cols * s["px_w"], rows * s["px_h"]
    pmax = n * s["pmax"]
    pix = pxw * pxh
    if pix <= 65536:
        card = "Card HD-WF2 / HD-WF4 (Wifi, điều khiển bằng điện thoại/PC)"
    elif pix <= 262144:
        card = "Card HD-C16C / Novastar / Linsn (USB/LAN/Wifi)"
    else:
        card = "Bộ xử lý hình ảnh LED (vd HD-VP210) + card nhận"
    return dict(mod=mod, cols=cols, rows=rows, aw=cols * s["w"], ah=rows * s["h"], n=n,
                pxw=pxw, pxh=pxh, pix=pix, pmax=pmax, pavg=n * s["pavg"],
                psu=max(1, math.ceil(pmax / 160.0)),  # nguồn 5V40A=200W chạy 80% tải
                card=card, area=cols * s["w"] * rows * s["h"] / 10000)


def aspect_ratio(w, h):
    f = Fraction(min(max(w / h, 1 / 8), 8)).limit_denominator(12)
    return f"{f.numerator}:{f.denominator}"


def fmt(n):
    return f"{int(round(n)):,}".replace(",", ".")


def to_excel(sheets):
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)
    return bio.getvalue()


# ==============================================================================
# 2. SƠ ĐỒ BỐ CỤC (trả về bytes PNG)
# ==============================================================================
@st.cache_data(show_spinner=False)
def make_wireframe(product, w, h, brand, title, contact, sub, material, led_mod, led_mode):
    led = None
    if material.startswith("Bảng LED"):
        led = calc_led(w, h, led_mod, led_mode)
        w, h = led["aw"], led["ah"]
    fig, ax = plt.subplots(figsize=(8, min(max(8 * h / w, 3), 11)), dpi=120)
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_xlim(-0.1 * w, 1.1 * w)
    ax.set_ylim(-0.1 * h, 1.1 * h)
    ax.set_aspect("equal")
    mx, my = w * 0.05, h * 0.05
    nn = lambda bw: max(8, int(bw / w * 42))

    def B(x, y, bw, bh, fc, ec, a=0.75, ls="-"):
        ax.add_patch(patches.Rectangle((x, y), bw, bh, fc=fc, ec=ec, lw=1.2, alpha=a, ls=ls, zorder=3))

    def T(x, y, s, color, fs=9, n=None):
        if n:
            s = "\n".join(textwrap.fill(l, n) for l in s.split("\n"))
        ax.text(x, y, s, color=color, fontsize=fs, fontweight="bold", ha="center", va="center", zorder=4)

    ax.add_patch(patches.Rectangle((0, 0), w, h, lw=2.5, ec="#1E293B", fc="#F1F5F9", zorder=1))
    ax.add_patch(patches.Rectangle((mx, my), w - 2 * mx, h - 2 * my, lw=1, ec="#94A3B8", fc="none", ls="--", zorder=2))
    kind = product.split(" (")[0]

    if led:
        mw, mh = w / led["cols"], h / led["rows"]
        if led["n"] <= 400:
            for i in range(led["cols"]):
                for j in range(led["rows"]):
                    B(i * mw, j * mh, mw, mh, "#E0F2FE", "#3B82F6", 0.5)
        else:  # bảng rất lớn: vẽ 1 khối cho nhẹ
            B(0, 0, w, h, "#E0F2FE", "#3B82F6", 0.5)
        T(w / 2, h * 0.62, f"BẢNG LED {led['mod'].upper()}: {led['cols']} CỘT x {led['rows']} HÀNG\n({led['n']} module 32x16cm)", "#1E40AF", 10, nn(w))
        T(w / 2, h * 0.36, f'NỘI DUNG: "{title}"\n{brand} - {contact}', "#0369A1", 9, nn(w))
    elif kind == "Standee":
        bc = min(max(h * 0.15, 30), h * 0.3)
        B(0, 0, w, bc, "#FEE2E2", "#EF4444", 0.6)
        T(w / 2, bc / 2, "VÙNG AN TOÀN CHÂN STANDEE\n(Không đặt thông tin quan trọng)", "#991B1B", 8, nn(w))
        B(mx, h * 0.8, w - 2 * mx, h * 0.15, "#DBEAFE", "#3B82F6")
        T(w / 2, h * 0.875, f"LOGO & THƯƠNG HIỆU\n[{brand.upper()}]", "#1E40AF", 10, nn(w - 2 * mx))
        B(mx, bc + h * 0.12, w - 2 * mx, h - bc - h * 0.35, "#FEF3C7", "#F59E0B", 0.6)
        T(w / 2, (h + bc) / 2, f'HÌNH CỐT LÕI & TIÊU ĐỀ\n"{title}"\n{sub}', "#92400E", 9, nn(w - 2 * mx))
        B(mx, bc + 2, w - 2 * mx, h * 0.09, "#DCFCE7", "#22C55E")
        T(w / 2, bc + 2 + h * 0.045, f"HOTLINE: {contact}", "#166534", 8, nn(w - 2 * mx))
    elif kind in ("Biển hiệu", "Băng rôn"):
        lw_ = w * 0.22
        tw = w - lw_ - 3 * mx
        B(mx, my, lw_, h - 2 * my, "#DBEAFE", "#3B82F6")
        T(mx + lw_ / 2, h / 2, f"LOGO\n{brand}", "#1E40AF", 9, nn(lw_))
        B(2 * mx + lw_, h * 0.35, tw, h * 0.55 - my, "#FEF3C7", "#F59E0B")
        T(2 * mx + lw_ + tw / 2, h * 0.625, f'TÊN CỬA HÀNG / TIÊU ĐỀ\n"{title.upper()}"\n{sub}', "#92400E", 10, nn(tw))
        B(2 * mx + lw_, my, tw, h * 0.28, "#DCFCE7", "#22C55E")
        T(2 * mx + lw_ + tw / 2, my + h * 0.14, f"LIÊN HỆ & DỊCH VỤ\n{contact}", "#166534", 8, nn(tw))
    elif kind == "Bảng vẫy":
        r = min(w, h) * 0.42
        ax.add_patch(patches.Circle((w / 2, h / 2), r, lw=2, ec="#0EA5E9", fc="#E0F2FE", zorder=3))
        T(w / 2, h / 2 + r * 0.35, f"[{brand.upper()}]", "#0369A1", 11, nn(r * 1.6))
        T(w / 2, h / 2, f'BIỂU TƯỢNG / DỊCH VỤ\n"{title}"', "#0284C7", 9, nn(r * 1.6))
        T(w / 2, h / 2 - r * 0.4, f"SĐT: {contact}", "#075985", 8, nn(r * 1.6))
    elif kind == "Menu":
        B(mx, h * 0.82, w - 2 * mx, h * 0.13, "#E0E7FF", "#6366F1", 0.8)
        T(w / 2, h * 0.885, f'THỰC ĐƠN - {brand.upper()}\n"{title}"', "#3730A3", 10, nn(w))
        items = [l.strip() for l in sub.split("\n") if l.strip()] or ["Món 1 ..... 50k", "Món 2 ..... 75k", "Món 3 ..... 90k", "Món 4 ..... 35k"]
        cw, bh = (w - 3 * mx) / 2, h * 0.72 - my
        for k, col in enumerate((items[0::2], items[1::2])):
            x = mx + k * (cw + mx)
            B(x, my + h * 0.08, cw, bh - h * 0.08, "#F1F5F9", "#94A3B8", 0.6)
            T(x + cw / 2, h * 0.45, "\n".join(col) or "...", "#334155", 8, nn(cw))
        T(w / 2, my + h * 0.03, f"Hotline: {contact}", "#64748B", 7)
    else:
        rx, ry = w * 0.4, h * 0.4
        B(w / 2 - rx, h / 2 - ry, 2 * rx, 2 * ry, "#FCE7F3", "#EC4899", 1)
        T(w / 2, h / 2 + ry * 0.5, brand.upper(), "#BE185D", 10, nn(2 * rx))
        T(w / 2, h / 2, f"{title}\n{sub}", "#9D174D", 9, nn(2 * rx))
        T(w / 2, h / 2 - ry * 0.5, f"HSD / Hotline: {contact}", "#831843", 7, nn(2 * rx))

    ax.annotate("", xy=(0, -my * 0.5), xytext=(w, -my * 0.5), arrowprops=dict(arrowstyle="<->", color="#0F172A", lw=1.2))
    ax.text(w / 2, -my * 0.8, f"Rộng: {w:g} cm", ha="center", va="top", fontsize=9, fontweight="bold", color="#0F172A")
    ax.annotate("", xy=(-mx * 0.5, 0), xytext=(-mx * 0.5, h), arrowprops=dict(arrowstyle="<->", color="#0F172A", lw=1.2))
    ax.text(-mx * 0.8, h / 2, f"Cao: {h:g} cm", ha="right", va="center", fontsize=9, fontweight="bold", color="#0F172A", rotation=90)
    ax.set_title(f"SƠ ĐỒ BỐ CỤC: {product.upper()}\n{w:g}x{h:g} cm | {material}", fontsize=10, fontweight="bold", pad=12, color="#1E293B")
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


# ==============================================================================
# 3. PROMPT ENGINE
# ==============================================================================
def build_prompt(product, w, h, brand, title, colors, style, material, contact, sub, led_mod):
    mat = MATERIALS.get(material, "")
    if material.startswith("Bảng LED"):
        mat = f"{led_mod} " + mat
    ctx = dict(brand=brand, title=title, colors=colors, style=style, mat=mat, contact=contact, sub=sub.replace("\n", ", "))
    p = PROMPTS.get(product.split(" (")[0], PROMPTS["Tem nhãn Decal"]).format(**ctx)
    ar = aspect_ratio(w, h)
    return dict(prompt=p, ar=ar, negative=NEGATIVE)


def engine_text(d, engine):
    if engine == "Midjourney":
        return f"/imagine prompt: {d['prompt']} --ar {d['ar']} --no blurry text, distorted logo"
    return f"{d['prompt']} Aspect ratio {d['ar']}. Avoid: {d['negative']}."


# ==============================================================================
# 4. GEMINI + CHẾ ĐỘ KHÔNG CẦN KHOÁ
#    - Khoá nằm trong Secrets của chủ xưởng -> khách vào Chrome dùng luôn, không nhập gì.
#    - Có giới hạn lượt AI để không cháy hạn mức; hết lượt / không có khoá thì tự
#      chuyển sang bộ xử lý offline (không gọi Gemini).
# ==============================================================================
TEXT_FALLBACK = ["gemini-3-flash-preview"]
VN_TZ = timezone(timedelta(hours=7))
GATE_MSG = {
    "no_key": "Chưa cài khoá Gemini nên đang dùng chế độ không cần AI.",
    "session": "Bạn đã dùng hết lượt AI miễn phí của phiên này.",
    "daily": "Hôm nay lượt AI dùng chung đã hết, mai thử lại nhé.",
}


def _secret(name, default=""):
    try:
        v = st.secrets.get(name, default)
        return default if v in (None, "") else v
    except Exception:
        return default


def api_key():
    return (st.session_state.get("api_key_in") or "").strip() or str(_secret("GEMINI_API_KEY"))


def using_own_key():
    return bool((st.session_state.get("api_key_in") or "").strip())


@st.cache_resource
def _usage():
    return {"day": "", "count": 0, "lock": threading.Lock()}


def _limit(name, default):
    try:
        return int(_secret(name, default))
    except (TypeError, ValueError):
        return default


def ai_gate(weight=1):
    """(True, '') nếu được gọi AI (và trừ hạn mức); ngược lại (False, mã lý do)."""
    if not api_key():
        return False, "no_key"
    if using_own_key():
        return True, ""
    u = _usage()
    today = datetime.now(VN_TZ).strftime("%Y-%m-%d")
    with u["lock"]:
        if u["day"] != today:
            u["day"], u["count"] = today, 0
        if st.session_state.get("ai_used", 0) + weight > _limit("AI_SESSION_LIMIT", 30):
            return False, "session"
        if u["count"] + weight > _limit("AI_DAILY_LIMIT", 300):
            return False, "daily"
        u["count"] += weight
    st.session_state.ai_used = st.session_state.get("ai_used", 0) + weight
    return True, ""


def friendly_err(e):
    s = str(e)
    if "429" in s or "RESOURCE_EXHAUSTED" in s:
        return "Hạn mức Gemini đang hết, thử lại sau ít phút."
    if "API key" in s or "401" in s or "403" in s or "PERMISSION_DENIED" in s:
        return "API Key không hợp lệ hoặc chưa có quyền dùng model này."
    if "404" in s or "NOT_FOUND" in s:
        return "Không tìm thấy model - đổi tên model ở mục Nâng cao."
    return s[:250]


@st.cache_resource
def _client_for(key):
    # Giữ client sống lâu: nếu tạo mới mỗi lần, Python dọn bộ nhớ làm client đóng giữa chừng ("client has been closed")
    from google import genai
    return genai.Client(api_key=key)


def _client():
    return _client_for(api_key())


def ai_text(prompt, system=None, image=None, as_json=False):
    from google.genai import types
    cfg = types.GenerateContentConfig(system_instruction=system, temperature=0.6,
                                      response_mime_type="application/json" if as_json else "text/plain")
    contents = [image, prompt] if image is not None else [prompt]
    last = None
    for m in dict.fromkeys(x for x in [st.session_state.text_model, *TEXT_FALLBACK] if x):
        try:
            r = _client().models.generate_content(model=m, contents=contents, config=cfg)
            return (r.text or "").strip()
        except Exception as e:  # chỉ thử model dự phòng khi sai tên model
            last = e
            if "404" not in str(e) and "NOT_FOUND" not in str(e):
                raise
    raise last


def ai_image(prompt, ref=None):
    from google.genai import types
    contents = [ref, prompt] if ref is not None else [prompt]
    r = _client().models.generate_content(
        model=st.session_state.image_model, contents=contents,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]))
    for part in (r.candidates[0].content.parts if r.candidates else []):
        if getattr(part, "inline_data", None) and part.inline_data.data:
            return Image.open(io.BytesIO(part.inline_data.data))
    raise RuntimeError("Gemini không trả về ảnh (có thể bị bộ lọc an toàn chặn, hoặc model ảnh cần tài khoản trả phí).")


# ---------- Bộ xử lý OFFLINE (không cần khoá, không gọi mạng) ----------
def _num(s):
    return float(s.replace(",", "."))


def _cm(v, unit):
    v = _num(v)
    if unit in ("m", "mét"):
        return v * 100
    if unit == "cm":
        return v
    return v * 100 if v <= 30 else v


def offline_parse(txt):
    d, t = {}, txt.lower()
    ph = re.search(r"(?<!\d)(?:\+?84|0)(?:[\s.\-]?\d){8,10}(?!\d)", txt)
    if ph:
        d["contact"] = ph.group(0).strip()
    for key, pat in (("Standee (Cuốn / Khung X)", r"\bstandee\b"), ("Băng rôn (Banner)", r"băng[\s-]?rôn|\bbanner\b"),
                     ("Bảng vẫy (Hanging Sign)", r"[bB]ảng vẫy|biển vẫy"), ("Menu (Bảng giá)", r"\bmenu\b|thực đơn|bảng giá"),
                     ("Biển hiệu (Signboard)", r"\bbiển\b"), ("Tem nhãn Decal", r"\b(?:tem|nhãn|decal)\b")):
        if re.search(pat, t):
            d["p_type"] = key
            break
    n = r"(\d+(?:[.,]\d+)?)"
    m = re.search(n + r"\s*(cm|mét|m)?\s*[x×*]\s*" + n + r"\s*(cm|mét|m)?\b", t)
    if m:
        u = m.group(4) or m.group(2)
        d["width"], d["height"] = _cm(m.group(1), m.group(2) or u), _cm(m.group(3), u)
    else:
        mw = re.search(r"(?:ngang|rộng|dài)\s*" + n + r"\s*(cm|mét|m)?\b", t)
        mh = re.search(r"cao\s*" + n + r"\s*(cm|mét|m)?\b", t)
        if mw:
            d["width"] = _cm(mw.group(1), mw.group(2))
        if mh:
            d["height"] = _cm(mh.group(1), mh.group(2))
    for k, pat in (("Bảng LED Module", r"\bled\b"), ("Nhôm Tổ Ong (Aluminum Honeycomb)", r"tổ ong"),
                   ("Inox mạ vàng 3D + Neon", r"inox|neon"), ("Alu + Mica nổi đèn LED", r"\bmica\b|\balu\b"),
                   ("Bạt Hiflex / Flex Banner", r"hiflex|\bbạt\b|\bflex\b"), ("Gỗ Vintage / Khắc Laser", r"\bgỗ\b"),
                   ("Decal Sắc Nét / Màng Mờ", r"\bdecal\b")):
        if re.search(pat, t):
            d["material"] = k
            break
    for k, pat in (("Sang trọng & VIP", r"sang trọng|\bvip\b|luxury"), ("Cổ điển / Vintage", r"vintage|cổ điển"),
                   ("Tối giản & Tinh tế", r"tối giản|minimal"), ("Nổi bật & Rực rỡ", r"rực|nổi bật"),
                   ("Hiện đại & Trẻ trung", r"hiện đại|trẻ")):
        if re.search(pat, t):
            d["style"] = k
            break
    cut = r"\s+(?:ngang|cao|rộng|dài|nền|sđt|sdt|số|màu|kích|làm|size)\b"
    b = re.search(r"(?:quán|cửa hàng|shop|tiệm|nhà hàng|spa|salon|công ty)\s+[^,.\n;]+", txt, re.I)
    if b:
        d["brand"] = re.split(cut, b.group(0), flags=re.I)[0].strip().upper()
    c = re.search(r"(?:nền|màu|tông)\s+([^,.\n;]+)", t)
    if c:
        d["colors"] = re.split(cut, c.group(1))[0].strip()
    return d


def offline_optimize(p):
    return (p + " Ultra-detailed professional advertising design, typography rendered exactly as written, "
            "balanced composition with clear visual hierarchy, soft cinematic lighting, sharp focus, 8k, print-ready.")


def offline_slogans(brand, sub):
    first = next((l.strip() for l in sub.splitlines() if l.strip()), "chất lượng")
    b = brand.title()
    return "\n".join([f"{b} - {first}, chất lượng thấy liền", f"Ghé {b}, hài lòng ngay lần đầu",
                      f"{b}: chuẩn chất, chuẩn giá", f"Đến {b} - trải nghiệm khác biệt", f"{b} - uy tín tạo niềm tin"])


FAQ = [
    (("hiflex", "bạt", "banner", "băng rôn"), "Bạt Hiflex in ngoài trời bền ~1-2 năm, rẻ, hợp băng rôn/biển tạm. Bạt không gân căng khung sắt cho hình ảnh mịn hơn. File in khổ lớn để 100-150 DPI ở kích thước thật, chừa lề gấp viền ~5 cm."),
    (("alu", "mica"), "Alu + mica nổi (chữ nổi) là loại biển hiệu phổ biến: nền alu composite, chữ mica cắt CNC, có thể gắn LED hắt sáng. Bền 5+ năm nếu thi công đúng; giá tính theo m² và độ phức tạp chữ."),
    (("inox",), "Inox mạ vàng gương 3D sang trọng, hợp nhà hàng/khách sạn/spa; đắt hơn alu mica và cần thi công chữ nổi, hắt đèn LED."),
    (("led", "module"), "LED module P10 ngoài trời, P5/P3.08/P2.5 trong nhà. Dùng tab '⚡ Tính LED & Vật tư' để ra số module, nguồn, card điều khiển và dự toán."),
    (("standee", "cuốn"), "Standee cuốn 60x160 hoặc 80x200 cm. Đáy ~15-20% bị đế che: đừng đặt SĐT/địa chỉ ở đó. In bạt PP/decal PP, độ phân giải 150 DPI là đủ."),
    (("dpi", "độ phân giải", "file in", "cmyk", "bleed", "lề"), "File in nên để chế độ màu CMYK, chữ chuyển curve/outline, chừa lề cắt (bleed) 3 mm với ấn phẩm nhỏ, ~5 cm gấp viền với bạt lớn. Khổ lớn 100-150 DPI; ấn phẩm nhỏ (menu, tem) 300 DPI."),
    (("decal", "tem", "nhãn"), "Decal giấy/PVC dán sản phẩm; cán màng mờ cho cảm giác cao cấp, cán bóng cho màu rực. Nhớ để đường bế (cutline) riêng một layer."),
    (("giá", "báo giá", "bao nhiêu"), "Giá in thường tính theo m² nhân độ phức tạp. Vào tab '🧾 Báo giá in ấn' để nhập bảng giá của xưởng và xuất Excel gửi khách."),
]


def offline_chat(q):
    ql = q.lower()
    hits = [a for keys, a in FAQ if any(k in ql for k in keys)]
    if hits:
        return "\n\n".join(hits[:2])
    return ("Trợ lý đang ở chế độ có sẵn (không dùng AI) nên chỉ trả lời được các chủ đề: bạt hiflex, alu mica, inox, LED module, "
            "standee, decal/tem, chuẩn file in và báo giá. Bạn thử hỏi lại theo các từ khoá này nhé.")


def apply_brief(data):
    """Điền form từ dict; trả về số trường đã điền."""
    n = 0
    if data.get("p_type") in PRODUCTS:
        st.session_state.p_type = data["p_type"]
        st.session_state.width, st.session_state.height = PRODUCTS[data["p_type"]]
        n += 1
    for k in ("brand", "title", "sub", "contact", "colors"):
        if data.get(k):
            st.session_state[k] = str(data[k])
            n += 1
    for k in ("width", "height"):
        try:
            st.session_state[k] = float(min(max(float(data[k]), 5), 2000))
            n += 1
        except (KeyError, TypeError, ValueError):
            pass
    if data.get("material") in MATERIALS:
        st.session_state.material = data["material"]
        n += 1
    if data.get("style") in STYLES:
        st.session_state.style = data["style"]
        n += 1
    return n


def parse_brief():
    """Callback: đọc yêu cầu thô/ảnh của khách và điền sẵn form (AI nếu có, không thì bộ đọc nhanh)."""
    txt = st.session_state.get("brief_txt", "").strip()
    up = st.session_state.get("brief_img")
    if not txt and up is None:
        st.session_state.brief_msg = ("warning", "Hãy dán nội dung của khách hoặc tải ảnh ghi chú.")
        return
    why = ""
    ok, code = ai_gate(1)
    if ok:
        system = ("Bạn là nhân viên tư vấn xưởng in quảng cáo Việt Nam. Trích thông tin từ yêu cầu của khách và trả về DUY NHẤT một JSON "
                  'với các khoá: "p_type" (một trong ' + json.dumps(list(PRODUCTS), ensure_ascii=False) + '), "brand", "title", "sub" (danh mục dịch vụ, mỗi mục một dòng), '
                  '"contact", "width" (cm, số), "height" (cm, số), "material" (một trong ' + json.dumps(list(MATERIALS), ensure_ascii=False) + '), '
                  '"style" (một trong ' + json.dumps(STYLES, ensure_ascii=False) + '), "colors". Thiếu thông tin thì bỏ khoá đó, không bịa số điện thoại.')
        try:
            img = Image.open(up) if up is not None else None
            raw = ai_text(txt or "Đọc ảnh ghi chú của khách.", system=system, image=img, as_json=True)
            data = json.loads(re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.M).strip())
            if isinstance(data, list):
                data = data[0]
            apply_brief(data)
            st.session_state.brief_msg = ("success", "Đã điền form bằng AI. Kiểm tra lại các ô bên dưới nhé.")
            return
        except Exception as e:
            why = friendly_err(e)
    else:
        why = GATE_MSG[code]
    if not txt:  # chỉ có ảnh -> bắt buộc phải có AI
        st.session_state.brief_msg = ("warning", f"Đọc ảnh cần AI. {why} Hãy gõ/dán nội dung chữ thay vì ảnh.")
        return
    n = apply_brief(offline_parse(txt))
    if n:
        st.session_state.brief_msg = ("info", f"Đã điền {n} mục bằng bộ đọc nhanh (không dùng AI). Kiểm tra lại các ô bên dưới nhé.")
    else:
        st.session_state.brief_msg = ("warning", f"{why} Bộ đọc nhanh chưa nhận ra thông tin nào - hãy ghi rõ loại biển, kích thước (vd 3x1m), SĐT.")


def on_product_change():
    st.session_state.width, st.session_state.height = PRODUCTS[st.session_state.p_type]


# ==============================================================================
# 5. GIAO DIỆN
# ==============================================================================
DEFAULTS = dict(p_type="Biển hiệu (Signboard)", brand="NHÀ HÀNG HẢI SẢN BIỂN ĐÔNG",
                title="TƯƠI SỐNG MỖI NGÀY - GIẢM 20% TỔNG HÓA ĐƠN",
                sub="Cua Cà Mau\nTôm Hùm Nha Trang\nLẩu Hải Sản\nĐặt bàn trước giảm thêm 5%",
                contact="0988.123.456 - 123 Nguyễn Văn Cừ, Q.1", width=320.0, height=96.0,
                style=STYLES[0], material="Alu + Mica nổi đèn LED", colors="Xanh dương biển - Vàng kim - Trắng",
                led_mod="P10 Outdoor", led_mode=ROUND_MODES[0], text_model=_secret("GEMINI_TEXT_MODEL", "gemini-3.1-flash-lite"),
                image_model=_secret("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview"),
                shop_name="XƯỞNG IN QUẢNG CÁO", shop_phone="", chat=[])
# Streamlit xoá state của widget không được vẽ ở lần chạy hiện tại (vd khi chuyển tab) -> lưu/khôi phục thủ công
FORM_KEYS = ["p_type", "brand", "title", "sub", "contact", "width", "height", "style", "material", "colors", "led_mod", "led_mode"]
_saved = st.session_state.setdefault("_saved", {})
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, _saved.get(k, v) if k in FORM_KEYS else v)

st.markdown("""<style>
.main-header{font-size:2.1rem;font-weight:800;color:#1E293B;text-align:center;margin-bottom:.2rem}
.sub-header{font-size:1.05rem;color:#0284C7;text-align:center;margin-bottom:1.2rem;font-weight:600}
.led-card{background:#F0F9FF;border:1.5px solid #0284C7;padding:1rem;border-radius:.6rem;color:#0369A1;margin-bottom:1rem}
.warn{background:#FEF2F2;border-left:4px solid #EF4444;padding:.8rem;border-radius:.5rem;color:#991B1B;margin-bottom:.8rem}
.ok{background:#F0FDF4;border-left:4px solid #22C55E;padding:.8rem;border-radius:.5rem;color:#166534;margin-bottom:.8rem}
</style>""", unsafe_allow_html=True)
st.markdown("<div class='main-header'>🖨️ TRỢ LÝ AI QUẢNG CÁO & IN ẤN (v4)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>AI đọc yêu cầu khách • Bố cục in • Prompt & ảnh phối cảnh • Tính LED • Báo giá Excel • Chat tư vấn</div>", unsafe_allow_html=True)

with st.sidebar:
    st.title("DANH MỤC")
    mode = st.radio("Chức năng:", ["🛠️ Thiết kế & Prompt AI", "⚡ Tính LED & Vật tư", "🧾 Báo giá in ấn", "💬 Chat tư vấn AI", "🚀 Thư viện Prompt", "📚 Hướng dẫn"])
    st.markdown("---")
    st.subheader("⚙️ Cài đặt")
    st.text_input("Tên xưởng (hiện trên báo giá)", key="shop_name")
    st.text_input("Hotline xưởng", key="shop_phone")
    if using_own_key():
        st.caption("✅ Đang dùng khoá riêng của bạn")
    elif api_key():
        st.caption(f"✅ AI sẵn sàng - không cần nhập khoá ({_limit('AI_SESSION_LIMIT', 30) - st.session_state.get('ai_used', 0)} lượt còn lại)")
    else:
        st.caption("⚪ Chế độ không cần khoá: AI đang tắt, các công cụ vẫn chạy bình thường")
    with st.expander("🔧 Nâng cao (dành cho chủ xưởng)"):
        st.text_input("Gemini API Key riêng (tuỳ chọn)", type="password", key="api_key_in",
                      help="Khách KHÔNG cần nhập. Chỉ dùng nếu bạn muốn test bằng khoá khác (không bị giới hạn lượt).")
        st.text_input("Model văn bản / đọc ảnh", key="text_model")
        st.text_input("Model tạo ảnh", key="image_model")

# ------------------------------------------------------------------ TAB 1
if mode.startswith("🛠️"):
    with st.expander("🤖 AI đọc yêu cầu của khách → tự điền form (dán tin nhắn Zalo hoặc tải ảnh chữ viết tay)", expanded=False):
        st.text_area("Nội dung khách gửi", key="brief_txt", height=90,
                     placeholder="VD: Làm cho chị cái biển quán cà phê Lưu Gia, ngang 3m cao 1m, nền nâu gỗ, SĐT 0909...")
        st.file_uploader("Hoặc ảnh ghi chú / ảnh chụp tay", type=["png", "jpg", "jpeg", "webp"], key="brief_img")
        st.button("✨ Phân tích & điền form", on_click=parse_brief)
        if "brief_msg" in st.session_state:
            getattr(st, st.session_state.brief_msg[0])(st.session_state.brief_msg[1])

    left, right = st.columns([1, 1.25])
    with left:
        st.markdown("### 1. Thông tin đầu vào")
        st.selectbox("Loại ấn phẩm", list(PRODUCTS), key="p_type", on_change=on_product_change)
        st.text_input("Tên cửa hàng / thương hiệu", key="brand")
        st.text_input("Tiêu đề chính / thông điệp", key="title")
        st.text_area("Dịch vụ / danh mục (mỗi dòng 1 mục)", key="sub", height=100)
        st.text_input("Hotline / địa chỉ", key="contact")
        c1, c2 = st.columns(2)
        c1.number_input("Rộng (cm)", min_value=5.0, max_value=2000.0, key="width")
        c2.number_input("Cao (cm)", min_value=5.0, max_value=2000.0, key="height")
        c1, c2 = st.columns(2)
        c1.selectbox("Phong cách", STYLES, key="style")
        c2.selectbox("Chất liệu", list(MATERIALS), key="material")
        if st.session_state.material.startswith("Bảng LED"):
            c1, c2 = st.columns(2)
            c1.selectbox("Loại module LED", list(LED_SPECS), key="led_mod")
            c2.selectbox("Cách chia tấm", ROUND_MODES, key="led_mode")
        st.text_input("Màu chủ đạo", key="colors")

    S = st.session_state
    png = make_wireframe(S.p_type, S.width, S.height, S.brand, S.title, S.contact, S.sub, S.material, S.led_mod, S.led_mode)
    pr = build_prompt(S.p_type, S.width, S.height, S.brand, S.title, S.colors, S.style, S.material, S.contact, S.sub, S.led_mod)

    with right:
        st.markdown("### 2. Kết quả")
        st.image(png, caption="Sơ đồ bố cục chuẩn in & thi công", width="stretch")
        st.download_button("📥 Tải sơ đồ (PNG)", png, file_name="so_do_bo_cuc.png", mime="image/png")
        if S.material.startswith("Bảng LED"):
            r = calc_led(S.width, S.height, S.led_mod, S.led_mode)
            st.markdown(f"<div class='led-card'>⚡ <b>Dự toán LED {r['mod']}:</b> {r['n']} module ({r['cols']}x{r['rows']}) • "
                        f"Kích thước thực {r['aw']}x{r['ah']} cm • {r['pxw']}x{r['pxh']} px • Tối đa {r['pmax']} W • "
                        f"{r['psu']} nguồn 5V40A • {r['card']}</div>", unsafe_allow_html=True)
        elif S.p_type.startswith("Standee"):
            st.markdown("<div class='warn'>⚠️ Vùng chân standee bị đế che khuất - không đặt SĐT/địa chỉ ở đáy.</div>", unsafe_allow_html=True)
        elif S.p_type.startswith("Biển hiệu"):
            st.markdown("<div class='ok'>✅ Gợi ý tỷ lệ: Logo 20-25% • Tiêu đề ~50% • Liên hệ 25-30%. Nhớ chừa lề gấp viền.</div>", unsafe_allow_html=True)

        st.markdown("#### 🤖 Prompt cho AI tạo ảnh")
        engine = st.radio("Công cụ", ["Midjourney", "Gemini / Nano Banana / Flux / DALL·E"], horizontal=True)
        final = engine_text(pr, engine)
        st.code(final, language="markdown", wrap_lines=True)
        st.caption(f"Tỷ lệ khung hình: {pr['ar']} • Negative: {pr['negative']}")

        b1, b2, b3 = st.columns(3)
        if b1.button("✨ Tối ưu prompt", width="stretch"):
            S.notice = None
            ok, why = ai_gate(1)
            if ok:
                with st.spinner("Đang tối ưu..."):
                    try:
                        S.opt = ai_text("Viết lại prompt tạo ảnh quảng cáo sau cho chi tiết, chuyên nghiệp hơn bằng tiếng Anh. "
                                        "GIỮ NGUYÊN các chữ trong dấu nháy đơn (tên, tiêu đề, số điện thoại). Chỉ trả về prompt.\n\n" + pr["prompt"])
                    except Exception as e:
                        S.opt = offline_optimize(pr["prompt"])
                        S.notice = ("warning", friendly_err(e) + " Đã dùng bộ tối ưu nhanh thay thế.")
            else:
                S.opt = offline_optimize(pr["prompt"])
                S.notice = ("info", GATE_MSG[why] + " Đã dùng bộ tối ưu nhanh (không AI).")
        if b2.button("🎨 Tạo ảnh phối cảnh", width="stretch"):
            S.notice = None
            ok, why = ai_gate(5)
            if not ok:
                S.notice = ("info", GATE_MSG[why] + " Tạo ảnh cần AI - bạn vẫn có thể copy prompt ở trên dán vào Gemini / ChatGPT / Midjourney.")
            else:
                with st.spinner("Gemini đang vẽ (10-40 giây)..."):
                    try:
                        S.gen_img = ai_image(pr["prompt"] + f" Follow the layout of the attached wireframe. Aspect ratio {pr['ar']}.", ref=Image.open(io.BytesIO(png)))
                        S.gen_err = ""
                    except Exception as e:
                        S.gen_img, S.gen_err = None, friendly_err(e)
        if b3.button("💡 5 slogan", width="stretch"):
            S.notice = None
            ok, why = ai_gate(1)
            S.slogans = offline_slogans(S.brand, S.sub)
            if ok:
                with st.spinner("Đang nghĩ slogan..."):
                    try:
                        S.slogans = ai_text(f"Viết 5 slogan tiếng Việt ngắn gọn, bắt tai cho '{S.brand}' ({S.sub.replace(chr(10), ', ')}), "
                                            f"phong cách {S.style}, phù hợp in trên {S.p_type}. Mỗi slogan một dòng, không giải thích.")
                    except Exception as e:
                        S.notice = ("warning", friendly_err(e) + " Đã dùng gợi ý có sẵn.")
            else:
                S.notice = ("info", GATE_MSG[why] + " Đã dùng gợi ý có sẵn (không AI).")
        if S.get("notice"):
            getattr(st, S.notice[0])(S.notice[1])
        if S.get("opt"):
            st.markdown("**Prompt đã tối ưu:**")
            st.code(S.opt, language="markdown", wrap_lines=True)
        if S.get("slogans"):
            st.markdown("**Gợi ý slogan:**")
            st.write(S.slogans)
        if S.get("gen_err"):
            st.error(S.gen_err + " (Model tạo ảnh của Gemini thường cần khoá thuộc tài khoản trả phí; có thể đổi tên model ở Cài đặt > Nâng cao.)")
        if S.get("gen_img") is not None:
            st.image(S.gen_img, caption="Ảnh phối cảnh do Gemini tạo (tham khảo, hãy kiểm tra lại chữ)", width="stretch")
            buf = io.BytesIO()
            S.gen_img.save(buf, format="PNG")
            st.download_button("📥 Tải ảnh phối cảnh", buf.getvalue(), file_name="phoi_canh.png", mime="image/png")

# ------------------------------------------------------------------ TAB 2
elif mode.startswith("⚡"):
    st.subheader("⚡ Tính số lượng module LED & vật tư")
    c1, c2 = st.columns([1, 1.3])
    with c1:
        mod = st.selectbox("Loại module", list(LED_SPECS), key="led_mod2")
        rm = st.radio("Cách chia tấm", ROUND_MODES, key="led_mode2")
        w = st.number_input("Rộng mong muốn (cm)", 10.0, 3000.0, 320.0, 10.0)
        h = st.number_input("Cao mong muốn (cm)", 10.0, 3000.0, 96.0, 10.0)
        hours = st.number_input("Giờ bật mỗi ngày", 1, 24, 12)
        p_mod = st.number_input("Đơn giá 1 module (VNĐ)", value=65000, step=5000)
        p_psu = st.number_input("Đơn giá 1 nguồn 5V40A (VNĐ)", value=115000, step=5000)
        p_card = st.number_input("Đơn giá card điều khiển (VNĐ)", value=250000, step=10000)
        p_kd = st.number_input("Đơn giá khung/cabinet (VNĐ/m²)", value=0, step=50000, help="Để 0 nếu chưa tính khung")
    r = calc_led(w, h, mod, rm)
    with c2:
        st.success(f"🎯 Cần **{r['n']} module** ({r['cols']} cột x {r['rows']} hàng) • Kích thước thực **{r['aw']} x {r['ah']} cm** ({r['area']:.2f} m²)")
        if abs(r["aw"] - w) > 16 or abs(r["ah"] - h) > 8:
            st.warning("Kích thước thực lệch so với mong muốn - cân nhắc đổi cách chia tấm.")
        kwh = r["pavg"] * hours * 30 / 1000
        st.markdown(f"""
* **Độ phân giải:** `{r['pxw']} x {r['pxh']} px` ({r['pix']:,} điểm LED)
* **Công suất:** tối đa `{r['pmax']} W` • trung bình ~`{r['pavg']} W` • ước tính `{kwh:.0f} kWh/tháng`
* **Nguồn 5V 40A:** `{r['psu']} cái` (tính ở 80% tải)
* **Card điều khiển:** {r['card']}""")
        rows_ = [("Module " + r["mod"], r["n"], p_mod), ("Nguồn 5V 40A", r["psu"], p_psu), ("Card điều khiển", 1, p_card)]
        if p_kd:
            rows_.append(("Khung / cabinet (m²)", round(r["area"], 2), p_kd))
        df = pd.DataFrame([{"Hạng mục": a, "Số lượng": b, "Đơn giá": c, "Thành tiền": b * c} for a, b, c in rows_])
        total = df["Thành tiền"].sum()
        show = df.copy()
        for col in ("Đơn giá", "Thành tiền"):
            show[col] = show[col].map(fmt)
        st.table(show)
        st.markdown(f"### Tổng vật tư chính: {fmt(total)} VNĐ")
        st.caption("Chưa gồm dây điện, ốc vít, công lắp đặt và vận chuyển.")
        out = pd.concat([df, pd.DataFrame([{"Hạng mục": "TỔNG", "Số lượng": "", "Đơn giá": "", "Thành tiền": total}])])
        st.download_button("📥 Tải bảng vật tư (Excel)", to_excel({"Vat tu LED": out}), file_name="vat_tu_led.xlsx")

# ------------------------------------------------------------------ TAB 3
elif mode.startswith("🧾"):
    st.subheader("🧾 Báo giá in ấn theo m² (xuất Excel)")
    st.caption("Bảng giá mẫu - sửa trực tiếp theo giá của xưởng. Thêm dòng bằng nút + ở cuối bảng.")
    if "quote" not in st.session_state:
        st.session_state.quote = pd.DataFrame([
            {"Hạng mục": "Bạt Hiflex in", "Rộng (cm)": 500.0, "Cao (cm)": 100.0, "SL": 1, "Đơn giá/m²": 70000},
            {"Hạng mục": "Biển Alu + Mica nổi", "Rộng (cm)": 320.0, "Cao (cm)": 96.0, "SL": 1, "Đơn giá/m²": 1800000},
            {"Hạng mục": "Decal dán kính", "Rộng (cm)": 100.0, "Cao (cm)": 50.0, "SL": 2, "Đơn giá/m²": 180000},
        ])
    if st.session_state.get("_prev_mode") != mode and "quote_last" in st.session_state:
        st.session_state.quote = st.session_state.quote_last  # quay lại tab: nạp bản đã sửa
    ed = st.data_editor(st.session_state.quote, num_rows="dynamic", width="stretch", key="q_ed")
    st.session_state.quote_last = ed
    c1, c2, c3, c4 = st.columns(4)
    install = c1.number_input("Thi công/lắp đặt (% )", 0.0, 100.0, 10.0)
    ship = c2.number_input("Vận chuyển (VNĐ)", 0, value=0, step=50000)
    disc = c3.number_input("Giảm giá (%)", 0.0, 100.0, 0.0)
    vat = c4.number_input("VAT (%)", 0.0, 20.0, 0.0)
    q = ed.copy().dropna(subset=["Hạng mục"])
    for col in ("Rộng (cm)", "Cao (cm)", "SL", "Đơn giá/m²"):
        q[col] = pd.to_numeric(q[col], errors="coerce").fillna(0)
    q["Diện tích (m²)"] = (q["Rộng (cm)"] * q["Cao (cm)"] / 10000 * q["SL"]).round(2)
    q["Thành tiền"] = (q["Diện tích (m²)"] * q["Đơn giá/m²"]).round(0)
    sub_t = q["Thành tiền"].sum()
    inst = sub_t * install / 100
    after = (sub_t + inst) * (1 - disc / 100) + ship
    vat_v = after * vat / 100
    grand = after + vat_v
    view = q.copy()
    for col in ("Đơn giá/m²", "Thành tiền"):
        view[col] = view[col].map(fmt)
    st.dataframe(view, width="stretch", hide_index=True)
    st.markdown(f"**Cộng hạng mục:** {fmt(sub_t)} • **Thi công:** {fmt(inst)} • **Vận chuyển:** {fmt(ship)} • **VAT:** {fmt(vat_v)}")
    st.markdown(f"### 💰 TỔNG BÁO GIÁ: {fmt(grand)} VNĐ")
    summ = pd.DataFrame([
        {"Hạng mục": "Cộng hạng mục", "Thành tiền": sub_t}, {"Hạng mục": f"Thi công ({install:g}%)", "Thành tiền": inst},
        {"Hạng mục": f"Giảm giá ({disc:g}%)", "Thành tiền": -(sub_t + inst) * disc / 100}, {"Hạng mục": "Vận chuyển", "Thành tiền": ship},
        {"Hạng mục": f"VAT ({vat:g}%)", "Thành tiền": vat_v}, {"Hạng mục": "TỔNG CỘNG", "Thành tiền": grand}])
    head = pd.DataFrame([{"Hạng mục": f"BÁO GIÁ - {st.session_state.shop_name} {st.session_state.shop_phone}".strip()}])
    st.download_button("📥 Tải báo giá (Excel)", to_excel({"Bao gia": pd.concat([head, q, summ], ignore_index=True)}), file_name="bao_gia.xlsx")

# ------------------------------------------------------------------ TAB 4
elif mode.startswith("💬"):
    st.subheader("💬 Chat tư vấn AI cho xưởng in & quảng cáo")
    if not api_key():
        st.info("Đang ở chế độ trợ lý có sẵn (không AI): trả lời nhanh các chủ đề bạt, alu mica, inox, LED, standee, decal, file in, báo giá.")
    sys_prompt = ("Bạn là chuyên gia tư vấn ngành in ấn & quảng cáo tại Việt Nam (biển hiệu, alu mica, inox, hiflex, decal, LED module, standee, menu). "
                  "Trả lời bằng tiếng Việt, ngắn gọn, thực tế, nêu rõ giả định khi báo giá/ước tính. Không chắc thì nói không chắc.")
    for m in st.session_state.chat:
        st.chat_message(m["role"]).write(m["content"])
    if q := st.chat_input("Hỏi về chất liệu, kỹ thuật thi công, cách báo giá, viết nội dung quảng cáo..."):
        st.session_state.chat.append({"role": "user", "content": q})
        st.chat_message("user").write(q)
        hist = "\n".join(f"{'Khách' if m['role'] == 'user' else 'Trợ lý'}: {m['content']}" for m in st.session_state.chat[-12:])
        with st.chat_message("assistant"):
            with st.spinner("Đang trả lời..."):
                ok, why = ai_gate(1)
                if ok:
                    try:
                        ans = ai_text(hist + "\nTrợ lý:", system=sys_prompt)
                    except Exception as e:
                        ans = offline_chat(q) + f"\n\n_(AI tạm lỗi: {friendly_err(e)})_"
                else:
                    ans = offline_chat(q) + ("" if why == "no_key" else f"\n\n_({GATE_MSG[why]})_")
            st.write(ans)
        st.session_state.chat.append({"role": "assistant", "content": ans})
    if st.session_state.chat and st.button("🗑️ Xoá hội thoại"):
        st.session_state.chat = []
        st.rerun()

# ------------------------------------------------------------------ TAB 5
elif mode.startswith("🚀"):
    st.subheader("🚀 Thư viện Prompt phụ trợ")
    x = st.text_input("Mô tả sản phẩm / thương hiệu", "quán cà phê phong cách Indochine, tông nâu gỗ ấm")
    for i, (t, p) in enumerate(TOOLKIT, 1):
        with st.expander(f"📌 {i}. {t}"):
            st.code(f"/imagine prompt: {p.format(x=x or 'advertising display')}", language="markdown", wrap_lines=True)

# ------------------------------------------------------------------ TAB 6
else:
    st.subheader("📚 Quy trình & cài đặt")
    st.markdown("""
**Quy trình 5 bước:** nhận yêu cầu khách → *AI đọc yêu cầu* tự điền form → xem sơ đồ bố cục & tải PNG → tính LED / lập báo giá Excel → copy prompt (hoặc bấm *Tạo ảnh phối cảnh*) gửi khách duyệt.

**Để khách dùng ngay trên Chrome, không đăng nhập, không nhập khoá (làm 1 lần):**
1. Streamlit Cloud → app → **Settings → Secrets**, thêm:
```toml
GEMINI_API_KEY = "khoá_của_bạn"
AI_SESSION_LIMIT = 30   # số lượt AI tối đa / mỗi khách / phiên
AI_DAILY_LIMIT = 300    # tổng lượt AI / ngày cho cả app (tạo ảnh tính 5 lượt)
# tuỳ chọn khi Google đổi tên model:
# GEMINI_TEXT_MODEL = "gemini-3.1-flash-lite"
# GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image-preview"
```
2. **Share → Who can view this app → "This app is public"** (nếu để Private, khách sẽ bị bắt đăng nhập Google/GitHub).

Hết lượt hoặc chưa có khoá, app tự chuyển sang chế độ offline (đọc yêu cầu bằng quy tắc, slogan/tối ưu prompt có sẵn, chat FAQ); riêng *Tạo ảnh phối cảnh* và *đọc ảnh ghi chú* cần AI.
""")

# ------------------------------------------------------------------ LƯU STATE
for _k in FORM_KEYS:
    if _k in st.session_state:
        st.session_state._saved[_k] = st.session_state[_k]
st.session_state._prev_mode = mode
