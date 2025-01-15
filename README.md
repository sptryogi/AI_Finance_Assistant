# Asisten Keuangan Berbasis AI

Repositori ini berisi aplikasi asisten keuangan berbasis AI yang dibangun menggunakan **FastAPI** (backend) dan **Streamlit** (frontend). Aplikasi ini menyediakan fitur untuk mengunggah file transaksi, membuat laporan keuangan, melakukan analisis dengan asisten AI, dan memberikan rekomendasi penghematan.

---

## Fitur
1. **Unggah dan Analisis Transaksi:**
   - Mendukung file transaksi dalam format CSV dan PDF.
   - Kategorisasi transaksi secara otomatis.
2. **Membuat Laporan Keuangan:**
   - Visualisasi pengeluaran berdasarkan kategori.
3. **Asisten AI untuk Analisis Keuangan:**
   - Menjawab pertanyaan pengguna terkait data keuangan.
4. **Rekomendasi Penghematan:**
   - Memberikan saran penghematan berdasarkan pola pengeluaran.

---

## Teknologi yang Digunakan
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** SQLite
- **Komponen AI:** LangChain, Qdrant, FastEmbed, Groq

---

## Instalasi

### Prasyarat
1. **Python 3.9+**
2. **Pip** (manajer paket Python)
3. **Git**
4. **API Key OpenAI** (atau Groq API Key untuk embeddings)

### Clone Repositori
```bash
# Clone repositori ini
git clone https://github.com/your-repo/ai-finance-assistant.git

# Masuk ke direktori proyek
cd ai-finance-assistant
```

### Instal Dependensi
```bash
# Instal pustaka Python yang dibutuhkan
pip install -r requirements.txt
```

---

## Persiapan

### 1. Variabel Lingkungan
Buat file `.env` di direktori utama dengan isi sebagai berikut:
```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 2. Inisialisasi Database
Jalankan perintah berikut untuk menginisialisasi database SQLite:
```bash
python -c "from main import init_db; init_db()"
```

### 3. Siapkan Embedding AI
Jalankan skrip untuk membuat embedding dokumen untuk query asisten AI:
```bash
python backend/generate.py
```
Langkah ini akan memproses dokumen di folder `data/parsed_documents` dan membuat embedding yang disimpan di direktori `data/db`.

---

## Menjalankan Aplikasi

### 1. Jalankan Backend (FastAPI)
Gunakan perintah berikut untuk menjalankan server FastAPI:
```bash
uvicorn main:app --reload
```
Backend akan tersedia di `http://127.0.0.1:8000`.

### 2. Jalankan Frontend (Streamlit)
Buka terminal baru dan jalankan perintah berikut:
```bash
streamlit run frontend/app.py
```
Frontend akan tersedia di `http://localhost:8501`.

---

## Penggunaan

### 1. Unggah File Transaksi
- Navigasikan ke menu **Upload File**.
- Unggah file CSV atau PDF yang berisi transaksi.
- Transaksi akan dikategorikan dan disimpan ke dalam database.

### 2. Lihat Laporan Keuangan
- Navigasikan ke menu **Laporan Keuangan**.
- Lihat diagram pie yang menampilkan pengeluaran berdasarkan kategori.

### 3. Gunakan Asisten AI
- Navigasikan ke menu **AI Assistant**.
- Masukkan pertanyaan atau gunakan contoh pertanyaan yang tersedia.
- Lihat wawasan yang dihasilkan AI berdasarkan transaksi yang diunggah dan dokumen yang diindeks.

### 4. Dapatkan Rekomendasi Penghematan
- Navigasikan ke menu **Rekomendasi Penghematan**.
- Lihat saran penghematan yang disesuaikan berdasarkan pola pengeluaran.

---

## Contoh Pertanyaan untuk AI Assistant
- "Apa kategori dengan pengeluaran terbesar bulan ini?"
- "Tolong analisis struk belanja supermarket ini dan bandingkan dengan budget."
- "Berikan 3 rekomendasi cara menghemat pengeluaran bulan depan."

---

## Struktur Proyek
```
.
├── backend/
│   ├── main.py             # Aplikasi backend FastAPI
│   ├── generate.py         # Skrip pembuatan embedding
├── frontend/
│   ├── app.py              # Aplikasi frontend Streamlit
├── data/
│   ├── parsed_documents/   # Folder untuk dokumen yang sudah diparsing (Markdown)
│   ├── db/                 # Folder untuk embedding Qdrant
├── requirements.txt        # Dependensi Python
└── README.md               # Petunjuk proyek
```

---

## Deployment
Anda dapat mendesain aplikasi ini menggunakan **Streamlit Cloud** atau platform serupa untuk frontend. Untuk backend, Anda dapat menggunakan layanan seperti **AWS**, **Heroku**, atau **Render**.

---

## Lisensi
Proyek ini dilisensikan di bawah MIT License.
