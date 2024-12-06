import torch
import typer
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import AutoProcessor
from PIL import Image

from colpali_engine.models.paligemma_colbert_architecture import ColPali
from colpali_engine.trainer.retrieval_evaluator import CustomEvaluator
from colpali_engine.utils.colpali_processing_utils import process_images, process_queries
from colpali_engine.utils.image_from_page_utils import load_from_dataset

def main() -> None:
    """Integrated system for document indexing and retrieval using ColPali"""

    # Load model
    model_name = "vidore/colpali"
    model = ColPali.from_pretrained(
        "vidore/colpaligemma-3b-mix-448-base",
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    ).eval()
    model.load_adapter(model_name)
    processor = AutoProcessor.from_pretrained(model_name)

    # Load documents (images, PDFs, etc.)
    # split = 'test' or 'test[:16]' to reduce the number of documents for testing
    images = load_from_dataset("vidore/docvqa_test_subsampled", split="test[:16]")  # Adjust path as necessary
    queries = ["From which university does James V. Fiorca come?", "Who is the Japanese prime minister?"]

    # Run inference for documents
    dataloader_docs = DataLoader(
        images,
        batch_size=4,
        shuffle=False,
        collate_fn=lambda x: process_images(processor, x),
    )

    document_embeddings = []
    for batch_doc in tqdm(dataloader_docs, desc="Processing documents"):
        with torch.no_grad():
            batch_doc = {k: v.to(model.device) for k, v in batch_doc.items()}
            embeddings_doc = model(**batch_doc)
        document_embeddings.extend(list(torch.unbind(embeddings_doc.to("cpu"))))

    # Run inference for queries
    dataloader_queries = DataLoader(
        queries,
        batch_size=4,
        shuffle=False,
        collate_fn=lambda x: process_queries(processor, x, Image.new("RGB", (448, 448), (255, 255, 255))),
    )

    query_embeddings = []
    for batch_query in tqdm(dataloader_queries, desc="Processing queries"):
        with torch.no_grad():
            batch_query = {k: v.to(model.device) for k, v in batch_query.items()}
            embeddings_query = model(**batch_query)
        query_embeddings.extend(list(torch.unbind(embeddings_query.to("cpu"))))

    retriever_model = ColPali.from_pretrained(
        "vidore/colpaligemma-3b-mix-448-base",
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    ).eval()
    retriever_model.load_adapter(model_name)

    # Run evaluation
    retriever_evaluator = CustomEvaluator(is_multi_vector=True, retriever=retriever_model)
    scores = retriever_evaluator.evaluate(query_embeddings, document_embeddings)
    print("Best matching document indices:", scores.argmax(axis=1))

if __name__ == "__main__":
    typer.run(main)
