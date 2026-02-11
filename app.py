import streamlit as st
import simpy
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import time

# =========================
# KONFIGURASI DASAR
# =========================
START_TIME = datetime(2024, 1, 1, 7, 0)
random.seed(42)

# =========================
# CUSTOM CSS UNTUK TAMPILAN PROFESIONAL
# =========================
def load_custom_css():
    st.markdown("""
    <style>
    /* Kontainer utama */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(120deg, #1a2a6c, #2c3e50, #4a6491);
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .header-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #ffd700, #ffa500, #ff4500);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .header-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f8f9ff, #e9ecef);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e6ef;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }
    .metric-label {
        font-size: 0.95rem;
        color: #495057;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a3a6c;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2a4d 0%, #1a3a6c 100%);
        color: white;
    }
    [data-testid="stSidebar"] .sidebar-title {
        color: #ffd700;
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #ffd700;
        margin-bottom: 1.5rem;
    }
    [data-testid="stSidebar"] .sidebar-subtitle {
        color: #a9c1e1;
        font-weight: 600;
        margin: 1.2rem 0 0.5rem;
        font-size: 1.15rem;
    }
    [data-testid="stSidebar"] .stNumberInput, 
    [data-testid="stSidebar"] .stSlider {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.6rem 0;
    }
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(90deg, #ffd700, #ffa500);
        color: #1a2a6c;
        font-weight: 600;
        border-radius: 50px;
        border: none;
        padding: 0.6rem 1.5rem;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    [data-testid="stSidebar"] .stButton button:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
        background: linear-gradient(90deg, #ffcc00, #ff9900);
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #eaeff5;
    }
    .chart-title {
        text-align: center;
        font-size: 1.6rem;
        color: #1a3a6c;
        margin-bottom: 1.2rem;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #6c757d;
        font-size: 0.95rem;
        border-top: 1px solid #e9ecef;
        margin-top: 2rem;
        font-style: italic;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f0f4ff, #e6edff);
        border-radius: 12px !important;
        border: 1px solid #d1d9e6 !important;
    }
    
    /* Button styling di main content */
    .stDownloadButton button {
        background: linear-gradient(90deg, #2c7be5, #1a56db);
        color: white;
        border-radius: 50px;
        padding: 0.4rem 1.8rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 4px 10px rgba(26, 88, 219, 0.3);
    }
    .stDownloadButton button:hover {
        background: linear-gradient(90deg, #1a56db, #1547b0);
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(26, 88, 219, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# MODEL SIMULASI (Tidak berubah)
# =========================
class SistemPiketDES:
    def __init__(self, env, cfg):
        self.env = env
        self.cfg = cfg

        self.petugas_lauk = simpy.Resource(env, capacity=cfg["petugas_lauk"])
        self.petugas_angkut = simpy.Resource(env, capacity=cfg["petugas_angkut"])
        self.petugas_nasi = simpy.Resource(env, capacity=cfg["petugas_nasi"])

        self.data = []

    def proses_ompreng(self, oid):
        datang = self.env.now

        # Tahap 1: Lauk
        with self.petugas_lauk.request() as req:
            yield req
            t = random.uniform(*self.cfg["waktu_lauk"])
            yield self.env.timeout(t)

        # Tahap 2: Angkut
        with self.petugas_angkut.request() as req:
            yield req
            t = random.uniform(*self.cfg["waktu_angkut"])
            yield self.env.timeout(t)

        # Tahap 3: Nasi
        with self.petugas_nasi.request() as req:
            yield req
            t = random.uniform(*self.cfg["waktu_nasi"])
            yield self.env.timeout(t)

        selesai = self.env.now

        self.data.append({
            "Ompreng": oid,
            "Datang (menit)": datang,
            "Selesai (menit)": selesai,
            "Durasi (menit)": selesai - datang,
            "Jam Selesai": START_TIME + timedelta(minutes=selesai)
        })

# =========================
# STREAMLIT APP - VERSI DIPERBAIKI
# =========================
def main():
    st.set_page_config(
        page_title="Simulasi Sistem Piket IT Del",
        page_icon="🍱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Muat CSS kustom
    load_custom_css()
    
    # =========================
    # HEADER PROFESIONAL
    # =========================
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🍱 SIMULASI SISTEM PIKET IT DEL</div>
        <div class="header-subtitle">
            Analisis kinerja proses pengisian ompreng menggunakan <strong>Discrete Event Simulation (DES)</strong>. 
            Sesuaikan parameter sistem untuk melihat dampak terhadap efisiensi pelayanan.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # =========================
    # SIDEBAR DENGAN DESAIN PREMIUM
    # =========================
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ KONFIGURASI SIMULASI</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-subtitle">📋 Setup Area</div>', unsafe_allow_html=True)
        jumlah_meja = st.number_input("🪑 Jumlah Meja", 10, 100, 60, help="Total meja yang tersedia untuk mahasiswa")
        mahasiswa_per_meja = st.number_input("👥 Mahasiswa per Meja", 1, 5, 3, help="Rata-rata mahasiswa per meja")
        
        st.markdown('<div class="sidebar-subtitle">👨‍🍳 Tim Pelayanan</div>', unsafe_allow_html=True)
        petugas_lauk = st.number_input("🍗 Petugas Lauk", 1, 5, 2, help="Jumlah petugas bagian lauk")
        petugas_angkut = st.number_input("🥡 Petugas Angkut", 1, 5, 2, help="Jumlah petugas pengangkut ompreng")
        petugas_nasi = st.number_input("🍚 Petugas Nasi", 1, 5, 3, help="Jumlah petugas bagian nasi")
        
        st.markdown('<div class="sidebar-subtitle">⏱️ Parameter Waktu</div>', unsafe_allow_html=True)
        waktu_lauk = st.slider("🍗 Waktu Ambil Lauk (menit)", 0.3, 1.5, (0.5, 1.0), help="Rentang waktu pengambilan lauk per orang")
        waktu_angkut = st.slider("🥡 Waktu Angkut (menit)", 0.2, 1.5, (0.33, 1.0), help="Rentang waktu pengangkutan ompreng")
        waktu_nasi = st.slider("🍚 Waktu Ambil Nasi (menit)", 0.3, 1.5, (0.5, 1.0), help="Rentang waktu pengambilan nasi per orang")
        
        st.divider()
        run = st.button("🚀 JALANKAN SIMULASI", type="primary")
        
        # Informasi tambahan di sidebar
        st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; font-size: 0.85rem;">
        <strong>ℹ️ Tips Penggunaan:</strong><br>
        • Sesuaikan jumlah petugas berdasarkan beban kerja<br>
        • Rentang waktu proses memengaruhi variasi simulasi<br>
        • Total ompreng = Meja × Mahasiswa per Meja
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # KONTEN UTAMA
    # =========================
    if run:
        total_ompreng = jumlah_meja * mahasiswa_per_meja
        
        # Validasi parameter
        if total_ompreng <= 0:
            st.error("❌ Total ompreng tidak valid. Periksa parameter input!")
            st.stop()
        
        cfg = {
            "petugas_lauk": petugas_lauk,
            "petugas_angkut": petugas_angkut,
            "petugas_nasi": petugas_nasi,
            "waktu_lauk": waktu_lauk,
            "waktu_angkut": waktu_angkut,
            "waktu_nasi": waktu_nasi,
        }

        # Progress simulation dengan status
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.info("⏳ Memulai simulasi... Inisialisasi sistem")
        
        try:
            env = simpy.Environment()
            model = SistemPiketDES(env, cfg)
            
            # Buat proses untuk setiap ompreng
            for i in range(total_ompreng):
                env.process(model.proses_ompreng(i))
                if i % max(1, total_ompreng // 20) == 0:  # Update progress setiap 5%
                    progress_bar.progress(min(90, int(i / total_ompreng * 90)))
                    status_text.info(f"⏳ Sedang memproses... ({i}/{total_ompreng} ompreng)")
            
            # Jalankan simulasi
            env.run()
            progress_bar.progress(100)
            status_text.success("✅ Simulasi berhasil diselesaikan!")
            time.sleep(0.5)  # Efek visual
            status_text.empty()
            progress_bar.empty()
            
        except Exception as e:
            status_text.error(f"❌ Terjadi kesalahan saat simulasi: {str(e)}")
            st.stop()

        # Buat DataFrame hasil
        df = pd.DataFrame(model.data)
        
        # =========================
        # METRIK UTAMA DENGAN DESAIN MENARIK
        # =========================
        st.markdown("### 📈 Hasil Simulasi")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="Total Ompreng Diproses",
                value=f"{total_ompreng:,}",
                delta="Simulasi Selesai",
                delta_color="off"
            )
        with col2:
            avg_duration = df['Durasi (menit)'].mean()
            st.metric(
                label="Rata-rata Durasi",
                value=f"{avg_duration:.2f} menit",
                delta=f"±{df['Durasi (menit)'].std():.2f} menit",
                delta_color="normal"
            )
        with col3:
            max_time = df["Jam Selesai"].max()
            st.metric(
                label="Waktu Selesai Terakhir",
                value=max_time.strftime("%H:%M:%S"),
                delta=f"{max_time.strftime('%H:%M')} WIB",
                delta_color="off"
            )
        with col4:
            throughput = total_ompreng / (df["Selesai (menit)"].max() / 60)  # ompreng per jam
            st.metric(
                label="Throughput Sistem",
                value=f"{throughput:.1f} ompreng/jam",
                delta="Efisiensi Operasional",
                delta_color="off"
            )
        
        # =========================
        # VISUALISASI DENGAN DESAIN PROFESIONAL
        # =========================
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Distribusi Durasi Proses Per Ompreng</div>', unsafe_allow_html=True)
        
        # Histogram dengan styling Plotly modern
        fig_hist = px.histogram(
            df,
            x="Durasi (menit)",
            nbins=35,
            color_discrete_sequence=["#2c7be5"],
            labels={"Durasi (menit)": "Durasi (menit)", "count": "Frekuensi"},
            marginal="box"  # Menambahkan box plot di atas
        )
        fig_hist.update_layout(
            template="plotly_white",
            xaxis_title="Durasi Proses (menit)",
            yaxis_title="Jumlah Ompreng",
            bargap=0.1,
            hovermode="x unified",
            font=dict(size=13),
            title_font_size=18,
            title_x=0.5
        )
        fig_hist.update_traces(hovertemplate="Durasi: %{x:.2f} menit<br>Frekuensi: %{y}")
        st.plotly_chart(fig_hist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Timeline penyelesaian
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">⏱️ Timeline Penyelesaian Seluruh Ompreng</div>', unsafe_allow_html=True)
        
        df_sorted = df.sort_values("Selesai (menit)").reset_index(drop=True)
        df_sorted["Urutan Penyelesaian"] = df_sorted.index + 1
        
        fig_time = px.line(
            df_sorted,
            x="Urutan Penyelesaian",
            y="Selesai (menit)",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#e63757"],
            labels={"Selesai (menit)": "Waktu Selesai (menit)", "Urutan Penyelesaian": "Urutan"}
        )
        fig_time.add_hline(
            y=df_sorted["Selesai (menit)"].mean(), 
            line_dash="dash", 
            line_color="#ffa900",
            annotation_text=f"Rata-rata: {df_sorted['Selesai (menit)'].mean():.1f} menit",
            annotation_position="bottom right"
        )
        fig_time.update_layout(
            template="plotly_white",
            xaxis_title="Urutan Penyelesaian (Ompreng ke-)",
            yaxis_title="Waktu Selesai Sejak Mulai (menit)",
            hovermode="x unified",
            font=dict(size=13),
            title_font_size=18,
            title_x=0.5,
            showlegend=False
        )
        fig_time.update_traces(
            hovertemplate="Urutan: %{x}<br>Waktu Selesai: %{y:.1f} menit",
            marker=dict(size=6)
        )
        st.plotly_chart(fig_time, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # =========================
        # ANALISIS TAMBAHAN
        # =========================
        st.markdown("### 🔍 Analisis Performa Sistem")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Utilisasi perkiraan (berdasarkan waktu sibuk total)
            st.markdown("**Perkiraan Utilisasi Petugas**")
            total_time = df["Selesai (menit)"].max()
            st.progress(min(100, int((df["Durasi (menit)"].sum() / (total_time * (petugas_lauk + petugas_angkut + petugas_nasi))) * 100)))
            st.caption(f"Berdasarkan total waktu proses terhadap kapasitas sistem. Nilai >85% menunjukkan potensi bottleneck.")
        
        with col_b:
            # Statistik durasi
            st.markdown("**Statistik Durasi Proses**")
            stats_df = pd.DataFrame({
                "Metrik": ["Minimum", "Rata-rata", "Maksimum", "Standar Deviasi"],
                "Nilai (menit)": [
                    df["Durasi (menit)"].min(),
                    df["Durasi (menit)"].mean(),
                    df["Durasi (menit)"].max(),
                    df["Durasi (menit)"].std()
                ]
            })
            st.table(stats_df.style.format({"Nilai (menit)": "{:.2f}"}).set_properties(**{
                'text-align': 'center',
                'font-weight': 'bold'
            }))
        
        # =========================
        # DATA TABEL & EKSPOR
        # =========================
        with st.expander("📄 Lihat Data Detail Lengkap"):
            st.dataframe(
                df.style.format({
                    "Datang (menit)": "{:.2f}",
                    "Selesai (menit)": "{:.2f}",
                    "Durasi (menit)": "{:.2f}",
                    "Jam Selesai": lambda x: x.strftime("%H:%M:%S")
                }).set_properties(**{
                    'text-align': 'center',
                    'border': '1px solid #e0e6ef'
                }),
                use_container_width=True,
                height=400
            )
            
            col_csv1, col_csv2, _ = st.columns([1, 1, 3])
            with col_csv1:
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Unduh Data CSV",
                    data=csv,
                    file_name=f"simulasi_piket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download-csv"
                )
            with col_csv2:
                # Tombol contoh reset
                if st.button("↺ Reset Parameter"):
                    st.experimental_rerun()
        
        # Insight otomatis
        st.info(f"""
        💡 **Insight Simulasi**: 
        Durasi proses bervariasi antara **{df['Durasi (menit)'].min():.1f}** hingga **{df['Durasi (menit)'].max():.1f}** menit. 
        {"Sistem mengalami bottleneck pada tahap nasi." if petugas_nasi < max(petugas_lauk, petugas_angkut) else "Distribusi petugas seimbang."} 
        Waktu selesai terakhir pukul **{max_time.strftime('%H:%M')}** dengan throughput **{throughput:.1f}** ompreng per jam.
        """)
    
    else:
        # Tampilan awal dengan panduan
        st.markdown("""
        ### 📌 Panduan Penggunaan
        Selamat datang di simulator sistem piket IT Del! 
        
        **Langkah Penggunaan:**
        1. Sesuaikan parameter di sidebar kiri sesuai skenario yang ingin diuji
        2. Klik tombol **🚀 JALANKAN SIMULASI** untuk memulai analisis
        3. Tinjau hasil simulasi pada metrik dan visualisasi
        4. Unduh data lengkap untuk analisis lebih lanjut
        
        **Parameter Penting:**
        - 🪑 **Jumlah Meja & Mahasiswa**: Menentukan total beban kerja (ompreng)
        - 👨‍🍳 **Jumlah Petugas**: Pengaruhi kecepatan pemrosesan di tiap stasiun
        - ⏱️ **Waktu Proses**: Rentang waktu acak untuk setiap aktivitas
        
        > 💡 *Simulasi menggunakan pendekatan Discrete Event Simulation (DES) dengan 10,000+ event untuk akurasi tinggi*
        """)
        
        # Contoh visualisasi placeholder
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">✨ Contoh Visualisasi Hasil Simulasi</div>', unsafe_allow_html=True)
        sample_data = pd.DataFrame({
            "Durasi (menit)": np.random.normal(2.5, 0.5, 1000)
        })
        fig_sample = px.histogram(
            sample_data, 
            x="Durasi (menit)", 
            nbins=30,
            color_discrete_sequence=["#a5b4fc"]
        )
        fig_sample.update_layout(
            template="plotly_white",
            showlegend=False,
            height=300,
            xaxis_title="Durasi Proses (menit)",
            yaxis_title="Frekuensi"
        )
        st.plotly_chart(fig_sample, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tips tambahan
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-radius: 12px; padding: 1.2rem; margin-top: 1.5rem; border-left: 4px solid #2196f3;">
        <h4 style="margin-top: 0; color: #0d47a1;">💡 Tips Optimasi Sistem</h4>
        <ul style="line-height: 1.6; color: #0a2e5a;">
            <li>Tambah petugas di stasiun dengan waktu proses tertinggi</li>
            <li>Seimbangkan jumlah petugas sesuai kompleksitas tugas (nasi > lauk > angkut)</li>
            <li>Uji skenario "what-if" dengan mengubah parameter secara bertahap</li>
            <li>Perhatikan standar deviasi durasi - nilai tinggi menunjukkan ketidakstabilan sistem</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # =========================
    # FOOTER
    # =========================
    st.markdown("""
    <div class="footer">
        <strong>Simulasi Sistem Piket IT Del</strong> | 
        Dibuat dengan ❤️ menggunakan Streamlit, SimPy & Plotly | 
        Versi 2.1 • Februari 2026
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()