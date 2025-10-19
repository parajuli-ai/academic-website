"""
Script to index website documents for RAG
Run this script to create/update the vector store
"""

import os
import sys
from pathlib import Path

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, DirectoryLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def load_documents(website_url, cv_path=None, markdown_dir=None):
    """
    Load documents from various sources
    
    Args:
        website_url: Base URL of the deployed website
        cv_path: Path to CV PDF file
        markdown_dir: Directory containing markdown files
        
    Returns:
        List of loaded documents
    """
    documents = []
    
    # Load website content
    if website_url:
        print(f"Loading website content from {website_url}...")
        pages = [
            website_url,
            f"{website_url}/research",
            f"{website_url}/publications",
            f"{website_url}/teaching",
            f"{website_url}/cv",
            f"{website_url}/contact",
        ]
        
        for url in pages:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
                print(f"  ✓ Loaded {url}")
            except Exception as e:
                print(f"  ✗ Could not load {url}: {e}")
    
    # Load CV PDF
    if cv_path and os.path.exists(cv_path):
        print(f"\nLoading CV from {cv_path}...")
        try:
            loader = PyPDFLoader(cv_path)
            cv_docs = loader.load()
            documents.extend(cv_docs)
            print(f"  ✓ Loaded {len(cv_docs)} pages from CV")
        except Exception as e:
            print(f"  ✗ Error loading CV: {e}")
    
    # Load markdown files
    if markdown_dir and os.path.exists(markdown_dir):
        print(f"\nLoading markdown files from {markdown_dir}...")
        try:
            # Load .md files
            md_files = list(Path(markdown_dir).rglob("*.md"))
            for md_file in md_files:
                # Skip certain directories
                if any(skip in str(md_file) for skip in ['node_modules', '.git', 'vendor']):
                    continue
                    
                try:
                    loader = TextLoader(str(md_file), encoding='utf-8')
                    docs = loader.load()
                    # Add file path to metadata
                    for doc in docs:
                        doc.metadata['source'] = str(md_file)
                    documents.extend(docs)
                    print(f"  ✓ Loaded {md_file.name}")
                except Exception as e:
                    print(f"  ✗ Could not load {md_file.name}: {e}")
        except Exception as e:
            print(f"  ✗ Error loading markdown directory: {e}")
    
    return documents

def create_vector_store(documents, persist_directory="./chroma_db"):
    """
    Create vector store from documents
    
    Args:
        documents: List of documents to index
        persist_directory: Directory to persist vector store
        
    Returns:
        Created vector store
    """
    if not documents:
        raise ValueError("No documents provided for indexing")
    
    print(f"\nProcessing {len(documents)} documents...")
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks")
    
    # Initialize embeddings
    print("\nInitializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Create vector store
    print(f"\nCreating vector store in {persist_directory}...")
    
    # Remove existing vector store if it exists
    if os.path.exists(persist_directory):
        import shutil
        shutil.rmtree(persist_directory)
        print(f"  Removed existing vector store")
    
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"  ✓ Vector store created successfully!")
    print(f"  Total chunks indexed: {len(splits)}")
    
    return vector_store

def main():
    """Main function"""
    print("=" * 60)
    print("Document Indexing for RAG System")
    print("=" * 60)
    
    # Configuration
    # Update these values based on your setup
    WEBSITE_URL = os.getenv("WEBSITE_URL", "https://yourusername.github.io")
    CV_PATH = os.getenv("CV_PATH", "../assets/cv.pdf")
    MARKDOWN_DIR = os.getenv("MARKDOWN_DIR", "../")
    PERSIST_DIR = "./chroma_db"
    
    print("\nConfiguration:")
    print(f"  Website URL: {WEBSITE_URL}")
    print(f"  CV Path: {CV_PATH}")
    print(f"  Markdown Directory: {MARKDOWN_DIR}")
    print(f"  Vector Store Directory: {PERSIST_DIR}")
    
    # Check if markdown directory exists
    if not os.path.exists(MARKDOWN_DIR):
        print(f"\nWarning: Markdown directory not found: {MARKDOWN_DIR}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Load documents
    print("\n" + "=" * 60)
    print("Loading Documents")
    print("=" * 60)
    
    documents = load_documents(
        website_url=WEBSITE_URL,
        cv_path=CV_PATH if os.path.exists(CV_PATH) else None,
        markdown_dir=MARKDOWN_DIR
    )
    
    if not documents:
        print("\n❌ Error: No documents could be loaded!")
        print("\nTroubleshooting:")
        print("  1. Make sure your website is deployed and accessible")
        print("  2. Add your CV PDF to the assets directory")
        print("  3. Check that markdown files exist in the specified directory")
        sys.exit(1)
    
    print(f"\n✓ Successfully loaded {len(documents)} documents")
    
    # Create vector store
    print("\n" + "=" * 60)
    print("Creating Vector Store")
    print("=" * 60)
    
    try:
        vector_store = create_vector_store(documents, PERSIST_DIR)
        
        print("\n" + "=" * 60)
        print("✓ Indexing Complete!")
        print("=" * 60)
        print("\nYou can now run the FastAPI backend:")
        print("  python app.py")
        print("\nOr deploy to Vercel:")
        print("  vercel --prod")
        
    except Exception as e:
        print(f"\n❌ Error creating vector store: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

