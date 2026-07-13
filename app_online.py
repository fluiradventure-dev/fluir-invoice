import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os

# --- FUNGSI OTOMATISASI NOMOR INVOICE ---
COUNTER_FILE = "invoice_counter.txt"

def get_next_invoice_number():
    # Jika file belum ada, mulai dari nomor bawaan Anda (21872)
    if not os.path.exists(COUNTER_FILE):
        return 21872
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 21872

def save_next_invoice_number(current_number):
    with open(COUNTER_FILE, "w") as f:
        f.write(str(current_number + 1))

# Ambil nomor urut berikutnya
next_inv = get_next_invoice_number()

st.set_page_config(page_title="Fluir Billing System", layout="wide", page_icon="📄")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    div.stButton > button:first-child {
        background-color: #e67e22;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Fluir Invoice Generator")
st.caption("Aplikasi pembuat invoice resmi CV Fluir Travelindo dengan penomoran otomatis bertambah +1.")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Detail Invoice")

# Input nomor invoice sekarang otomatis mengambil dari urutan database file
inv_number = st.sidebar.text_input("Nomor Invoice (#)", value=str(next_inv))
inv_date = st.sidebar.date_input("Tanggal Invoice", datetime.today())

st.sidebar.header("👤 Dituju Kepada")
client_name = st.sidebar.text_input("Nama Pelanggan", "Teh Tari")
client_phone = st.sidebar.text_input("Nomor Telepon", "0896-1741-4370")
client_address = st.sidebar.text_area("Lokasi / Instansi", "Glamping lakeside")

st.sidebar.header("📅 Jadwal Event")
event_date_time = st.sidebar.text_input("Tanggal & Waktu Kegiatan", value="15 - 16 Mei 2026 (08:00 WIB)")

# Main Form Items
st.subheader("🛍️ Item Pesanan")

if 'invoice_items' not in st.session_state:
    st.session_state.invoice_items = [
        {"desc": "@Green Corner Pangalengan", "qty": 2, "price": 900000}
    ]

with st.expander("➕ Tambah Rincian Item Baru", expanded=False):
    c1, c2 = st.columns([3, 1])
    with c1:
        new_desc = st.text_input("Deskripsi Item / Layanan", placeholder="Contoh: @Green Corner Pangalengan")
    with c2:
        new_qty = st.number_input("Kuantitas", min_value=1, value=1)
        new_price = st.number_input("Harga Satuan (Rp)", min_value=0, step=50000, value=500000)
    
    if st.button("Tambahkan Item"):
        if new_desc:
            st.session_state.invoice_items.append({"desc": new_desc, "qty": new_qty, "price": new_price})
            st.rerun()

if st.session_state.invoice_items:
    df = pd.DataFrame(st.session_state.invoice_items)
    df['Jumlah'] = df['qty'] * df['price']
    
    df_render = df.copy()
    df_render['Harga'] = df_render['price'].apply(lambda x: f"Rp{x:,}".replace(",", "."))
    df_render['Jumlah'] = df_render['Jumlah'].apply(lambda x: f"Rp{x:,}".replace(",", "."))
    df_render.columns = ['Deskripsi', 'Kuantitas', 'price', 'Harga', 'Jumlah']
    
    st.table(df_render[['Deskripsi', 'Kuantitas', 'Harga', 'Jumlah']])
    
    if st.button("🗑️ Kosongkan Tabel"):
        st.session_state.invoice_items = []
        st.rerun()

# Financial Summary Calculation
subtotal = sum(item['qty'] * item['price'] for item in st.session_state.invoice_items)
dp_paid = st.number_input("Sudah Di bayar / Masuk DP (Rp)", min_value=0, value=600000, step=50000)
remaining_payment = max(0, subtotal - dp_paid)

st.markdown("---")

if st.button("🚀 Cetak Invoice Desain Baru", type="primary"):
    if not client_name:
        st.error("Nama Pelanggan wajib diisi!")
    else:
        # Simpan counter nomor baru (+1) untuk invoice berikutnya
        try:
            save_next_invoice_number(int(inv_number))
        except:
            pass

        # Build Rows
        rows_html = ""
        for item in st.session_state.invoice_items:
            item_total = item['qty'] * item['price']
            rows_html += f"""
            <tr>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded;'>{item['desc']}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: center;'>{item['qty']}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>Rp{item['price']:,}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>Rp{item_total:,}</td>
            </tr>
            """.replace(",", ".")
            
        event_info_html = f"<b>Kegiatan:</b> {event_date_time}<br>" if event_date_time else ""
        
        if remaining_payment == 0:
            status_badge_html = """
            <div style='border: 3px solid #27ae60; color: #27ae60; display: inline-block; 
                        padding: 4px 12px; font-size: 13pt; font-weight: bold; 
                        text-transform: uppercase; border-radius: 4px; margin-top: 15px; 
                        letter-spacing: 1px; transform: rotate(-3deg); opacity: 0.85;'>
                LUNAS / PAID
            </div>
            """
        else:
            status_badge_html = ""
            
        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8'>
            <title>Invoice #{inv_number}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #2c3e50; padding: 25px; line-height: 1.4; font-size: 10pt; }}
                .hdr-table {{ width: 100%; margin-bottom: 25px; border-bottom: 2px solid #e67e22; padding-bottom: 15px; }}
                .company-details {{ font-size: 9pt; color: #7f8c8d; text-align: right; line-height: 1.3; }}
                .info-table {{ width: 100%; margin-bottom: 25px; }}
                .info-cell {{ vertical-align: top; width: 50%; }}
                .section-title {{ font-size: 8pt; font-weight: bold; text-transform: uppercase; color: #95a5a6; margin-bottom: 5px; letter-spacing: 0.5px; }}
                table.items {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                table.items th {{ background-color: #f8f9fa; color: #34495e; padding: 10px; font-size: 9pt; text-transform: uppercase; border-bottom: 2px solid #bdc3c7; }}
                .split-container {{ width: 100%; overflow: hidden; margin-top: 15px; padding-bottom: 15px; border-bottom: 1px dashed #eaeded; }}
                .right-block {{ float: right; width: 42%; text-align: right; }}
                .summary-table {{ width: 100%; border-collapse: collapse; }}
                .summary-table td {{ padding: 7px 10px; border-bottom: 1px solid #f2f4f4; font-size: 10pt; }}
                .notes-list {{ padding-left: 15px; margin: 5px 0 0 0; font-size: 8.5pt; color: #626567; }}
                .notes-list li {{ margin-bottom: 3px; }}
                .bottom-layout-table {{ width: 100%; margin-top: 40px; border-collapse: collapse; page-break-inside: avoid; }}
                .bottom-layout-cell {{ width: 50%; vertical-align: top; font-size: 10pt; }}
            </style>
        </head>
        <body onload="window.print()">
            <table class='hdr-table'>
                <tr>
                    <td><img src="https://raw.githubusercontent.com/fluiradventure-dev/fluir-invoice/main/FLUIR%20LOGO%201.webp" style="height: 55px;"></td>
                    <td class='company-details'>
                        <b>CV Fluir Travelindo</b><br>
                        JL. Situ Cileunca No24 Pangalengan<br>
                        Bandung Jawa barat 40378<br>
                        NPWP: 91.570.415.9
