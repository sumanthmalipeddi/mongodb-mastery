"""
LangChain + MongoDB Atlas Vector Search
========================================
Integration example showing how to use LangChain with MongoDB
for document storage, embedding, and QA.

Required packages:
    pip install langchain langchain-mongodb langchain-openai pymongo

Prerequisites:
    - MongoDB Atlas cluster with vector search index
    - OPENAI_API_KEY in .env
    - See vector_search_setup.md for index configuration

Usage:
    python langchain_example.py

Note: This script requires OPENAI_API_KEY. It will show the code structure
      even without the key, but won't run the actual operations.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

MONGODB_URI = os.getenv("MONGODB_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_NAME = "quotes_db"
COLLECTION_NAME = "langchain_vectors"
INDEX_NAME = "vector_index"


def check_prerequisites():
    """Check that required packages and keys are available."""
    if not MONGODB_URI:
        print("❌ Set MONGODB_URI in .env file!")
        sys.exit(1)

    if not OPENAI_API_KEY:
        print("⚠️  OPENAI_API_KEY not found in .env")
        print("   This script requires OpenAI for embeddings.")
        print("   Add OPENAI_API_KEY=sk-... to your .env file\n")
        print("   Showing code structure without running:\n")
        show_code_structure()
        sys.exit(0)

    # Check for required packages
    try:
        import langchain
        import langchain_mongodb
        import langchain_openai
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Install with: pip install langchain langchain-mongodb langchain-openai")
        sys.exit(1)


def show_code_structure():
    """Print the code structure for reference without running it."""
    print("""
    # =========================================================================
    # LangChain + MongoDB Atlas Vector Search — Code Structure
    # =========================================================================

    from langchain_openai import OpenAIEmbeddings
    from langchain_mongodb import MongoDBAtlasVectorSearch
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import ChatOpenAI
    from langchain.chains import RetrievalQA
    from pymongo import MongoClient

    # 1. Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    collection = client[DB_NAME][COLLECTION_NAME]

    # 2. Set up embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # 3. Create vector store
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name="vector_index",
        text_key="text",
        embedding_key="embedding"
    )

    # 4. Add documents
    texts = ["Document 1 content...", "Document 2 content..."]
    vector_store.add_texts(texts)

    # 5. Similarity search
    results = vector_store.similarity_search("search query", k=5)

    # 6. QA Chain (RAG)
    llm = ChatOpenAI(model="gpt-4o-mini")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 5})
    )
    answer = qa_chain.invoke({"query": "What is the meaning of life?"})
    """)


def main():
    """Full LangChain + MongoDB Vector Search demo."""
    check_prerequisites()

    print("=" * 60)
    print("LangChain + MongoDB Atlas Vector Search")
    print("=" * 60)

    from pymongo import MongoClient
    from langchain_openai import OpenAIEmbeddings
    from langchain_mongodb import MongoDBAtlasVectorSearch
    from langchain_openai import ChatOpenAI
    from langchain.chains import RetrievalQA

    # =========================================================================
    # Step 1: Connect to MongoDB
    # =========================================================================
    print("\n--- Step 1: Connect to MongoDB ---")
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("  ✅ Connected")

    # =========================================================================
    # Step 2: Set up embeddings model
    # =========================================================================
    print("\n--- Step 2: Set up OpenAI embeddings ---")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    print("  ✅ Embeddings model ready")

    # =========================================================================
    # Step 3: Create vector store
    # =========================================================================
    print("\n--- Step 3: Create MongoDB vector store ---")
    vector_store = MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embeddings,
        index_name=INDEX_NAME,
        text_key="text",
        embedding_key="embedding"
    )
    print("  ✅ Vector store configured")

    # =========================================================================
    # Step 4: Load and embed documents
    # =========================================================================
    print("\n--- Step 4: Load quotes and create embeddings ---")

    # Get quotes from the scraper collection
    source = db["quotes"]
    quotes = list(source.find({}, {"text": 1, "author": 1, "tags": 1, "_id": 0}).limit(20))

    if not quotes:
        print("  ⚠️  No quotes found. Run scraper.py first.")
        client.close()
        return

    # Prepare texts and metadata
    texts = [q["text"] for q in quotes]
    metadatas = [{"author": q["author"], "tags": q.get("tags", [])} for q in quotes]

    # Clear existing and add new documents
    collection.drop()
    vector_store.add_texts(texts=texts, metadatas=metadatas)
    print(f"  ✅ Embedded and stored {len(texts)} quotes")

    # =========================================================================
    # Step 5: Similarity search
    # =========================================================================
    print("\n--- Step 5: Similarity Search ---")

    search_queries = [
        "wisdom about life and living",
        "courage and being brave",
        "love and relationships"
    ]

    for query in search_queries:
        print(f"\n  🔍 \"{query}\"")
        try:
            results = vector_store.similarity_search_with_score(query, k=3)
            for doc, score in results:
                author = doc.metadata.get("author", "Unknown")
                print(f"    [{score:.3f}] {author}: \"{doc.page_content[:60]}...\"")
        except Exception as e:
            print(f"    ⚠️  Search failed: {e}")
            print(f"    Make sure you've created a vector search index in Atlas")
            break

    # =========================================================================
    # Step 6: RAG — Question Answering
    # =========================================================================
    print(f"\n--- Step 6: RAG Question Answering ---")

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",  # Stuff all retrieved docs into context
            retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True
        )

        questions = [
            "What do the quotes say about imagination and creativity?",
            "What advice do the quotes give about love?",
        ]

        for question in questions:
            print(f"\n  ❓ {question}")
            try:
                result = qa_chain.invoke({"query": question})
                print(f"  💬 {result['result']}")
                print(f"  📚 Sources: {len(result.get('source_documents', []))} quotes")
            except Exception as e:
                print(f"  ⚠️  QA failed: {e}")
                print(f"  This requires a vector search index in Atlas.")

    except Exception as e:
        print(f"  ⚠️  Could not set up QA chain: {e}")

    # =========================================================================
    # Cleanup
    # =========================================================================
    print(f"\n{'=' * 60}")
    print("Done!")
    print(f"  Vector store: {DB_NAME}.{COLLECTION_NAME}")
    print(f"  Documents: {collection.count_documents({})}")
    print("=" * 60)

    client.close()


if __name__ == "__main__":
    main()
