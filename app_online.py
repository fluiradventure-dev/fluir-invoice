import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import os

# --- FUNGSI OTOMATISASI NOMOR INVOICE ---
COUNTER_FILE = "invoice_counter.txt"

def get_next_invoice_number():
    if not os.path.exists(COUNTER_FILE):
        return 21872
    try:
        with open(COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 21872

def save_next_invoice_number(current_number):
    try:
        with open(COUNTER_FILE, "w") as f:
            f.write(str(current_number + 1))
    except Exception as e:
        st.error(f"Gagal memperbarui nomor invoice di server: {e}")

# Ambil nomor urut berikutnya sebelum page config
next_inv = get_next_invoice_number()

st.set_page_config(page_title="Fluir Billing System", layout="wide", page_icon="📄")

# Custom CSS untuk tombol dan tata letak Streamlit
st.markdown("<style>.main .block-container { padding-top: 1.5rem; } div.stButton > button:first-child { background-color: #e67e22; color: white; border-radius: 6px; border: none; font-weight: bold; }</style>", unsafe_allow_html=True)

st.title("📄 Fluir Invoice Generator")
st.caption("Aplikasi pembuat invoice resmi CV Fluir Travelindo dengan penomoran otomatis bertambah +1.")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Detail Invoice")
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
    df_render['Harga'] = df_render['price'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    df_render['Jumlah'] = df_render['Jumlah'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    
    df_render.columns = ['Deskripsi', 'Kuantitas', 'price', 'Harga', 'Jumlah']
    st.table(df_render[['Deskripsi', 'Kuantitas', 'Harga', 'Jumlah']])
    
    if st.button("🗑️ Kosongkan Tabel"):
        st.session_state.invoice_items = []
        st.rerun()

# Financial Summary Calculation
subtotal = sum(item['qty'] * item['price'] for item in st.session_state.invoice_items)

# Kolom DP Pilihan (Bisa dikosongkan / diisi 0 jika tanpa DP)
dp_paid = st.number_input("Sudah Dibayar / Masuk DP (Rp) - Isi 0 jika tanpa DP", min_value=0, value=0, step=50000)
remaining_payment = max(0, subtotal - dp_paid)

subtotal_idr = f"Rp {subtotal:,.0f}".replace(",", ".")
dp_paid_idr = f"Rp {dp_paid:,.0f}".replace(",", ".")
remaining_payment_idr = f"Rp {remaining_payment:,.0f}".replace(",", ".")

st.markdown("---")

if 'invoice_ready' not in st.session_state:
    st.session_state.invoice_ready = False
if 'html_buffer' not in st.session_state:
    st.session_state.html_buffer = ""

if st.button("🚀 Cetak Invoice Desain Baru", type="primary"):
    if not client_name:
        st.error("❌ Nama Pelanggan wajib diisi sebelum mencetak!")
    elif not st.session_state.invoice_items:
        st.error("❌ Tabel item pesanan masih kosong!")
    else:
        try:
            save_next_invoice_number(int(inv_number))
        except:
            pass

        rows_html = ""
        row_template = "<tr><td style='padding: 12px 10px; border-bottom: 1px solid #eaeded;'>[DESC]</td><td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: center;'>[QTY]</td><td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>[PRICE]</td><td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>[TOTAL]</td></tr>"
        
        for item in st.session_state.invoice_items:
            item_total = item['qty'] * item['price']
            formatted_price = f"Rp {item['price']:,.0f}".replace(",", ".")
            formatted_total = f"Rp {item_total:,.0f}".replace(",", ".")
            rows_html += row_template.replace("[DESC]", str(item['desc'])).replace("[QTY]", str(item['qty'])).replace("[PRICE]", formatted_price).replace("[TOTAL]", formatted_total)
            
        event_info_html = f"<b>Kegiatan:</b> {event_date_time}<br>" if event_date_time else ""
        status_badge_html = "<div style='border: 3px solid #27ae60; color: #27ae60; display: inline-block; padding: 4px 12px; font-size: 13pt; font-weight: bold; text-transform: uppercase; border-radius: 4px; margin-top: 15px; letter-spacing:
