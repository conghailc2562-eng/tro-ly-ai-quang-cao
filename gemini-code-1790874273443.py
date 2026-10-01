"""
================================================================================
ỨNG DỤNG TRỢ LÝ AI CHUYÊN NGÀNH QUẢNG CÁO & IN ẤN (ADVERTISING & PRINT AI ASSISTANT) - VERSION 3 (Đã sửa lỗi Streamlit)
Tích hợp thêm: 
1. Nhôm Tổ Ong (Aluminum Honeycomb) & Bảng LED Module P10.
2. Bộ Động cơ Tự động Tính toán Số lượng Module LED P10, Kích thước thực tế,
   Công suất điện, Số nguồn 5V40A và Mạch điều khiển.
Yêu cầu thư viện: streamlit, matplotlib, Pillow, pandas
Cách chạy ứng dụng: streamlit run ad_print_ai_assistant-v3.py
================================================================================
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import math
import pandas as pd
from PIL import Image

# ==============================================================================
# 1. ĐỘNG CƠ TÍNH TOÁN KỸ THUẬT MODULE LED P10 & BẢNG ĐIỆN TỬ
# ==============================================================================
def calculate_led_p10(width_cm, height_cm, module_type="P10 Outdoor (32x16cm)"):
    specs = {
        "P10 Outdoor (32x16cm)": {"w": 32, "h": 16, "px_w": 32, "px_h": 16, "pwr_max": 30, "pwr_avg": 18, "desc": "P10 Ngoài trời 1 màu / 3 màu / Full Color"},
        "P5 Outdoor (32x16cm)": {"w": 32, "h": 16, "px_w": 64, "px_h": 32, "pwr_max": 32, "pwr_avg": 20, "desc": "P5 Ngoài trời Full Color độ nét cao"},
        "P3.08 Indoor (32x16cm)": {"w": 32, "h": 16, "px_w": 104, "px_h": 52, "pwr_max": 25, "pwr_avg": 15, "desc": "P3 Trong nhà Full Color độ phân giải siêu nét"},
        "P2.5 Indoor (32x16cm)": {"w": 32, "h": 16, "px_w": 128, "px_h": 64, "pwr_max": 25, "pwr_avg": 15, "desc": "P2.5 Trong nhà sắc nét cao cấp"}
    }
    spec = specs.get(module_type, specs["P10 Outdoor (32x16cm)"])
    
    mod_w = spec["w"]
    mod_h = spec["h"]
    
    cols = max(1, int(round(width_cm / mod_w)))
    rows = max(1, int(round(height_cm / mod_h)))
    
    actual_width = cols * mod_w
    actual_height = rows * mod_h
    total_modules = cols * rows
    
    total_px_w = cols * spec["px_w"]
    total_px_h = rows * spec["px_h"]
    total_pixels = total_px_w * total_px_h
    
    max_power_w = total_modules * spec["pwr_max"]
    avg_power_w = total_modules * spec["pwr_avg"]
    
    # Số nguồn 5V 40A (200W) - Khuyên dùng 80% công suất continuous (~160W/nguồn)
    psu_count_5v40a = max(1, math.ceil(max_power_w / 160.0))
    
    # Gợi ý card điều khiển
    if total_pixels <= 65536:
        card_type = "Mạch HD-WF2 / HD-WF4 (Wifi truyền ứng dụng điện thoại/PC)"
    elif total_pixels <= 262144:
        card_type = "Card HD-C16C / Novastar / Linsn (Kết nối USB/LAN/Wifi)"
    else:
        card_type = "Bộ xử lý hình ảnh LED Video Processor HD-VP210 + Card nhận"
        
    return {
        "module_name": module_type,
        "cols": cols,
        "rows": rows,
        "actual_width": actual_width,
        "actual_height": actual_height,
        "total_modules": total_modules,
        "total_px_w": total_px_w,
        "total_px_h": total_px_h,
        "total_pixels": total_pixels,
        "max_power_w": max_power_w,
        "avg_power_w": avg_power_w,
        "psu_count_5v40a": psu_count_5v40a,
        "card_type": card_type,
        "desc": spec["desc"]
    }


# ==============================================================================
# 2. ĐỘNG CƠ TẠO SƠ ĐỒ BỐ CỤC (LAYOUT WIREFRAME ENGINE)
# ==============================================================================
def generate_layout_wireframe(product_type, width, height, brand_name, title, contact_info, sub_text="", material="Bạt Hiflex / Alu"):
    fig, ax = plt.subplots(figsize=(8, 8 * (height / width) if height/width < 2.5 else 10), dpi=150)
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#FFFFFF')
    
    ax.set_xlim(-0.1 * width, 1.1 * width)
    ax.set_ylim(-0.1 * height, 1.1 * height)
    ax.set_aspect('equal')
    
    # Border
    outer_box = patches.Rectangle((0, 0), width, height, linewidth=2.5, edgecolor='#1E293B', facecolor='#F1F5F9', zorder=1)
    ax.add_patch(outer_box)
    
    # Safe Margin
    margin_x = width * 0.05
    margin_y = height * 0.05
    safe_box = patches.Rectangle((margin_x, margin_y), width - 2*margin_x, height - 2*margin_y, 
                                 linewidth=1, edgecolor='#94A3B8', facecolor='none', linestyle='--', zorder=2)
    ax.add_patch(safe_box)
    
    if "Bảng LED Module P10" in material:
        led_res = calculate_led_p10(width, height)
        cols, rows = led_res["cols"], led_res["rows"]
        mw, mh = width / cols, height / rows
        
        for i in range(cols):
            for j in range(rows):
                grid_box = patches.Rectangle((i*mw, j*mh), mw, mh, linewidth=0.5, edgecolor='#3B82F6', facecolor='#E0F2FE', alpha=0.5, zorder=3)
                ax.add_patch(grid_box)
        
        ax.text(width/2, height*0.6, f"BẢNG LED MATRIX P10: {cols} CỘT x {rows} HÀNG\n(Tổng số: {led_res['total_modules']} TẤM MODULE 32x16cm)", 
                color='#1E40AF', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(width/2, height*0.35, f"NỘI DUNG HIỂN THỊ: \"{title}\"\n{brand_name} - {contact_info}", 
                color='#0369A1', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)

    elif "Standee" in product_type:
        bottom_clearance = max(height * 0.15, 30)
        clear_box = patches.Rectangle((0, 0), width, bottom_clearance, 
                                      linewidth=1.5, edgecolor='#EF4444', facecolor='#FEE2E2', alpha=0.6, zorder=3)
        ax.add_patch(clear_box)
        ax.text(width/2, bottom_clearance/2, "⚠️ VÙNG AN TOÀN CHÂN STANDEE\n(Tránh để thông tin quan trọng ở đây)", 
                color='#991B1B', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)
        
        ax.add_patch(patches.Rectangle((margin_x, height - height*0.2), width - 2*margin_x, height*0.15, 
                                       facecolor='#DBEAFE', edgecolor='#3B82F6', alpha=0.7, zorder=3))
        ax.text(width/2, height - height*0.125, f"LOGO & THƯƠNG HIỆU\n[{brand_name.upper()}]", 
                color='#1E40AF', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        
        ax.add_patch(patches.Rectangle((margin_x, bottom_clearance + height*0.12), width - 2*margin_x, height - bottom_clearance - height*0.35, 
                                       facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.6, zorder=3))
        ax.text(width/2, (height + bottom_clearance)/2, f"HÌNH CỐT LÕI & TIÊU ĐỀ CHÍNH\n\"{title}\"\n{sub_text}", 
                color='#92400E', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
        
        ax.add_patch(patches.Rectangle((margin_x, bottom_clearance + 2), width - 2*margin_x, height*0.09, 
                                       facecolor='#DCFCE7', edgecolor='#22C55E', alpha=0.7, zorder=3))
        ax.text(width/2, bottom_clearance + height*0.045, f"HOTLINE & ĐỊA CHỈ: {contact_info}", 
                color='#166534', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)

    elif "Biển hiệu" in product_type or "Băng rôn" in product_type:
        logo_w = width * 0.22
        ax.add_patch(patches.Rectangle((margin_x, margin_y), logo_w, height - 2*margin_y, 
                                       facecolor='#DBEAFE', edgecolor='#3B82F6', alpha=0.7, zorder=3))
        ax.text(margin_x + logo_w/2, height/2, f"LOGO\n{brand_name}", 
                color='#1E40AF', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
        
        title_w = width - logo_w - 3*margin_x
        ax.add_patch(patches.Rectangle((margin_x*2 + logo_w, height*0.35), title_w, height*0.55 - margin_y, 
                                       facecolor='#FEF3C7', edgecolor='#F59E0B', alpha=0.7, zorder=3))
        ax.text(margin_x*2 + logo_w + title_w/2, height*0.625, f"TÊN CỬA HÀNG / TIÊU ĐỀ CHÍNH\n\"{title.upper()}\"\n({sub_text})", 
                color='#92400E', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        
        ax.add_patch(patches.Rectangle((margin_x*2 + logo_w, margin_y), title_w, height*0.28, 
                                       facecolor='#DCFCE7', edgecolor='#22C55E', alpha=0.7, zorder=3))
        ax.text(margin_x*2 + logo_w + title_w/2, margin_y + height*0.14, f"THÔNG TIN LIÊN HỆ & DỊCH VỤ\n{contact_info}", 
                color='#166534', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)

    elif "Bảng vẫy" in product_type:
        center_x, center_y = width/2, height/2
        radius = min(width, height) * 0.42
        circle = patches.Circle((center_x, center_y), radius, linewidth=2, edgecolor='#0EA5E9', facecolor='#E0F2FE', zorder=3)
        ax.add_patch(circle)
        ax.text(center_x, center_y + radius*0.35, f"[{brand_name.upper()}]", color='#0369A1', fontsize=11, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(center_x, center_y, f"BIỂU TƯỢNG / DỊCH VỤ\n\"{title}\"", color='#0284C7', fontsize=9, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(center_x, center_y - radius*0.4, f"SĐT: {contact_info}", color='#075985', fontsize=8, fontweight='bold', ha='center', va='center', zorder=4)

    elif "Menu" in product_type:
        ax.add_patch(patches.Rectangle((margin_x, height - height*0.18), width - 2*margin_x, height*0.13, 
                                       facecolor='#E0E7FF', edgecolor='#6366F1', alpha=0.8, zorder=3))
        ax.text(width/2, height - height*0.115, f"THỰC ĐƠN / BẢNG GIÁ - {brand_name.upper()}\n\"{title}\"", 
                color='#3730A3', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        col_w = (width - 3*margin_x) / 2
        body_h = height - height*0.28 - margin_y
        ax.add_patch(patches.Rectangle((margin_x, margin_y + height*0.08), col_w, body_h, 
                                       facecolor='#F1F5F9', edgecolor='#94A3B8', alpha=0.6, zorder=3))
        ax.text(margin_x + col_w/2, height*0.5, "DANH MỤC A (Món chính / Dịch vụ 1)\n• Món 1 ..... 50k\n• Món 2 ..... 75k\n• Món 3 ..... 90k", 
                color='#334155', fontsize=8, ha='center', va='center', zorder=4)
        ax.add_patch(patches.Rectangle((margin_x*2 + col_w, margin_y + height*0.08), col_w, body_h, 
                                       facecolor='#F1F5F9', edgecolor='#94A3B8', alpha=0.6, zorder=3))
        ax.text(margin_x*2 + col_w + col_w/2, height*0.5, "DANH MỤC B (Đồ uống / Dịch vụ 2)\n• Món 4 ..... 35k\n• Món 5 ..... 45k\n• Món 6 ..... 60k", 
                color='#334155', fontsize=8, ha='center', va='center', zorder=4)
        ax.text(width/2, margin_y + height*0.03, f"Ghi chú / Hotline: {contact_info}", color='#64748B', fontsize=7, ha='center', va='center', zorder=4)

    else:
        center_x, center_y = width/2, height/2
        r_x, r_y = width*0.4, height*0.4
        ax.add_patch(patches.Rectangle((center_x - r_x, center_y - r_y), 2*r_x, 2*r_y, 
                                       linewidth=2, edgecolor='#EC4899', facecolor='#FCE7F3', linestyle='-', zorder=3))
        ax.text(center_x, center_y + r_y*0.5, f"{brand_name.upper()}", color='#BE185D', fontsize=10, fontweight='bold', ha='center', va='center', zorder=4)
        ax.text(center_x, center_y, f"{title}\n{sub_text}", color='#9D174D', fontsize=9, ha='center', va='center', zorder=4)
        ax.text(center_x, center_y - r_y*0.5, f"HSD / Hotline: {contact_info}", color='#831843', fontsize=7, ha='center', va='center', zorder=4)

    # Dimensions
    ax.annotate('', xy=(0, -margin_y*0.5), xytext=(width, -margin_y*0.5),
                arrowprops=dict(arrowstyle='<->', color='#0F172A', lw=1.2))
    ax.text(width/2, -margin_y*0.8, f"Chiều rộng: {width} cm", ha='center', va='top', fontsize=9, fontweight='bold', color='#0F172A')

    ax.annotate('', xy=(-margin_x*0.5, 0), xytext=(-margin_x*0.5, height),
                arrowprops=dict(arrowstyle='<->', color='#0F172A', lw=1.2))
    ax.text(-margin_x*0.8, height/2, f"Chiều cao:\n{height} cm", ha='right', va='center', fontsize=9, fontweight='bold', color='#0F172A', rotation=90)

    ax.set_title(f"SƠ ĐỒ BỐ CỤC CHUẨN IN & THI CÔNG: {product_type.upper()}\nKích thước: {width}x{height} cm | Chất liệu: {material}", 
                 fontsize=10, fontweight='bold', pad=12, color='#1E293B')

    ax.axis('off')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


# ==============================================================================
# 3. ĐỘNG CƠ TẠO PROMPT AI CHUYÊN SÂU (PROMPT ENGINE)
# ==============================================================================
def generate_ai_prompt(product_type, width, height, brand_name, title, main_colors, style, material, contact_info, sub_details=""):
    aspect_ratio = f"{int(width)}:{int(height)}"
    
    material_prompts = {
        "Bảng LED Module P10": "outdoor P10 LED matrix module display board, bright illuminated scrolling text and graphics, high-brightness DIP/SMD LED pixel grid, waterproof aluminum cabinet frame",
        "Nhôm Tổ Ong (Aluminum Honeycomb)": "ultra-flat premium architectural aluminum honeycomb facade panels, seamless metallic joint lines, high-rigidity modern metallic finish, 3D raised letters",
        "Alu + Mica nổi đèn LED": "premium aluminum composite panel background with 3D raised acrylic mica lettering, glowing internal LED edge-lit illumination",
        "Inox mạ vàng 3D + Neon": "luxurious 3D electroplated gold mirror stainless steel letters, backlit warm neon halo glow",
        "Bạt Hiflex / Flex Banner": "heavy-duty outdoor vinyl flex banner, vivid printed graphics, matte finish",
        "Bạt Không Gân Khung Sắt": "high-definition seamless flex banner stretched taut on square iron truss frame",
        "Gỗ Vintage / Khắc Laser": "rustic polished dark wood board with laser-engraved typography and warm amber lighting",
        "Decal Sắc Nét / Màng Mờ": "ultra-sharp die-cut vinyl sticker sheet, premium matte lamination, vibrant color accuracy"
    }

    selected_mat = material_prompts.get(material, "premium outdoor advertising display panel, crisp print layout")

    if "Biển hiệu" in product_type:
        prompt = (
            f"Commercial storefront outdoor signboard design for '{brand_name}'. "
            f"Subject text/title reads '{title}'. Main brand color theme: {main_colors}. "
            f"Style: {style}, modern architectural facade background, eye-level street view perspective. "
            f"Crafted from {selected_mat}. "
            f"Layout structure: Bold brand logo on left, prominent centered primary typography, secondary services list and phone number clearly readable in bottom right footer. "
            f"Professional advertising design, perfectly proportioned typography hierarchy, clean grid alignment, photorealistic 8k render --ar {aspect_ratio}"
        )

    elif "Standee" in product_type:
        prompt = (
            f"Vertical advertising floor roll-up standee banner layout design for '{brand_name}'. "
            f"Promoting: '{title}'. Details: '{sub_details}'. Color scheme: {main_colors}. "
            f"Style: {style}. Crafted with {selected_mat}. "
            f"Crucial layout rules: Top 20% features bold '{brand_name}' logo. Middle section presents hero product illustration and key headline '{title}'. "
            f"Lower section contains contact info '{contact_info}'. Bottom 15% left completely clear of important text for physical standee base structure. "
            f"Clean modern corporate marketing graphic design, high contrast, studio lighting --ar {aspect_ratio}"
        )

    elif "Bảng vẫy" in product_type:
        prompt = (
            f"Double-sided outdoor hanging projection blade sign mounted on shop exterior wall. "
            f"Brand name: '{brand_name}'. Icon/Title: '{title}'. Color palette: {main_colors}. "
            f"Style: {style}. Materials: {selected_mat}, mounted on ornate wrought iron wall bracket. "
            f"Features glowing LED edge lighting, high contrast day/night visibility, photorealistic street view shot --ar {aspect_ratio}"
        )

    elif "Băng rôn" in product_type:
        prompt = (
            f"Wide horizontal promotional outdoor vinyl banner design for '{brand_name}'. "
            f"Event/Promotion title: '{title}'. Key message: '{sub_details}'. Color palette: {main_colors}. "
            f"Style: {style}, highly energetic and eye-catching. Crafted in {selected_mat}. "
            f"Layout: Big bold typography visible from 50 meters away, prominent discount/offer box, phone hotline '{contact_info}' prominently displayed in footer box. "
            f"Commercial print file layout, ultra-sharp vector graphics --ar {aspect_ratio}"
        )

    elif "Menu" in product_type:
        prompt = (
            f"Professional food and beverage menu board layout for '{brand_name}'. "
            f"Menu title: '{title}'. Theme colors: {main_colors}. Style: {style}. "
            f"Layout structure: Header with '{brand_name}' logo, structured 2-column food/drink item list with elegant prices, high-quality mouth-watering hero food photography inserts. "
            f"Print-ready graphic design, immaculate typography, clear visual hierarchy --ar {aspect_ratio}"
        )

    else:
        prompt = (
            f"Die-cut packaging sticker decal label design for '{brand_name}'. "
            f"Product title: '{title}'. Sub-info: '{sub_details}'. Color theme: {main_colors}. "
            f"Style: {style}. Finish: {selected_mat}. "
            f"Features central product illustration, sharp brand logo at top, clear border cutlines, high-contrast readable text. "
            f"Graphic design mockup, flat lay on neutral surface, ultra-detailed 8k vector render --ar {aspect_ratio}"
        )

    negative_prompt = "blurry text, distorted logo, misaligned layout, low resolution, crowded text at bottom edge, chaotic layout, dark illegible background"
    mj_command = f"/imagine prompt: {prompt}"
    
    return {
        "full_prompt": prompt,
        "mj_command": mj_command,
        "negative_prompt": negative_prompt,
        "aspect_ratio": aspect_ratio
    }


# ==============================================================================
# 4. THƯ VIỆN PROMPT PHỤ TRỢ (AUXILIARY PROMPTS)
# ==============================================================================
AUXILIARY_TOOLKIT = {
    "2d_to_3d_perspective": {
        "title": "1. Dựng Phối cảnh 3D từ Phác thảo 2D / Ảnh chụp tay",
        "description": "Chuyển ảnh nét vẽ tay hoặc file 2D phẳng thành phối cảnh 3D thực tế cài đặt trên mặt tiền cửa hàng.",
        "prompt_template": (
            "Photorealistic 3D architectural mockup of a store signboard based on a 2D flat sketch. "
            "Convert flat 2D layout into 3D dimensional acrylic letters with 5cm depth mounted on a dark textured aluminum composite panel wall. "
            "Eye-level perspective view from street level, natural ambient sunlight, subtle realistic drop shadows, photorealistic architectural rendering."
        )
    },
    "mockup_real_world": {
        "title": "2. Tạo ảnh Mockup Sản phẩm Thực tế (Real-world Mockup)",
        "description": "Đặt mẫu thiết kế (Standee, Bảng vẫy, Menu, Tem nhãn) vào không gian showroom/sảnh thực tế để gửi khách duyệt.",
        "prompt_template": (
            "Professional realistic product mockup of [INSERT_PRODUCT_TYPE] placed inside a modern brightly lit retail showroom interior. "
            "Soft studio illumination, shallow depth of field, neutral aesthetic background, realistic reflections, 8k resolution display."
        )
    },
    "day_night_lighting": {
        "title": "3. Diễn họa Biển hiệu Ban đêm & Hiệu ứng Đèn LED / Neon",
        "description": "Mô phỏng biển bảng rực rỡ vào ban đêm với hệ thống đèn LED hắt chân, Module LED P10 hoặc đèn Neon Sign.",
        "prompt_template": (
            "Nighttime urban street view photo of a glowing store signboard. "
            "Illuminated with vibrant backlit LED halo glow around 3D stainless steel channel letters and outdoor P10 LED matrix panel. "
            "Atmospheric twilight background, wet pavement reflections, dramatic contrast, photorealistic cinematic lighting."
        )
    },
    "material_simulation": {
        "title": "4. Mô phỏng & Sao chép Chất liệu Thi công",
        "description": "Tạo hiệu ứng bề mặt chất liệu inox xước, nhôm tổ ong, bảng LED P10, mica trong suốt, bạt hiflex cao cấp.",
        "prompt_template": (
            "Close-up macro photography of advertising materials: 3D electroplated gold mirror stainless steel letters, "
            "layered on top of matte black aluminum honeycomb panels with P10 LED display. Crisp metallic reflections, high tactile texture detail, 8k."
        )
    },
    "sketch_to_vector": {
        "title": "5. Chuẩn hóa Nét vẽ tay / Ảnh chụp chữ viết tay",
        "description": "Tự động trích xuất thông tin từ ghi chú tay của khách hàng thành bố cục bảng hiệu chuyên nghiệp.",
        "prompt_template": (
            "Clean graphic vector layout extracted from handwritten customer notes. "
            "Crisp typography hierarchy, perfectly aligned alignment grid, clean bold branding layout, high contrast white background, vector ready for print."
        )
    }
}


# ==============================================================================
# 5. GIAO DIỆN STREAMLIT (UI)
# ==============================================================================
st.set_page_config(
    page_title="Trợ lý AI Quảng cáo & In ấn v3",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1E293B; text-align: center; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #0284C7; text-align: center; margin-bottom: 1.5rem; font-weight: 600; }
    .warning-card { background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 0.8rem; border-radius: 0.5rem; color: #991B1B; font-size: 0.9rem; margin-bottom: 0.8rem; }
    .success-card { background-color: #F0FDF4; border-left: 4px solid #22C55E; padding: 0.8rem; border-radius: 0.5rem; color: #166534; font-size: 0.9rem; margin-bottom: 0.8rem; }
    .led-card { background-color: #F0F9FF; border: 1.5px solid #0284C7; padding: 1rem; border-radius: 0.6rem; color: #0369A1; font-size: 0.92rem; margin-bottom: 1rem; }
    .stButton>button { background-color: #0284C7; color: white; font-weight: bold; border-radius: 0.5rem; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-header'>🖨️ TRỢ LÝ AI CHUYÊN NGÀNH QUẢNG CÁO & IN ẤN (v3)</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Bố cục In ấn • Động cơ Prompt AI • Tự động Tính toán Số lượng Module LED P10</div>", unsafe_allow_html=True)

st.sidebar.title("DANH MỤC TÍNH NĂNG")
app_mode = st.sidebar.radio(
    "Chọn chức năng:",
    [
        "🛠️ Tạo Thiết kế 6 Ấn phẩm Cốt lõi",
        "⚡ Tính toán Module LED P10 & Vật tư",
        "📐 Sơ đồ Bố cục & Quy chuẩn Kỹ thuật",
        "🚀 Bộ Trợ thủ Prompt Phụ trợ",
        "📚 Cẩm nang Thi công & Bí quyết AI"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Mẹo thực chiến:**\n"
    "• Nhập thông tin thô từ khách hàng.\n"
    "• AI tự chừa vùng safe zone & lề xả xéo.\n"
    "• Tự động tính số lượng tấm LED P10, công suất & số nguồn 5V40A!"
)

# TAB 1: CREATOR
if app_mode == "🛠️ Tạo Thiết kế 6 Ấn phẩm Cốt lõi":
    st.subheader("🎯 Bộ Khởi tạo Bố cục & Prompt Thiết kế chuẩn Quy cách In")
    col_input, col_output = st.columns([1, 1.2])

    with col_input:
        st.markdown("### 1. Thông tin Đầu vào")
        product_type = st.selectbox(
            "Loại ấn phẩm quảng cáo:",
            ["Biển hiệu (Signboard)", "Standee (Cuốn / Khung X)", "Bảng vẫy (Hanging Sign)", "Băng rôn (Banner)", "Menu (Bảng giá)", "Tem nhãn Decal"]
        )

        brand_name = st.text_input("Tên Cửa hàng / Thương hiệu:", value="NHÀ HÀNG HẢI SẢN BIỂN ĐÔNG")
        title = st.text_input("Tiêu đề chính / Thông điệp cốt lõi:", value="TƯƠI SỐNG MỖI NGÀY - GIẢM 20% TỔNG HÓA ĐƠN")
        sub_details = st.text_area("Nội dung dịch vụ / Danh mục chính:", value="• Cua Cà Mau • Tôm Hùm Nha Trang • Lẩu Hải Sản\n• Đặt bàn trước giảm thêm 5%", height=80)
        contact_info = st.text_input("Hotline / Địa chỉ liên hệ:", value="0988.123.456 - 123 Nguyễn Văn Cừ, Q.1")

        st.markdown("#### Kích thước & Quy cách:")
        col_w, col_h = st.columns(2)
        with col_w:
            default_w = 320.0 if "Biển hiệu" in product_type else (60.0 if "Standee" in product_type else (100.0 if "Bảng vẫy" in product_type else (500.0 if "Băng rôn" in product_type else (21.0 if "Menu" in product_type else 10.0))))
            width = st.number_input("Chiều rộng (cm):", value=default_w, min_value=5.0, max_value=2000.0)
        with col_h:
            default_h = 96.0 if "Biển hiệu" in product_type else (160.0 if "Standee" in product_type else (100.0 if "Bảng vẫy" in product_type else (100.0 if "Băng rôn" in product_type else (29.7 if "Menu" in product_type else 10.0))))
            height = st.number_input("Chiều cao (cm):", value=default_h, min_value=5.0, max_value=2000.0)

        col_style, col_mat = st.columns(2)
        with col_style:
            style = st.selectbox("Phong cách thiết kế:", ["Hiện đại & Trẻ trung", "Sang trọng & VIP", "Cổ điển / Vintage", "Tối giản & Tinh tế", "Nổi bật & Rực rỡ"])
        with col_mat:
            material = st.selectbox("Chất liệu thi công dự kiến:", [
                "Bảng LED Module P10", 
                "Nhôm Tổ Ong (Aluminum Honeycomb)", 
                "Alu + Mica nổi đèn LED", 
                "Inox mạ vàng 3D + Neon", 
                "Bạt Hiflex / Flex Banner", 
                "Bạt Không Gân Khung Sắt", 
                "Gỗ Vintage / Khắc Laser", 
                "Decal Sắc Nét / Màng Mờ"
            ])

        main_colors = st.text_input("Màu sắc chủ đạo (Nền - Chữ):", value="Xanh dương biển - Vàng kim - Trắng")
        generate_btn = st.button("🚀 XUẤT BỐ CỤC & PROMPT AI", width='stretch')

    with col_output:
        st.markdown("### 2. Kết quả Bố cục & Prompt AI")
        if generate_btn or 'generated' not in st.session_state:
            st.session_state['generated'] = True
            st.session_state['wireframe'] = generate_layout_wireframe(product_type, width, height, brand_name, title, contact_info, sub_details, material)
            st.session_state['ai_prompt'] = generate_ai_prompt(product_type, width, height, brand_name, title, main_colors, style, material, contact_info, sub_details)

        st.image(st.session_state['wireframe'], caption="Sơ đồ Bố cục Quy chuẩn In & Thi công", width='stretch')

        if "Bảng LED Module P10" in material:
            led_res = calculate_led_p10(width, height)
            st.markdown(f"""
            <div class='led-card'>
                ⚡ <b>BẢNG DỰ TOÁN KỸ THUẬT LED MATRIX P10 (32x16cm):</b><br/>
                • <b>Số lượng Module:</b> <code>{led_res['total_modules']} TẤM</code> ({led_res['cols']} Cột x {led_res['rows']} Hàng)<br/>
                • <b>Kích thước thực tế chuẩn tấm:</b> <code>{led_res['actual_width']} x {led_res['actual_height']} cm</code><br/>
                • <b>Độ phân giải hiển thị:</b> <code>{led_res['total_px_w']} x {led_res['total_px_h']} Pixels</code> ({led_res['total_pixels']:,} điểm ảnh)<br/>
                • <b>Công suất tiêu thụ tối đa:</b> <code>{led_res['max_power_w']} W</code> (Trung bình ~{led_res['avg_power_w']} W)<br/>
                • <b>Khuyên dùng Nguồn 5V 40A (200W):</b> <code>{led_res['psu_count_5v40a']} Nguồn</code><br/>
                • <b>Mạch / Card điều khiển đề xuất:</b> {led_res['card_type']}
            </div>
            """, unsafe_allow_html=True)
        elif "Standee" in product_type:
            st.markdown("<div class='warning-card'>⚠️ <b>LƯU Ý THI CÔNG STANDEE:</b> Vùng 30cm chân dưới cùng bị che khuất bởi đế cắm/khung cuốn. Tuyệt đối không đặt SĐT hay địa chỉ ở đáy!</div>", unsafe_allow_html=True)
        elif "Biển hiệu" in product_type:
            st.markdown("<div class='success-card'>✅ <b>QUY CHUẨN BIỂN HỆU:</b> Tỷ lệ Logo (20-25%), Tiêu đề chính (50%), Liên hệ (25-30%). Đã bù lề gấp viền 3cm.</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🤖 Prompt Kỹ thuật cho AI (Midjourney / Flux / DALL-E 3):")
        prompt_data = st.session_state['ai_prompt']
        st.code(prompt_data['mj_command'], language="bash")
        
        with st.expander("🔍 Xem chi tiết Prompt tiếng Anh & Negative Prompt"):
            st.markdown("**Prompt Tiếng Anh chi tiết:**")
            st.text_area("Full Prompt", prompt_data['full_prompt'], height=100)
            st.markdown("**Negative Prompt (Từ khóa loại trừ):**")
            st.text(prompt_data['negative_prompt'])
            st.markdown(f"**Tỷ lệ khung hình (--ar):** `{prompt_data['aspect_ratio']}`")

# TAB 2: LED CALCULATOR
elif app_mode == "⚡ Tính toán Module LED P10 & Vật tư":
    st.subheader("⚡ Bộ Công cụ Tính toán Số lượng Module LED & Vật tư Thi công")
    st.markdown("Nhập kích thước biển bảng dự kiến để AI tự động tính chính xác số tấm LED 32x16cm, công suất điện và linh kiện đi kèm.")
    
    col_l1, col_l2 = st.columns([1, 1.2])
    
    with col_l1:
        st.markdown("### 1. Thông số Biển LED dự kiến")
        mod_type = st.selectbox("Chọn chủng loại Module LED:", [
            "P10 Outdoor (32x16cm)",
            "P5 Outdoor (32x16cm)",
            "P3.08 Indoor (32x16cm)",
            "P2.5 Indoor (32x16cm)"
        ])
        
        inp_w = st.number_input("Chiều rộng mong muốn (cm):", value=320.0, step=10.0, min_value=10.0, max_value=3000.0)
        inp_h = st.number_input("Chiều cao mong muốn (cm):", value=96.0, step=10.0, min_value=10.0, max_value=3000.0)
        
        price_per_mod = st.number_input("Đơn giá 1 tấm Module (VNĐ):", value=65000, step=5000)
        price_per_psu = st.number_input("Đơn giá 1 Nguồn 5V 40A (VNĐ):", value=115000, step=5000)
        price_card = st.number_input("Đơn giá Mạch / Card điều khiển (VNĐ):", value=250000, step=10000)
        
        calc_res = calculate_led_p10(inp_w, inp_h, mod_type)

    with col_l2:
        st.markdown("### 2. Kết quả Tính toán & Bảng Vật tư")
        
        st.success(f"🎯 **Cần sử dụng:** `{calc_res['total_modules']} TẤM MODULE` ({calc_res['cols']} Cột x {calc_res['rows']} Hàng)")
        
        st.markdown(f"""
        * **Kích thước thực tế chuẩn ghép tấm:** `{calc_res['actual_width']} cm x {calc_res['actual_height']} cm`
        * **Tổng số điểm ảnh (Resolution):** `{calc_res['total_px_w']} x {calc_res['total_px_h']} Pixels` (`{calc_res['total_pixels']:,}` điểm LED)
        * **Công suất điện tối đa:** `{calc_res['max_power_w']} W` (Công suất trung bình: ~`{calc_res['avg_power_w']} W`)
        * **Số lượng Nguồn 5V 40A (200W):** `{calc_res['psu_count_5v40a']} Cái` (Chạy ở 80% tải an toàn)
        * **Mạch điều khiển phù hợp:** `{calc_res['card_type']}`
        """)
        
        # Cost table
        cost_mod = calc_res['total_modules'] * price_per_mod
        cost_psu = calc_res['psu_count_5v40a'] * price_per_psu
        cost_card = price_card
        total_mat_cost = cost_mod + cost_psu + cost_card
        
        st.markdown("#### Bảng Ước tính Chi phí Vật tư Chính:")
        df_cost = pd.DataFrame([
            {"Hạng mục vật tư": f"Module {calc_res['module_name']}", "Số lượng": f"{calc_res['total_modules']} tấm", "Đơn giá (VNĐ)": f"{price_per_mod:,}", "Thành tiền (VNĐ)": f"{cost_mod:,}"},
            {"Hạng mục vật tư": "Nguồn 5V 40A ngoài trời", "Số lượng": f"{calc_res['psu_count_5v40a']} cái", "Đơn giá (VNĐ)": f"{price_per_psu:,}", "Thành tiền (VNĐ)": f"{cost_psu:,}"},
            {"Hạng mục vật tư": "Mạch / Card điều khiển LED", "Số lượng": "1 bộ", "Đơn giá (VNĐ)": f"{price_card:,}", "Thành tiền (VNĐ)": f"{cost_card:,}"},
            {"Hạng mục vật tư": "TỔNG CHI PHÍ LINH KIỆN VẬT TƯ", "Số lượng": "-", "Đơn giá (VNĐ)": "-", "Thành tiền (VNĐ)": f"{total_mat_cost:,}"}
        ])
        st.table(df_cost)
        st.caption("*(Lưu ý: Chưa bao gồm khung sắt cabinet, dây điện, ốc nam chân và công lắp đặt thi công)*")

# TAB 3: WIREFRAME
elif app_mode == "📐 Sơ đồ Bố cục & Quy chuẩn Kỹ thuật":
    st.subheader("📐 Xem & Tải Sơ đồ Bố cục Kỹ thuật (Technical Blueprint)")
    col1, col2 = st.columns([1, 2])
    with col1:
        p_type = st.selectbox("Chọn loại sản phẩm cần xem quy chuẩn:", ["Standee (Cuốn / Khung X)", "Biển hiệu (Signboard)", "Bảng vẫy (Hanging Sign)", "Băng rôn (Banner)", "Menu (Bảng giá)", "Tem nhãn Decal"])
        w = st.number_input("Rộng (cm)", value=60.0 if "Standee" in p_type else 320.0)
        h = st.number_input("Cao (cm)", value=160.0 if "Standee" in p_type else 96.0)
        b_name = st.text_input("Tên thương hiệu mẫu", "XƯỞNG IN QUẢNG CÁO PRO")
        t_title = st.text_input("Tiêu đề mẫu", "THIẾT KẾ & IN ẤN NHANH LẤY NGAY")
        c_info = st.text_input("Liên hệ mẫu", "0909.888.999 - xuerngin.vn")
        mat_sel = st.selectbox("Chất liệu mẫu:", ["Bảng LED Module P10", "Alu + Mica nổi đèn LED", "Nhôm Tổ Ong (Aluminum Honeycomb)", "Bạt Hiflex / Flex Banner"])
        wf_buf = generate_layout_wireframe(p_type, w, h, b_name, t_title, c_info, material=mat_sel)

    with col2:
        st.image(wf_buf, caption=f"Sơ đồ Quy cách {p_type} - Kích thước {w}x{h}cm", width='stretch')
        st.download_button("📥 Tải Sơ đồ Bố cục Wireframe (PNG)", data=wf_buf, file_name=f"wireframe_{p_type}_{w}x{h}.png", mime="image/png")

# TAB 4: AUXILIARY PROMPTS
elif app_mode == "🚀 Bộ Trợ thủ Prompt Phụ trợ":
    st.subheader("🚀 Bộ Thư viện Prompt Phụ trợ Chuyên biệt Ngành In")
    brand_input = st.text_input("Tên Thương hiệu / Cửa hàng của bạn:", "LƯU GIA COFFEE")
    custom_desc = st.text_input("Mô tả bổ sung (nếu có):", "Quán cà phê phong cách Indochine, tông màu nâu gỗ ấm")

    for key, tool_data in AUXILIARY_TOOLKIT.items():
        with st.expander(f"📌 {tool_data['title']}"):
            st.write(f"**Mô tả:** {tool_data['description']}")
            pmt = tool_data["prompt_template"].replace("[INSERT_PRODUCT_TYPE]", custom_desc if custom_desc else "advertising display")
            st.code(f"/imagine prompt: {pmt}", language="bash")

# TAB 5: GUIDE
else:
    st.subheader("📚 Quy trình Thực chiến: Đưa AI vào Xưởng In & Quảng cáo")
    st.markdown("""
    ### 🔑 Quy trình 4 Bước Tối ưu Thời gian & Chi phí cho Xưởng In:
    1. **Bước 1:** Tiếp nhận nội dung thô từ khách hàng (chữ viết tay, file ghi chú, ảnh chụp).
    2. **Bước 2:** Nhập vào ứng dụng để tự động phân bổ lề an toàn, lề xả xéo và khoảng bù chân Standee.
    3. **Bước 3:** Sử dụng **Bộ tính toán LED P10** để ra ngay số lượng tấm, công suất điện và số nguồn 5V40A.
    4. **Bước 4:** Sao chép Prompt AI dán vào Midjourney/Flux để xuất 4 mẫu phối cảnh 3D siêu nét gửi khách chốt nhanh!
    """)
    st.success("🎉 **Ứng dụng phiên bản 3 đã hoàn chỉnh và tích hợp thành công Động cơ Tính toán Module LED P10 & Báo giá Vật tư!**")