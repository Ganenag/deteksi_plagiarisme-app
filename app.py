import streamlit as st
import pandas as pd
import algoritma as algo 
import PyPDF2
import time

# --- FUNGSI BACA FILE ---
def read_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        else:
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return ""

# --- CONFIG PAGE ---
st.set_page_config(page_title="Plagiarism Checker", layout="wide")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2666/2666505.png", width=50)
    st.title("Plagiarism Tool")
    st.info("Kelompok 2 - Deteksi Plagiarisme\n\nAnalisis Perbandingan KMP vs Boyer-Moore")

# --- MAIN LAYOUT ---
st.header("🔍 Deteksi Plagiarisme & Analisis Algoritma")
st.markdown("Upload dokumen untuk melihat persentase kemiripan dan **perbandingan kecepatan** algoritma.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 Dokumen Suspect")
        file_suspect = st.file_uploader("Upload file (.txt/.pdf)", type=["txt", "pdf"], key="suspect")
    with col2:
        st.subheader("📚 Dokumen Asli")
        file_original = st.file_uploader("Upload file (.txt/.pdf)", type=["txt", "pdf"], key="original")

st.divider()

# Tombol Eksekusi
if st.button("Mulai Analisis Komparasi 🚀", type="primary", use_container_width=True):
    if file_suspect and file_original:
        
        # 1. Baca File
        with st.spinner("Mengekstrak teks..."):
            text_suspect = read_uploaded_file(file_suspect)
            text_original = read_uploaded_file(file_original)
        
        if not text_suspect or not text_original:
            st.error("Gagal membaca file. Pastikan file berisi teks.")
        else:
            # 2. JALANKAN KEDUA ALGORITMA
            with st.spinner("Sedang menjalankan KMP dan Boyer-Moore secara bersamaan..."):
                # Run KMP
                sim_kmp, time_kmp, details_kmp = algo.calculate_similarity(text_suspect, text_original, "KMP")
                # Run Boyer-Moore
                sim_bm, time_bm, details_bm = algo.calculate_similarity(text_suspect, text_original, "Boyer-Moore")
            
            st.success("Analisis Selesai!")
            
            # --- TAMPILAN 1: HASIL DETEKSI  ---
            st.subheader("📊 Hasil Deteksi")
            
            # Cek apakah hasil akurasi sama persis
            if sim_kmp == sim_bm:
                accuracy_label = "Hasil Identik (KMP & BM)"
            else:
                accuracy_label = "Terdapat Perbedaan Hasil"

            m1, m2, m3 = st.columns(3)
            
            m1.metric("Tingkat Kemiripan", f"{sim_kmp:.2f}%", help=accuracy_label)
            
            # Status Plagiarisme
            status_text = "Aman"
            if sim_kmp > 70: status_text = "Plagiat Berat"
            elif sim_kmp > 30: status_text = "Plagiat Ringan"
            
            m2.metric("Status", status_text)
            m3.metric("Total Kalimat Terdeteksi", f"{len(details_kmp)} Kalimat")

            # --- TAMPILAN 2: KOMPARASI KECEPATAN ---
            st.subheader("⚡ Perbandingan Kecepatan Algoritma")
            st.markdown("Grafik ini membuktikan efisiensi waktu eksekusi (Running Time) antara KMP dan Boyer-Moore.")
            
            c_chart, c_data = st.columns([2, 1])
            
            with c_chart:
                chart_data = pd.DataFrame({
                    "Algoritma": ["Knuth-Morris-Pratt (KMP)", "Boyer-Moore"],
                    "Waktu (Detik)": [time_kmp, time_bm]
                })
                st.bar_chart(chart_data, x="Algoritma", y="Waktu (Detik)", color="Algoritma")
            
            with c_data:
                st.info(f"**KMP Time:** {time_kmp:.6f} detik")
                st.info(f"**Boyer-Moore Time:** {time_bm:.6f} detik")
                
                diff = abs(time_kmp - time_bm)
                winner = "Boyer-Moore" if time_bm < time_kmp else "KMP"
                
                # Highlight pemenang
                if winner == "Boyer-Moore":
                    st.success(f"🏆 **{winner}** lebih cepat {diff:.6f} detik.")
                else:
                    st.warning(f"🏆 **{winner}** lebih cepat {diff:.6f} detik.")

            # --- TAMPILAN 3: TABEL DETAIL KALIMAT ---
            st.divider()
            st.subheader("📝 Detail Kalimat yang Terdeteksi Sama")
            
            if details_kmp:
                df_details = pd.DataFrame(details_kmp)
                st.dataframe(
                    df_details[["Kalimat Terdeteksi", "Status"]], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.caption("Tidak ada kalimat yang terindikasi plagiat.")
                
    else:
        st.warning("Mohon upload kedua file terlebih dahulu.")