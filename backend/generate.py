import os
from pathlib import Path
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
#from langchain.retrievers.document_compressors import FlashrankRerank
from llama_parse import LlamaParse

# Set API keys
GROQ_API_KEY = "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"
LLAMA_PARSE_KEY = "llx-vFjatmoq2uPnMhXQWW9bHSrQ5JBt0HNmfGxqe3kJgOtQiwjc"

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Fungsi untuk memproses banyak dokumen PDF
async def process_multiple_pdfs(pdf_folder, output_dir):
    instruction = """The provided documents contain financial information. Extract key details precisely."""
    parser = LlamaParse(
        api_key=LLAMA_PARSE_KEY,
        result_type="markdown",
        parsing_instruction=instruction,
        max_timeout=5000,
    )

    # Pastikan folder output ada
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Memproses semua file PDF di folder
    for pdf_file in Path(pdf_folder).glob("*.pdf"):
        print(f"Memproses {pdf_file.name}...")
        try:
            # Parsing dokumen menggunakan LlamaParse
            llama_parse_documents = await parser.aload_data(str(pdf_file))
            if not llama_parse_documents or len(llama_parse_documents) == 0:
                raise ValueError(f"Dokumen {pdf_file.name} tidak menghasilkan output yang valid.")

            # Mengambil teks hasil parsing
            parsed_doc = llama_parse_documents[0].text

            # Simpan hasil parsing ke file markdown
            markdown_path = output_dir / f"{pdf_file.stem}.md"
            with markdown_path.open("w", encoding="utf-8") as f:
                f.write(parsed_doc)

            print(f"Hasil parsing disimpan di {markdown_path}")
        except Exception as e:
            print(f"Gagal memproses {pdf_file.name}: {e}")

# Fungsi untuk membagi dokumen dan membuat Qdrant index
def create_qdrant_index(parsed_folder, db_path):
    # Muat semua file markdown hasil parsing
    documents = []
    for markdown_file in Path(parsed_folder).glob("*.md"):
        loader = UnstructuredMarkdownLoader(markdown_file)
        documents.extend(loader.load())

    # Pisahkan dokumen menjadi bagian kecil
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=128)
    docs = text_splitter.split_documents(documents)

    # Buat embedding menggunakan FastEmbed
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")

    # Simpan embedding ke dalam Qdrant
    qdrant = Qdrant.from_documents(
        docs,
        embeddings,
        path=db_path,
        collection_name="financial_embeddings",
    )

    print(f"Qdrant index berhasil dibuat di {db_path}")
    return qdrant  # Return seluruh vector store Qdrant



# Fungsi utama untuk menjalankan proses
async def main():
    pdf_folder = "data/dataset"  # Folder berisi file PDF
    parsed_folder = "data/parsed_documents"  # Folder untuk hasil parsing
    db_path = "./data/db"  # Path untuk database Qdrant

    # Langkah 1: Parsing semua PDF
    await process_multiple_pdfs(pdf_folder, parsed_folder)

    # Langkah 2: Membuat Qdrant index
    qdrant = create_qdrant_index(parsed_folder, db_path)

    # Langkah 3: Simpan Qdrant database
    print(f"Qdrant database telah disimpan di {db_path}")


# Jalankan fungsi utama
if __name__ == "__main__":
    asyncio.run(main())

