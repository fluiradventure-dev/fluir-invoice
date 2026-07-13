import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64

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

st.title("📄 Fluir Invoice Generator (Desain Baru)")
st.caption("Aplikasi pembuat invoice dengan layout terstruktur sesuai standar CV Fluir Travelindo.")
st.markdown("---")

# Sidebar Configuration
st.sidebar.header("⚙️ Detail Invoice")
inv_number = st.sidebar.text_input("Nomor Invoice (#)", "21872")
inv_date = st.sidebar.date_input("Tanggal Invoice", datetime.today())

st.sidebar.header("👤 Dituju Kepada")
client_name = st.sidebar.text_input("Nama Pelanggan", "Teh Tari")
client_phone = st.sidebar.text_input("Nomor Telepon", "0896-1741-4370")
client_address = st.sidebar.text_area("Lokasi / Instansi", "Glamping lakeside")

# BARU: Input Tanggal & Waktu Kegiatan di Sidebar
st.sidebar.header("📅 Jadwal Event")
event_date_time = st.sidebar.text_input("Tanggal & Waktu Kegiatan", placeholder="Contoh: 15 - 16 Mei 2026 (08:00 WIB)")

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
dp_paid = st.number_input("Sudah DP (Rp)", min_value=0, value=600000, step=50000)
remaining_payment = max(0, subtotal - dp_paid)

st.markdown("---")

if st.button("🚀 Cetak Invoice Desain Baru", type="primary"):
    if not client_name:
        st.error("Nama Pelanggan wajib diisi!")
    else:
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
            
        # Format teks jika input kegiatan kosong
        event_info_html = f"<b>Kegiatan:</b> {event_date_time}<br>" if event_date_time else ""
            
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
                .split-container {{ width: 100%; overflow: hidden; margin-top: 15px; }}
                .left-block {{ float: left; width: 55%; }}
                .right-block {{ float: right; width: 40%; }}
                .summary-table {{ width: 100%; border-collapse: collapse; }}
                .summary-table td {{ padding: 6px 8px; border-bottom: 1px solid #f2f4f4; }}
                .badge-container {{ background-color: #f4f6f7; padding: 12px; border-radius: 6px; margin-top: 10px; border-left: 4px solid #e67e22; }}
                .notes-list {{ padding-left: 15px; margin: 5px 0 0 0; font-size: 8.5pt; color: #626567; }}
                .notes-list li {{ margin-bottom: 3px; }}
            </style>
        </head>
        <body onload="window.print()">
            <!-- Header (Logo Terintegrasi) -->
            <table class='hdr-table'>
                <tr>
                    <td><img src="https://raw.githubusercontent.com/fluiradventure-dev/fluir-invoice/main/FLUIR%20LOGO%201.webp" style="height: 55px;"></td>
                    <td class='company-details'>
                        <b>CV Fluir Travelindo</b><br>
                        JL. Situ Cileunca No24 Pangalengan<br>
                        Bandung Jawa barat 40378<br>
                        NPWP: 91.570.415.9-404.000<br>
                        Hub: 081386000797 | fluiradventure@gmail.com
                    </td>
                </tr>
            </table>
            
            <!-- Metadata info -->
            <table class='info-table'>
                <tr>
                    <td class='info-cell'>
                        <div class='section-title'>Dituju Kepada</div>
                        <b>{client_name}</b><br>
                        {client_phone}<br>
                        {client_address}
                    </td>
                    <td class='info-cell' style='text-align: right;'>
                        <div class='section-title'>Data Dokumen</div>
                        <b>Invoice #</b> {inv_number}<br>
                        <b>Tanggal:</b> {inv_date.strftime('%B %d, %Y')}<br>
                        {event_info_html}
                    </td>
                </tr>
            </table>

            <!-- Table items -->
            <table class='items'>
                <thead>
                    <tr>
                        <th style='text-align: left; width: 50%;'>Deskripsi</th>
                        <th style='width: 15%; text-align: center;'>Kuantitas</th>
                        <th style='width: 17%; text-align: right;'>Harga</th>
                        <th style='width: 18%; text-align: right;'>Jumlah</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <!-- Split bottom section -->
            <div class='split-container'>
                <!-- Left Details (Payments & Notes) -->
                <div class='left-block'>
                    <div class='section-title'>Instruksi Pembayaran</div>
                    <div style='font-size: 9pt; color: #2c3e50; margin-bottom: 15px;'>
                        Bank Transfer: <b>BCA 7380549926</b> A/N Muhammad Hanif Padma<br>
                        Metode Lain: <b>Qris</b>
                    </div>
                    
                    <div class='section-title'>Catatan Penting</div>
                    <ul class='notes-list'>
                        <li>Pembayaran yang telah dilakukan tidak dapat Dibatalkan / Dikembalikan.</li>
                        <li>Pastikan invoice sesuai dengan harga & jumlah peserta yang didaftarkan.</li>
                        <li>Pelunasan pembayaran Dilakukan H-7 Kegiatan.</li>
                        <li>Pembayaran Melalui Bank transfer.</li>
                        <li>Mohon lampirkan bukti pembayaran melalui Email/WhatsApp kami.</li>
                    </ul>
                </div>
                
                <!-- Right Details (Financial Status Block) -->
                <div class='right-block'>
                    <table class='summary-table'>
                        <tr><td>Subtotal</td><td style='text-align: right;'>Rp{subtotal:,}</td></tr>
                        <tr><td>Sudah DP</td><td style='text-align: right; color: #27ae60;'>Rp{dp_paid:,}</td></tr>
                        <tr style='font-weight: bold;'><td>Sisa Pembayaran</td><td style='text-align: right; color: #c0392b;'>Rp{remaining_payment:,}</td></tr>
                    </table>
                    
                    <div class='badge-container'>
                        <div class='section-title' style='margin-bottom: 2px;'>Payment Received</div>
                        <div style='font-size: 13pt; font-weight: bold; color: #27ae60;'>Rp{dp_paid:,}</div>
                        <div class='section-title' style='margin-top: 8px; margin-bottom: 2px;'>Sisa Pembayaran</div>
                        <div style='font-size: 13pt; font-weight: bold; color: #c0392b;'>Rp{remaining_payment:,}</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """.replace(",", ".")
        
        b64 = base64.b64encode(html_doc.encode('utf-8')).decode()
        st.success("🎉 Tampilan Invoice CV Fluir Travelindo Berhasil Diperbarui!")
        st.markdown(f'''
            <a href="data:text/html;base64,{b64}" download="Invoice_{inv_number}_{client_name.replace(' ', '_')}.html" style="text-decoration:none;">
                <button style="width:100%; padding:14px; background-color:#e67e22; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:11pt;">
                    📥 DOWNLOAD & SIMPAN SEBAGAI PDF PREMIUM
                </button>
            </a>
        ''', unsafe_allow_html=True)
