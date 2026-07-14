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
dp_paid = st.number_input("Sudah Di bayar / Masuk DP (Rp)", min_value=0, value=600000, step=50000)
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
        for item in st.session_state.invoice_items:
            item_total = item['qty'] * item['price']
            formatted_price = f"Rp {item['price']:,.0f}".replace(",", ".")
            formatted_total = f"Rp {item_total:,.0f}".replace(",", ".")
            
            rows_html += f"""
            <tr>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded;'>{item['desc']}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: center;'>{item['qty']}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>{formatted_price}</td>
                <td style='padding: 12px 10px; border-bottom: 1px solid #eaeded; text-align: right;'>{formatted_total}</td>
            </tr>
            """
            
        event_info_html = f"<b>Kegiatan:</b> {event_date_time}<br>" if event_date_time else ""
        status_badge_html = "<div style='border: 3px solid #27ae60; color: #27ae60; display: inline-block; padding: 4px 12px; font-size: 13pt; font-weight: bold; text-transform: uppercase; border-radius: 4px; margin-top: 15px; letter-spacing: 1px; transform: rotate(-3deg); opacity: 0.85;'>LUNAS / PAID</div>" if remaining_payment == 0 else ""
            
        # Menggunakan template string biasa tanpa f-string untuk menghindari bentrokan CSS {}
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8'>
            <title>Invoice #[INV_NUMBER]</title>
            <style>
                body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #2c3e50; padding: 25px; line-height: 1.4; font-size: 10pt; }
                .hdr-table { width: 100%; margin-bottom: 25px; border-bottom: 2px solid #e67e22; padding-bottom: 15px; }
                .company-details { font-size: 9pt; color: #7f8c8d; text-align: right; line-height: 1.3; }
                .info-table { width: 100%; margin-bottom: 25px; }
                .info-cell { vertical-align: top; width: 50%; }
                .section-title { font-size: 8pt; font-weight: bold; text-transform: uppercase; color: #95a5a6; margin-bottom: 5px; letter-spacing: 0.5px; }
                table.items { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                table.items th { background-color: #f8f9fa; color: #34495e; padding: 10px; font-size: 9pt; text-transform: uppercase; border-bottom: 2px solid #bdc3c7; }
                .split-container { width: 100%; overflow: hidden; margin-top: 15px; padding-bottom: 15px; border-bottom: 1px dashed #eaeded; }
                .right-block { float: right; width: 42%; text-align: right; }
                .summary-table { width: 100%; border-collapse: collapse; }
                .summary-table td { padding: 7px 10px; border-bottom: 1px solid #f2f4f4; font-size: 10pt; }
                .notes-list { padding-left: 15px; margin: 5px 0 0 0; font-size: 8.5pt; color: #626567; }
                .notes-list li { margin-bottom: 3px; }
                .bottom-layout-table { width: 100%; margin-top: 40px; border-collapse: collapse; page-break-inside: avoid; }
                .bottom-layout-cell { width: 50%; vertical-align: top; font-size: 10pt; }
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
                        NPWP: 91.570.415.9-404.000<br>
                        Hub: 081386000797 | fluiradventure@gmail.com
                    </td>
                </tr>
            </table>
            
            <table class='info-table'>
                <tr>
                    <td class='info-cell'>
                        <div class='section-title'>Dituju Kepada</div>
                        <b>[CLIENT_NAME]</b><br>
                        [CLIENT_PHONE]<br>
                        [CLIENT_ADDRESS]
                    </td>
                    <td class='info-cell' style='text-align: right;'>
                        <div class='section-title'>Data Dokumen</div>
                        <b>Invoice #</b> [INV_NUMBER]<br>
                        <b>Tanggal:</b> [INV_DATE]<br>
                        [EVENT_INFO]
                    </td>
                </tr>
            </table>

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
                    [ROWS_HTML]
                </tbody>
            </table>

            <div class='split-container'>
                <div class='right-block'>
                    <table class='summary-table'>
                        <tr><td style='text-align: left; color:#7f8c8d;'>Subtotal</td><td style='text-align: right;'>[SUBTOTAL]</td></tr>
                        <tr><td style='text-align: left; color:#7f8c8d;'>Sudah Dibayar</td><td style='text-align: right; color: #27ae60;'>[DP_PAID]</td></tr>
                        <tr style='font-weight: bold; background-color: #fcfcfc;'>
                            <td style='text-align: left; border-top: 1px solid #34495e;'>Sisa Pembayaran</td>
                            <td style='text-align: right; color: #c0392b; border-top: 1px solid #34495e;'>[REMAINING]</td>
                        </tr>
                    </table>
                    [STATUS_BADGE]
                </div>
            </div>

            <table class='bottom-layout-table'>
                <tr>
                    <td class='bottom-layout-cell' style='width: 60%; padding-right: 30px;'>
                        <div class='section-title'>Instruksi Pembayaran</div>
                        <div style='font-size: 9pt; color: #2c3e50; margin-bottom: 15px; line-height: 1.5;'>
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
                    </td>
                    
                    <td class='bottom-layout-cell' style='width: 40%; text-align: right; padding-right: 20px; vertical-align: top;'>
                        <p style='margin-top: 0; margin-bottom: 65px; font-weight: 500;'>Hormat kami,</p>
                        <b style='color: #2c3e50; font-size: 10.5pt;'>Hanif Padma</b>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # Proses replace string manual agar aman dari gangguan sintaksis CSS
        final_html = html_template.replace("[INV_NUMBER]", inv_number)\
                                  .replace("[CLIENT_NAME]", client_name)\
                                  .replace("[CLIENT_PHONE]", client_phone)\
                                  .replace("[CLIENT_ADDRESS]", client_address)\
                                  .replace("[INV_DATE]", inv_date.strftime('%B %d, %Y'))\
                                  .replace("[EVENT_INFO]", event_info_html)\
                                  .replace("[ROWS_HTML]", rows_html)\
                                  .replace("[SUBTOTAL]", subtotal_idr)\
                                  .replace("[DP_PAID]", dp_paid_idr)\
                                  .replace("[REMAINING]", remaining_payment_idr)\
                                  .replace("[STATUS_BADGE]", status_badge_html)
        
        st.session_state.html_buffer = final_html
        st.session_state.invoice_ready = True

if st.session_state.invoice_ready:
    b64 = base64.b64encode(st.session_state.html_buffer.encode('utf-8')).decode()
    st.success("🎉 Invoice Berhasil Dibuat!")
    st.markdown(f'''
        <a href="data:text/html;base64,{b64}" download="Invoice_{inv_number}_{client_name.replace(' ', '_')}.html" style="text-decoration:none;">
            <button style="width:100%; padding:14px; background-color:#e67e22; color:white; border:none; border-radius:6px; font-weight:bold; cursor:pointer; font-size:11pt;">
                📥 DOWNLOAD INVOICE #{inv_number}
            </button>
        </a>
    ''', unsafe_allow_html=True)
    
    if st.button("🔄 Segarkan Antrean Nomor Berikutnya"):
        st.session_state.invoice_ready = False
        st.rerun()
