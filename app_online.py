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

# Kolom DP Default 0 (Bisa dikosongkan)
dp_paid = st.number_input("Sudah Dibayar / Masuk DP (Rp) - Isi 0 jika tanpa DP", min_value=0, value=0, step=50000)
remaining_payment = max(0, subtotal - dp_paid)

subtotal_idr = f"Rp {subtotal:,.0f}".replace(",", ".")
dp_paid_idr
