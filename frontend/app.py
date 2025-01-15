import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Backend API base URL
BASE_URL = "http://127.0.0.1:8000"  # Update to your backend server's URL

# App title and sidebar
st.title("AI-Powered Financial Assistant")
st.sidebar.title("Menu")

menu = st.sidebar.radio("Pilih Menu:", ["Upload File", "Laporan Keuangan", "AI Assistant", "Rekomendasi Penghematan"])

if menu == "Upload File":
    st.header("Upload File Transaksi")
    uploaded_file = st.file_uploader("Unggah file CSV atau PDF:", type=["csv", "pdf"])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1]
        files = {"file": (uploaded_file.name, uploaded_file, f"application/{file_type}")}

        # Send file to backend
        response = requests.post(f"{BASE_URL}/upload", files=files)
        if response.status_code == 200:
            st.success("File berhasil diunggah dan diproses!")
            data = response.json().get("data", [])
            if data:
                st.dataframe(pd.DataFrame(data))
            else:
                st.warning("Data transaksi kosong setelah pemrosesan.")
        else:
            st.error("Gagal memproses file. Pastikan formatnya benar.")

elif menu == "Laporan Keuangan":
    st.header("Laporan Keuangan")
    response = requests.get(f"{BASE_URL}/report")

    if response.status_code == 200:
        chart_path = response.json().get("chart", "")
        if chart_path:
            with open(chart_path, "rb") as chart_file:
                st.image(chart_file.read(), caption="Distribusi Pengeluaran Berdasarkan Kategori")
        else:
            st.error("Laporan tidak memiliki data visualisasi.")
    else:
        st.error("Gagal menghasilkan laporan. Pastikan ada data transaksi.")

elif menu == "AI Assistant":
    st.header("AI Assistant untuk Analisis Keuangan")
    query = st.text_input("Ajukan pertanyaan Anda:")
    example_queries = [
        "Apa kategori dengan pengeluaran terbesar bulan ini?",
        "Tolong analisis struk belanja supermarket ini dan bandingkan dengan budget.",
        "Berikan 3 rekomendasi cara menghemat pengeluaran bulan depan."
    ]
    st.markdown("**Contoh pertanyaan:**")
    for q in example_queries:
        st.markdown(f"- {q}")

    if st.button("Tanya AI") and query:
        response = requests.post(f"{BASE_URL}/query", json={"query": query})
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "Tidak ada jawaban.")
            
            # Tampilkan jawaban utama
            st.success("Jawaban AI:")
            st.write(answer)
            
            # Tampilkan dokumen sumber (opsional)
            source_documents = result.get("source_documents", [])
            if source_documents:
                with st.expander("Dokumen Sumber"):
                    for doc in source_documents:
                        source = doc["metadata"].get("source", "Tidak diketahui")
                        content = doc.get("page_content", "Tidak ada konten.")
                        st.write(f"**Sumber:** {source}")
                        st.write(f"**Konten:** {content}")
        else:
            st.error("Gagal mendapatkan jawaban dari AI.")


elif menu == "Rekomendasi Penghematan":
    st.header("Rekomendasi Penghematan")
    response = requests.get(f"{BASE_URL}/recommendations")
    
    if response.status_code == 200:
        data = response.json()
        if "recommendations" in data:
            recommendations = data["recommendations"]
            st.success("Berikut rekomendasi penghematan Anda:")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        else:
            st.error("Tidak ada data rekomendasi yang ditemukan.")
    else:
        st.error("Gagal mendapatkan rekomendasi penghematan dari backend.")
