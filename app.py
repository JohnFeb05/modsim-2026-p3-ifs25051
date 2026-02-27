import streamlit as st
import simpy
import random
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ============================================
# 🎨 CUSTOM CSS STYLING - DARK THEME
# ============================================
st.markdown("""
<style>
    /* Main Background - Dark Gradient */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        min-height: 100vh;
    }
    
    /* Sidebar Background */
    .stSidebar {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 2px solid #e94560;
    }
    
    /* Card Style - Dark */
    .metric-card {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 8px 16px rgba(233, 69, 96, 0.2);
        margin: 10px 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(233, 69, 96, 0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(233, 69, 96, 0.4);
        border-color: #e94560;
    }
    
    /* Header Style - Neon Effect */
    .main-header {
        background: linear-gradient(90deg, #e94560, #0f3460, #533483);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 0 0 20px rgba(233, 69, 96, 0.5);
    }
    
    /* Subheader */
    .sub-header {
        color: #a0a0a0;
        font-size: 1.1em;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* Button Style - Dark Theme */
    .stButton > button {
        background: linear-gradient(90deg, #e94560, #533483);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 15px 30px;
        font-size: 1.1em;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(233, 69, 96, 0.6);
        background: linear-gradient(90deg, #ff6b6b, #764ba2);
    }
    
    /* Info Box - Dark */
    .info-box {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%);
        border-left: 5px solid #0f3460;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #e0e0e0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    /* Warning Box - Dark */
    .warning-box {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.3) 0%, rgba(26, 26, 46, 0.9) 100%);
        border-left: 5px solid #e94560;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #ff6b6b;
        box-shadow: 0 4px 8px rgba(233, 69, 96, 0.2);
    }
    
    /* Success Box - Dark */
    .success-box {
        background: linear-gradient(135deg, rgba(0, 200, 83, 0.3) 0%, rgba(26, 26, 46, 0.9) 100%);
        border-left: 5px solid #00c853;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        color: #69f0ae;
        box-shadow: 0 4px 8px rgba(0, 200, 83, 0.2);
    }
    
    /* Metric Display - Dark */
    .big-metric {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(90deg, #e94560, #0f3460);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #a0a0a0;
        text-align: center;
        margin-top: 8px;
    }
    
    /* Section Header */
    .section-header {
        color: #e94560;
        font-size: 1.3em;
        font-weight: bold;
        margin: 20px 0 10px 0;
        border-bottom: 2px solid rgba(233, 69, 96, 0.3);
        padding-bottom: 5px;
    }
    
    /* Process Step Card */
    .process-card {
        background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid rgba(233, 69, 96, 0.3);
        text-align: center;
    }
    
    .process-card h4 {
        color: #e94560;
        margin: 0 0 10px 0;
        font-size: 1.2em;
    }
    
    .process-card .icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    
    .process-card p {
        color: #a0a0a0;
        margin: 5px 0;
        font-size: 0.9em;
    }
    
    .process-card .time-info {
        color: #00c853;
        font-weight: bold;
        font-size: 0.85em;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #666;
        padding: 20px;
        border-top: 1px solid rgba(233, 69, 96, 0.2);
        margin-top: 40px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ⚙ KONFIGURASI - STUDI KASUS SISTEM PIKET
# ============================================
@dataclass
class ConfigPiket:
    """
    Konfigurasi untuk Sistem Piket Kantin IT Del
    Sesuai Modul Praktikum 3 - Bagian 2.1 Studi Kasus
    """
    
    # ========== Parameter Dasar ==========
    NUM_MEJA: int = 60                    # Jumlah meja (default: 60)
    MAHASISWA_PER_MEJA: int = 3           # Mahasiswa/ompreng per meja (default: 3)
    TOTAL_PETUGAS: int = 7                # Total petugas piket (default: 7)
    
    # ========== Alokasi Petugas per Tahap ==========
    # Harus total = 7 petugas
    PETUGAS_ISI_LAUK: int = 3             # Tahap 1: Isi lauk ke ompreng
    PETUGAS_ANGKUT: int = 2               # Tahap 2: Angkut ompreng ke meja
    PETUGAS_TAMBAH_NASI: int = 2          # Tahap 3: Tambah nasi ke ompreng
    
    # ========== Waktu Pelayanan per Tahap (MENIT) ==========
    # Tahap 1: Isi lauk ke ompreng (30-60 detik = 0.5-1.0 menit)
    MIN_ISI_LAUK: float = 0.5
    MAX_ISI_LAUK: float = 1.0
    
    # Tahap 2: Angkut ompreng ke meja, 4-7 ompreng sekaligus (20-60 detik = 0.33-1.0 menit)
    MIN_ANGKUT: float = 0.33
    MAX_ANGKUT: float = 1.0
    
    # Tahap 3: Tambah nasi ke ompreng (30-60 detik = 0.5-1.0 menit)
    MIN_TAMBAH_NASI: float = 0.5
    MAX_TAMBAH_NASI: float = 1.0
    
    # ========== Batch Angkut Ompreng ==========
    MIN_BATCH_ANGKUT: int = 4             # Minimal 4 ompreng per angkut
    MAX_BATCH_ANGKUT: int = 7             # Maksimal 7 ompreng per angkut
    
    # ========== Waktu Mulai ==========
    START_HOUR: int = 7                   # Mulai pukul 07:00
    START_MINUTE: int = 0
    
    # ========== Random Seed ==========
    RANDOM_SEED: int = 42

# ============================================
# 🏗 MODEL SIMULASI - SISTEM PIKET DES
# ============================================
class SistemPiketKantinDES:
    """
    Model Discrete Event Simulation untuk Sistem Piket Kantin IT Del
    3 Tahap Proses: Isi Lauk → Angkut Ompreng → Tambah Nasi
    """
    
    def __init__(self, config: ConfigPiket):
        self.config = config
        self.env = simpy.Environment()
        
        # Resources: Petugas per tahap
        self.petugas_isi_lauk = simpy.Resource(self.env, capacity=config.PETUGAS_ISI_LAUK)
        self.petugas_angkut = simpy.Resource(self.env, capacity=config.PETUGAS_ANGKUT)
        self.petugas_tambah_nasi = simpy.Resource(self.env, capacity=config.PETUGAS_TAMBAH_NASI)
        
        # Buffer/Queue antar tahap
        self.buffer_setelah_lauk = simpy.Store(self.env)
        self.buffer_setelah_angkut = simpy.Store(self.env)
        
        # Statistik
        self.statistics = {
            'meja_data': [],
            'queue_lengths': {'lauk': [], 'angkut': [], 'nasi': []},
            'waiting_times': [],
            'service_times': {'lauk': [], 'angkut': [], 'nasi': []},
            'utilization': {'lauk': [], 'angkut': [], 'nasi': []}
        }
        
        # Waktu mulai simulasi
        self.start_time = datetime(2024, 1, 1, config.START_HOUR, config.START_MINUTE)
        
        # Set random seed
        random.seed(config.RANDOM_SEED)
        np.random.seed(config.RANDOM_SEED)
    
    def waktu_ke_jam(self, waktu_simulasi: float) -> datetime:
        """Konversi waktu simulasi (menit) ke datetime"""
        return self.start_time + timedelta(minutes=waktu_simulasi)
    
    def generate_service_time(self, min_time: float, max_time: float) -> float:
        """Generate waktu layanan dengan distribusi uniform"""
        return random.uniform(min_time, max_time)
    
    def proses_meja(self, meja_id: int):
        """Proses untuk satu meja dari awal hingga selesai"""
        waktu_mulai = self.env.now
        total_ompreng = self.config.MAHASISWA_PER_MEJA
        
        # ═══════════════════════════════════════════════════════════
        # TAHAP 1: ISI LAUK KE OMPRENG
        # Deskripsi: Petugas memasukkan lauk ke dalam ompreng
        # Waktu: 30-60 detik per ompreng
        # ═══════════════════════════════════════════════════════════
        for i in range(total_ompreng):
            with self.petugas_isi_lauk.request() as request:
                yield request
                
                self.statistics['utilization']['lauk'].append({
                    'time': self.env.now,
                    'in_use': self.petugas_isi_lauk.count
                })
                
                service_time = self.generate_service_time(
                    self.config.MIN_ISI_LAUK, 
                    self.config.MAX_ISI_LAUK
                )
                yield self.env.timeout(service_time)
                
                self.statistics['service_times']['lauk'].append(service_time)
            
            yield self.buffer_setelah_lauk.put({'meja_id': meja_id, 'ompreng_id': i})
        
        self.statistics['queue_lengths']['lauk'].append({
            'time': self.env.now,
            'queue_length': len(self.buffer_setelah_lauk.items)
        })
        
        # ═══════════════════════════════════════════════════════════
        # TAHAP 2: ANGKUT OMPRENG KE MEJA (BATCH PROCESSING)
        # Deskripsi: Petugas membawa 4-7 ompreng sekaligus ke meja
        # Waktu: 20-60 detik per batch
        # ═══════════════════════════════════════════════════════════
        ompreng_siap = []
        
        while len(ompreng_siap) < total_ompreng:
            item = yield self.buffer_setelah_lauk.get()
            ompreng_siap.append(item)
            
            self.statistics['queue_lengths']['angkut'].append({
                'time': self.env.now,
                'queue_length': len(self.buffer_setelah_lauk.items)
            })
        
        with self.petugas_angkut.request() as request:
            yield request
            
            self.statistics['utilization']['angkut'].append({
                'time': self.env.now,
                'in_use': self.petugas_angkut.count
            })
            
            service_time = self.generate_service_time(
                self.config.MIN_ANGKUT, 
                self.config.MAX_ANGKUT
            )
            yield self.env.timeout(service_time)
            
            self.statistics['service_times']['angkut'].append(service_time)
        
        for item in ompreng_siap:
            yield self.buffer_setelah_angkut.put(item)
        
        # ═══════════════════════════════════════════════════════════
        # TAHAP 3: TAMBAH NASI KE OMPRENG
        # Deskripsi: Petugas menambahkan nasi ke dalam ompreng
        # Waktu: 30-60 detik per ompreng
        # ═══════════════════════════════════════════════════════════
        for i in range(total_ompreng):
            item = yield self.buffer_setelah_angkut.get()
            
            with self.petugas_tambah_nasi.request() as request:
                yield request
                
                self.statistics['utilization']['nasi'].append({
                    'time': self.env.now,
                    'in_use': self.petugas_tambah_nasi.count
                })
                
                service_time = self.generate_service_time(
                    self.config.MIN_TAMBAH_NASI,
                    self.config.MAX_TAMBAH_NASI
                )
                yield self.env.timeout(service_time)
                
                self.statistics['service_times']['nasi'].append(service_time)
            
            self.statistics['queue_lengths']['nasi'].append({
                'time': self.env.now,
                'queue_length': len(self.buffer_setelah_angkut.items)
            })
        
        # ═══════════════════════════════════════════════════════════
        # SELESAI
        # ═══════════════════════════════════════════════════════════
        waktu_selesai = self.env.now
        total_waktu = waktu_selesai - waktu_mulai
        
        self.statistics['meja_data'].append({
            'meja_id': meja_id,
            'waktu_mulai': waktu_mulai,
            'waktu_selesai': waktu_selesai,
            'total_waktu_proses': total_waktu,
            'jam_mulai': self.waktu_ke_jam(waktu_mulai),
            'jam_selesai': self.waktu_ke_jam(waktu_selesai),
            'jumlah_ompreng': total_ompreng
        })
        
        self.statistics['waiting_times'].append(total_waktu)
    
    def proses_semua_meja(self):
        """Generate proses untuk semua meja"""
        processes = []
        for i in range(self.config.NUM_MEJA):
            proc = self.env.process(self.proses_meja(i))
            processes.append(proc)
        yield simpy.AllOf(self.env, processes)
    
    def run_simulation(self):
        """Jalankan simulasi"""
        self.env.process(self.proses_semua_meja())
        self.env.run()
        return self.analyze_results()
    
    def analyze_results(self):
        """Analisis hasil simulasi"""
        if not self.statistics['meja_data']:
            return None, None
        
        df = pd.DataFrame(self.statistics['meja_data'])
        
        results = {
            'total_meja': len(df),
            'total_ompreng': df['jumlah_ompreng'].sum(),
            'waktu_selesai_terakhir': df['waktu_selesai'].max(),
            'jam_selesai_terakhir': self.waktu_ke_jam(df['waktu_selesai'].max()),
            'durasi_total_menit': df['waktu_selesai'].max(),
            
            'avg_waktu_proses': df['total_waktu_proses'].mean(),
            'max_waktu_proses': df['total_waktu_proses'].max(),
            'min_waktu_proses': df['total_waktu_proses'].min(),
            'std_waktu_proses': df['total_waktu_proses'].std(),
            
            'avg_service_lauk': np.mean(self.statistics['service_times']['lauk']) if self.statistics['service_times']['lauk'] else 0,
            'avg_service_angkut': np.mean(self.statistics['service_times']['angkut']) if self.statistics['service_times']['angkut'] else 0,
            'avg_service_nasi': np.mean(self.statistics['service_times']['nasi']) if self.statistics['service_times']['nasi'] else 0,
            
            'utilization_lauk': self._calculate_utilization('lauk', df),
            'utilization_angkut': self._calculate_utilization('angkut', df),
            'utilization_nasi': self._calculate_utilization('nasi', df),
            
            'distribusi_jam': self.calculate_hourly_distribution(df)
        }
        
        return results, df
    
    def _calculate_utilization(self, stage: str, df: pd.DataFrame) -> float:
        """Hitung utilization untuk satu tahap"""
        if not self.statistics['utilization'][stage]:
            return 0.0
        
        total_simulation_time = df['waktu_selesai'].max()
        if stage == 'lauk':
            capacity = self.config.PETUGAS_ISI_LAUK
        elif stage == 'angkut':
            capacity = self.config.PETUGAS_ANGKUT
        else:
            capacity = self.config.PETUGAS_TAMBAH_NASI
        
        total_service_time = sum(self.statistics['service_times'][stage])
        utilization = (total_service_time / (total_simulation_time * capacity)) * 100
        return min(utilization, 100)
    
    def calculate_hourly_distribution(self, df: pd.DataFrame) -> Dict:
        """Hitung distribusi meja selesai per jam"""
        df['jam'] = df['jam_selesai'].dt.hour
        hourly = df.groupby('jam').size().reset_index(name='jumlah')
        return dict(zip(hourly['jam'], hourly['jumlah']))

# ============================================
# 📊 FUNGSI VISUALISASI PLOTLY - DARK THEME
# ============================================
def create_process_time_distribution(df):
    """Histogram distribusi waktu proses per meja"""
    fig = px.histogram(
        df, x='total_waktu_proses', nbins=30,
        title='📊 Distribusi Waktu Proses per Meja',
        labels={'total_waktu_proses': 'Waktu Proses (menit)', 'count': 'Jumlah Meja'},
        color_discrete_sequence=['#e94560'],
        opacity=0.8
    )
    
    avg_val = df['total_waktu_proses'].mean()
    fig.add_vline(x=avg_val, line_dash="dash", line_color="#00c853",
                  annotation_text=f"Rata-rata: {avg_val:.2f} menit",
                  annotation_position="top right")
    
    fig.update_layout(
        xaxis_title="Waktu Proses (menit)",
        yaxis_title="Frekuensi",
        showlegend=False,
        hovermode="x unified",
        plot_bgcolor='rgba(26, 26, 46, 0.9)',
        paper_bgcolor='rgba(26, 26, 46, 0.9)',
        font_color='#e0e0e0',
        xaxis_gridcolor='rgba(233, 69, 96, 0.2)',
        yaxis_gridcolor='rgba(233, 69, 96, 0.2)'
    )
    
    return fig

def create_timeline_chart(df):
    """Timeline mulai dan selesai per meja"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['waktu_mulai'], y=df['meja_id'], mode='markers',
        name='Mulai',
        marker=dict(size=5, color='#0f3460', opacity=0.7),
        hovertemplate='Meja %{y}<br>Mulai: %{x:.1f} menit<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['waktu_selesai'], y=df['meja_id'], mode='markers',
        name='Selesai',
        marker=dict(size=5, color='#00c853', opacity=0.7),
        hovertemplate='Meja %{y}<br>Selesai: %{x:.1f} menit<extra></extra>'
    ))
    
    fig.update_layout(
        title='📈 Timeline Mulai dan Selesai per Meja',
        xaxis_title="Waktu Simulasi (menit)",
        yaxis_title="ID Meja",
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(26, 26, 46, 0.9)',
        paper_bgcolor='rgba(26, 26, 46, 0.9)',
        font_color='#e0e0e0',
        xaxis_gridcolor='rgba(233, 69, 96, 0.2)',
        yaxis_gridcolor='rgba(233, 69, 96, 0.2)'
    )
    
    return fig

def create_hourly_distribution_chart(results):
    """Chart distribusi per jam"""
    hours = list(results['distribusi_jam'].keys())
    counts = list(results['distribusi_jam'].values())
    
    fig = px.bar(
        x=hours, y=counts,
        title='🕐 Distribusi Meja Selesai per Jam',
        labels={'x': 'Jam', 'y': 'Jumlah Meja'},
        color=counts,
        color_continuous_scale='Plasma'
    )
    
    fig.update_layout(
        xaxis_title="Jam",
        yaxis_title="Jumlah Meja",
        coloraxis_showscale=False,
        plot_bgcolor='rgba(26, 26, 46, 0.9)',
        paper_bgcolor='rgba(26, 26, 46, 0.9)',
        font_color='#e0e0e0',
        xaxis_gridcolor='rgba(233, 69, 96, 0.2)',
        yaxis_gridcolor='rgba(233, 69, 96, 0.2)'
    )
    
    return fig

def create_utilization_gauge_piket(results):
    """Gauge utilization untuk 3 tahap"""
    fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]])
    
    # Isi Lauk
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=results['utilization_lauk'],
        title={'text': "🍖 Isi Lauk", 'font': {'color': '#e0e0e0', 'size': 12}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': '#e0e0e0'}, 'bar': {'color': "#e94560"},
               'steps': [{'range': [0, 50], 'color': "rgba(0, 200, 83, 0.3)"},
                        {'range': [50, 80], 'color': "rgba(255, 152, 0, 0.3)"},
                        {'range': [80, 100], 'color': "rgba(233, 69, 96, 0.3)"}]},
        domain={'x': [0, 0.3], 'y': [0, 1]}
    ))
    
    # Angkut
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=results['utilization_angkut'],
        title={'text': "🚚 Angkut", 'font': {'color': '#e0e0e0', 'size': 12}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': '#e0e0e0'}, 'bar': {'color': "#0f3460"},
               'steps': [{'range': [0, 50], 'color': "rgba(0, 200, 83, 0.3)"},
                        {'range': [50, 80], 'color': "rgba(255, 152, 0, 0.3)"},
                        {'range': [80, 100], 'color': "rgba(233, 69, 96, 0.3)"}]},
        domain={'x': [0.35, 0.65], 'y': [0, 1]}
    ))
    
    # Tambah Nasi
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=results['utilization_nasi'],
        title={'text': "🍚 Tambah Nasi", 'font': {'color': '#e0e0e0', 'size': 12}},
        gauge={'axis': {'range': [0, 100], 'tickcolor': '#e0e0e0'}, 'bar': {'color': "#533483"},
               'steps': [{'range': [0, 50], 'color': "rgba(0, 200, 83, 0.3)"},
                        {'range': [50, 80], 'color': "rgba(255, 152, 0, 0.3)"},
                        {'range': [80, 100], 'color': "rgba(233, 69, 96, 0.3)"}]},
        domain={'x': [0.7, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=350, 
        paper_bgcolor='rgba(26, 26, 46, 0.9)', 
        font={'color': '#e0e0e0'},
        title={'text': '📊 Utilisasi Petugas per Tahap', 'font': {'color': '#e0e0e0'}}
    )
    
    return fig

def create_queue_length_chart(model):
    """Chart panjang antrian"""
    queue_data = []
    for stage in ['lauk', 'angkut', 'nasi']:
        if model.statistics['queue_lengths'][stage]:
            stage_df = pd.DataFrame(model.statistics['queue_lengths'][stage])
            stage_df['stage'] = stage
            queue_data.append(stage_df)
    
    if queue_data:
        queue_df = pd.concat(queue_data, ignore_index=True)
        stage_names = {'lauk': '🍖 Isi Lauk', 'angkut': '🚚 Angkut', 'nasi': '🍚 Tambah Nasi'}
        queue_df['stage_name'] = queue_df['stage'].map(stage_names)
        
        fig = px.line(
            queue_df, x='time', y='queue_length', color='stage_name',
            title='📊 Panjang Antrian Sepanjang Waktu',
            labels={'time': 'Waktu Simulasi (menit)', 'queue_length': 'Panjang Antrian', 'stage_name': 'Tahap'}
        )
        fig.update_layout(
            plot_bgcolor='rgba(26, 26, 46, 0.9)',
            paper_bgcolor='rgba(26, 26, 46, 0.9)',
            font_color='#e0e0e0',
            xaxis_gridcolor='rgba(233, 69, 96, 0.2)',
            yaxis_gridcolor='rgba(233, 69, 96, 0.2)',
            hovermode="x unified"
        )
        return fig
    return None

def create_service_time_comparison(model):
    """Box plot waktu layanan per tahap"""
    service_data = []
    for stage, times in model.statistics['service_times'].items():
        if times:
            stage_df = pd.DataFrame({'waktu': times, 'tahap': stage})
            service_data.append(stage_df)
    
    if service_data:
        service_df = pd.concat(service_data, ignore_index=True)
        stage_names = {'lauk': '🍖 Isi Lauk', 'angkut': '🚚 Angkut', 'nasi': '🍚 Tambah Nasi'}
        service_df['tahap_name'] = service_df['tahap'].map(stage_names)
        
        fig = px.box(
            service_df, x='tahap_name', y='waktu', color='tahap_name',
            title='⏱ Distribusi Waktu Layanan per Tahap',
            labels={'tahap_name': 'Tahap', 'waktu': 'Waktu (menit)'}
        )
        fig.update_layout(
            plot_bgcolor='rgba(26, 26, 46, 0.9)',
            paper_bgcolor='rgba(26, 26, 46, 0.9)',
            font_color='#e0e0e0',
            xaxis_gridcolor='rgba(233, 69, 96, 0.2)',
            yaxis_gridcolor='rgba(233, 69, 96, 0.2)',
            showlegend=False
        )
        return fig
    return None

# ============================================
# 🎯 APLIKASI STREAMLIT - STUDI KASUS
# ============================================
def main():
    # Page Configuration
    st.set_page_config(
        page_title="🍽 Studi Kasus: Sistem Piket Kantin IT Del",
        page_icon="🍽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 class="main-header">🍽 Sistem Piket Kantin IT Del</h1>
            <p class="sub-header">Modul Praktikum 3 - Discrete Event Simulation (DES)<br>Bagian 2.1: Studi Kasus</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar dengan Parameter
    with st.sidebar:
        st.markdown("### ⚙️ Parameter Simulasi")
        st.markdown("---")
        
        # ========== Parameter Meja ==========
        st.markdown('<p class="section-header">🪑 Parameter Meja</p>', unsafe_allow_html=True)
        
        num_meja = st.number_input(
            "Jumlah Meja",
            min_value=10, max_value=200, value=60, step=10,
            help="Total meja yang harus dilayani (default: 60)"
        )
        
        mahasiswa_per_meja = st.number_input(
            "Mahasiswa per Meja",
            min_value=1, max_value=10, value=3, step=1,
            help="Jumlah mahasiswa/ompreng per meja (default: 3)"
        )
        
        total_ompreng = num_meja * mahasiswa_per_meja
        
        st.markdown(f"""
        <div class="info-box">
            <strong>📊 Total Ompreng:</strong> {total_ompreng} buah
        </div>
        """, unsafe_allow_html=True)
        
        # ========== Alokasi Petugas ==========
        st.markdown('<p class="section-header">👷 Alokasi 7 Petugas</p>', unsafe_allow_html=True)
        st.info("💡 Total petugas harus = 7 orang sesuai studi kasus")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            petugas_lauk = st.number_input(
                "🍖 Lauk", 
                min_value=1, max_value=5, value=3,
                help="Tahap 1: Isi lauk ke ompreng (30-60 detik)"
            )
        with col2:
            petugas_angkut = st.number_input(
                "🚚 Angkut", 
                min_value=1, max_value=5, value=2,
                help="Tahap 2: Angkut ompreng ke meja (4-7 ompreng/batch)"
            )
        with col3:
            petugas_nasi = st.number_input(
                "🍚 Nasi", 
                min_value=1, max_value=5, value=2,
                help="Tahap 3: Tambah nasi ke ompreng (30-60 detik)"
            )
        
        total_petugas = petugas_lauk + petugas_angkut + petugas_nasi
        
        if total_petugas != 7:
            st.markdown(f"""
            <div class="warning-box">
                ⚠️ <strong>Total petugas harus 7!</strong><br>
                Saat ini: {total_petugas} orang
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-box">
                ✅ <strong>Total petugas: {total_petugas} orang</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # ========== Waktu per Tahap ==========
        st.markdown('<p class="section-header">⏱️ Waktu per Tahap</p>', unsafe_allow_html=True)
        
        # Tahap 1
        st.markdown("""
        <div class="process-card">
            <div class="icon">🍖</div>
            <h4>Tahap 1: Isi Lauk</h4>
            <p>Memasukkan lauk ke dalam ompreng</p>
            <p class="time-info">30-60 detik per ompreng</p>
        </div>
        """, unsafe_allow_html=True)
        min_lauk = st.slider("Min Isi Lauk (menit)", 0.25, 2.0, 0.5, 0.25, key='min_lauk')
        max_lauk = st.slider("Max Isi Lauk (menit)", 0.5, 3.0, 1.0, 0.25, key='max_lauk')
        
        # Tahap 2
        st.markdown("""
        <div class="process-card">
            <div class="icon">🚚</div>
            <h4>Tahap 2: Angkut Ompreng</h4>
            <p>Membawa 4-7 ompreng sekaligus ke meja</p>
            <p class="time-info">20-60 detik per batch</p>
        </div>
        """, unsafe_allow_html=True)
        min_angkut = st.slider("Min Angkut (menit)", 0.25, 2.0, 0.33, 0.25, key='min_angkut')
        max_angkut = st.slider("Max Angkut (menit)", 0.5, 3.0, 1.0, 0.25, key='max_angkut')
        
        min_batch = st.slider("Min Batch Ompreng", 4, 7, 4, 1, key='min_batch')
        max_batch = st.slider("Max Batch Ompreng", 4, 7, 7, 1, key='max_batch')
        
        # Tahap 3
        st.markdown("""
        <div class="process-card">
            <div class="icon">🍚</div>
            <h4>Tahap 3: Tambah Nasi</h4>
            <p>Menambahkan nasi ke dalam ompreng</p>
            <p class="time-info">30-60 detik per ompreng</p>
        </div>
        """, unsafe_allow_html=True)
        min_nasi = st.slider("Min Tambah Nasi (menit)", 0.25, 2.0, 0.5, 0.25, key='min_nasi')
        max_nasi = st.slider("Max Tambah Nasi (menit)", 0.5, 3.0, 1.0, 0.25, key='max_nasi')
        
        # ========== Waktu Mulai ==========
        st.markdown('<p class="section-header">🕐 Waktu Mulai</p>', unsafe_allow_html=True)
        
        start_hour = st.slider("Jam Mulai", 0, 23, 7)
        start_minute = st.slider("Menit Mulai", 0, 59, 0, 15)
        
        st.markdown("---")
        
        # Run Button
        run_simulation = st.button(
            "🚀 Jalankan Simulasi",
            type="primary",
            use_container_width=True
        )
        
        reset_params = st.button(
            "🔄 Reset Parameter",
            use_container_width=True
        )
        
        if reset_params:
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### 📖 Tentang Studi Kasus
        Simulasi ini memodelkan **Sistem Piket Kantin IT Del** 
        dengan 7 mahasiswa petugas dan 3 tahap proses.
        
        **Referensi:** Modul Praktikum 3 - Bagian 2.1
        
        **Fitur:**
        - 🌙 Dark Theme untuk kenyamanan mata
        - 📊 6 Visualisasi Interaktif
        - 💡 Rekomendasi Otomatis
        - 📥 Export Data CSV
        """)
    
    # Main Content Area
    if run_simulation:
        # Validasi total petugas
        if total_petugas != 7:
            st.markdown("""
            <div class="warning-box">
                ❌ <strong>Total petugas harus 7 orang!</strong> Silakan sesuaikan alokasi.
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # Progress Bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
            status_text.text(f"Menjalankan simulasi... {i + 1}%")
        
        status_text.text("✅ Simulasi selesai!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        # Setup Configuration
        config = ConfigPiket(
            NUM_MEJA=num_meja,
            MAHASISWA_PER_MEJA=mahasiswa_per_meja,
            PETUGAS_ISI_LAUK=petugas_lauk,
            PETUGAS_ANGKUT=petugas_angkut,
            PETUGAS_TAMBAH_NASI=petugas_nasi,
            MIN_ISI_LAUK=min_lauk, MAX_ISI_LAUK=max_lauk,
            MIN_ANGKUT=min_angkut, MAX_ANGKUT=max_angkut,
            MIN_TAMBAH_NASI=min_nasi, MAX_TAMBAH_NASI=max_nasi,
            MIN_BATCH_ANGKUT=min_batch, MAX_BATCH_ANGKUT=max_batch,
            START_HOUR=start_hour, START_MINUTE=start_minute
        )
        
        # Run Simulation
        model = SistemPiketKantinDES(config)
        results, df = model.run_simulation()
        
        if results:
            # Success Message
            st.markdown(f"""
            <div class="success-box">
                <h3>✅ Simulasi Berhasil!</h3>
                <p><strong>{num_meja} meja</strong> dengan <strong>{total_ompreng} ompreng</strong> 
                telah diproses oleh <strong>{total_petugas} petugas</strong>.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics Cards
            st.markdown("### 📊 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-metric">{results['avg_waktu_proses']:.2f}</div>
                    <div class="metric-label">⏱ Rata-rata Waktu/Meja (menit)</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-metric">{results['jam_selesai_terakhir'].strftime('%H:%M')}</div>
                    <div class="metric-label">⏰ Waktu Selesai Terakhir</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-metric">{total_petugas}</div>
                    <div class="metric-label">👷 Total Petugas</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_util = np.mean([results['utilization_lauk'], results['utilization_angkut'], results['utilization_nasi']])
                st.markdown(f"""
                <div class="metric-card">
                    <div class="big-metric">{avg_util:.1f}%</div>
                    <div class="metric-label">📈 Rata-rata Utilisasi</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Visualizations
            st.markdown("### 📈 Visualisasi Dashboard")
            
            # Row 1
            col1, col2 = st.columns(2)
            with col1:
                fig_wait = create_process_time_distribution(df)
                st.plotly_chart(fig_wait, use_container_width=True)
            
            with col2:
                fig_timeline = create_timeline_chart(df)
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            # Row 2
            col3, col4 = st.columns(2)
            with col3:
                fig_hourly = create_hourly_distribution_chart(results)
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col4:
                fig_util = create_utilization_gauge_piket(results)
                st.plotly_chart(fig_util, use_container_width=True)
            
            # Row 3
            col5, col6 = st.columns(2)
            with col5:
                fig_queue = create_queue_length_chart(model)
                if fig_queue:
                    st.plotly_chart(fig_queue, use_container_width=True)
            
            with col6:
                fig_service = create_service_time_comparison(model)
                if fig_service:
                    st.plotly_chart(fig_service, use_container_width=True)
            
            # Detailed Statistics
            st.markdown("---")
            st.markdown("### 📋 Statistik Detail")
            
            with st.expander("📊 Lihat Statistik Lengkap", expanded=False):
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown("#### ⏱ Statistik Waktu Proses")
                    st.write(f"**Rata-rata:** {results['avg_waktu_proses']:.2f} menit")
                    st.write(f"**Maksimum:** {results['max_waktu_proses']:.2f} menit")
                    st.write(f"**Minimum:** {results['min_waktu_proses']:.2f} menit")
                    st.write(f"**Standar Deviasi:** {results['std_waktu_proses']:.2f} menit")
                    
                    st.markdown("#### ⏱ Waktu Layanan per Tahap")
                    st.write(f"**Isi Lauk:** {results['avg_service_lauk']*60:.1f} detik")
                    st.write(f"**Angkut:** {results['avg_service_angkut']*60:.1f} detik")
                    st.write(f"**Tambah Nasi:** {results['avg_service_nasi']*60:.1f} detik")
                
                with col_right:
                    st.markdown("#### 📊 Utilisasi per Tahap")
                    st.write(f"**Isi Lauk:** {results['utilization_lauk']:.1f}%")
                    st.write(f"**Angkut:** {results['utilization_angkut']:.1f}%")
                    st.write(f"**Tambah Nasi:** {results['utilization_nasi']:.1f}%")
                    
                    st.markdown("#### 🕐 Distribusi per Jam")
                    for jam in sorted(results['distribusi_jam'].keys()):
                        st.write(f"**Jam {jam:02d}:00:** {results['distribusi_jam'][jam]} meja")
            
            # Data Table
            st.markdown("---")
            st.markdown("### 📄 Data Hasil Simulasi")
            
            with st.expander("📋 Lihat Data Detail", expanded=False):
                st.dataframe(
                    df.sort_values('meja_id'),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download Button
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data CSV",
                    data=csv,
                    file_name=f"studi_kasus_piket_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Recommendations
            st.markdown("---")
            st.markdown("### 💡 Rekomendasi Optimasi")
            
            recommendations = []
            
            if results['utilization_lauk'] > 80:
                recommendations.append("🔴 **Tahap Isi Lauk** memiliki utilisasi tinggi (>80%). Pertimbangkan menambah petugas di tahap ini.")
            
            if results['utilization_angkut'] > 80:
                recommendations.append("🔴 **Tahap Angkut** memiliki utilisasi tinggi (>80%). Pertimbangkan menambah petugas atau mengurangi ukuran batch.")
            
            if results['utilization_nasi'] > 80:
                recommendations.append("🔴 **Tahap Tambah Nasi** memiliki utilisasi tinggi (>80%). Pertimbangkan menambah petugas di tahap ini.")
            
            if results['avg_waktu_proses'] > 5:
                recommendations.append("🟡 **Waktu proses rata-rata** cukup lama (>5 menit). Evaluasi efisiensi setiap tahap.")
            
            if not recommendations:
                recommendations.append("🟢 **Sistem berjalan optimal!** Semua tahap memiliki utilisasi yang baik (<80%).")
            
            for rec in recommendations:
                st.markdown(f"""
                <div class="info-box">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="warning-box">
                ❌ <strong>Gagal menjalankan simulasi!</strong> Silakan coba lagi dengan parameter yang berbeda.
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Default Welcome Screen
        st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h2 style="color: #e0e0e0;">👋 Selamat Datang di Simulasi Sistem Piket</h2>
            <p style="color: #a0a0a0; font-size: 1.2em;">Atur parameter di sidebar kiri, lalu klik <strong>"🚀 Jalankan Simulasi"</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Process Flow Diagram
        st.markdown("---")
        st.markdown("### 🔄 Alur Proses Sistem Piket")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="process-card">
                <div class="icon">🍖</div>
                <h4>Tahap 1</h4>
                <p>Isi Lauk</p>
                <p class="time-info">30-60 detik</p>
                <p style="color: #a0a0a0; font-size: 0.8em;">3 petugas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="process-card">
                <div class="icon">➡️</div>
                <h4>Buffer</h4>
                <p>Antrian</p>
                <p class="time-info">-</p>
                <p style="color: #a0a0a0; font-size: 0.8em;">Queue</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="process-card">
                <div class="icon">🚚</div>
                <h4>Tahap 2</h4>
                <p>Angkut</p>
                <p class="time-info">20-60 detik</p>
                <p style="color: #a0a0a0; font-size: 0.8em;">2 petugas, 4-7 batch</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="process-card">
                <div class="icon">🍚</div>
                <h4>Tahap 3</h4>
                <p>Tambah Nasi</p>
                <p class="time-info">30-60 detik</p>
                <p style="color: #a0a0a0; font-size: 0.8em;">2 petugas</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Info Box
        st.markdown("""
        <div class="info-box" style="margin-top: 30px;">
            <strong>📋 Informasi Studi Kasus:</strong><br>
            • Total Petugas: 7 orang mahasiswa<br>
            • Total Meja: 60 meja (default)<br>
            • Mahasiswa per Meja: 3 orang (180 total)<br>
            • Waktu Mulai: 07:00 pagi<br>
            • Sistem: 3 tahap dengan antrian antar tahap
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        <p><strong>MODSIM - Discrete Event Simulation (DES)</strong></p>
        <p>Modul Praktikum 3 - Bagian 2.1: Studi Kasus</p>
        <p>Terakhir diupdate: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <p>🎓 Institut Teknologi Del</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()