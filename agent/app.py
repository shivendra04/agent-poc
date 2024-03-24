
import sys, os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.core import VectorStoreIndex
from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker

def load_and_parse_documents(files_list):
    parser = LlamaParse(
        result_type="markdown",
        verbose=True,
        language="en",
        num_workers=2,
    )
    return parser.load_data(files_list)

def set_llm_and_embed_models():
    Settings.llm = OpenAI(model="gpt-3.5-turbo")
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

def get_nodes_and_objects(documents):
    node_parser = MarkdownElementNodeParser(llm=OpenAI('gpt-3.5-turbo'), num_workers=8)
    nodes = node_parser.get_nodes_from_documents(documents=documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    return base_nodes, objects

def create_and_get_index(base_nodes, objects):
    return VectorStoreIndex(nodes=base_nodes+objects)

def perform_reranking(recursive_index):
    reranker = FlagEmbeddingReranker(
        top_n=5,
        model="BAAI/bge-reranker-large",
    )
    return reranker

def get_query_engine(recursive_index, reranker):
    recursive_query_engine = recursive_index.as_query_engine(
        similarity_top_k=15,
        node_postprocessors=[reranker],
        verbose=True
    )
    return recursive_query_engine

def init_rag(files_list):
    load_api_keys()
    set_llm_and_embed_models()
    documents = load_and_parse_documents(files_list)
    nodes, objects = get_nodes_and_objects(documents)
    recursive_index = create_and_get_index(nodes, objects)
    reranker = perform_reranking(recursive_index)
    return get_query_engine(recursive_index, reranker)
    
load_api_keys()