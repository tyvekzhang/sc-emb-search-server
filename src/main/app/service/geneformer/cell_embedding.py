import torch
import datetime
import os
import pickle
import random
import traceback

import loompy
import numpy as np
import pandas as pd
from anndata import AnnData
from loguru import logger

from src.main.app.common.config.config_manager import load_config
from src.main.app.model.job_model import JobDO
from ..geneformer import EmbExtractor
from ..geneformer.tokenizer import TOKEN_DICTIONARY_FILE, TranscriptomeTokenizer

gene_info_path = str(load_config().server.model_dir) + os.sep + "geneformer" + os.sep + "gene_info_table.csv"
gene_info = pd.read_csv(gene_info_path)
gene_name_id_combine_dict = gene_info.set_index("gene_name")["ensembl_id"].to_dict()
gene_name_type_dict = gene_info.set_index("gene_name")["gene_type"].to_dict()
gene_id_type_dict = gene_info.set_index("ensembl_id")["gene_type"].to_dict()
func_gene_list = [
    i
    for i in gene_info[
        (gene_info["gene_type"] == "protein_coding")
        | (gene_info["gene_type"] == "miRNA")
    ]["ensembl_id"]
]

with open(TOKEN_DICTIONARY_FILE, "rb") as f:
    gene_token_info = pickle.load(f)

def generate_random_str():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    random_str = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for _ in range(8))
    return date_str + random_str

def preprocess(adata: AnnData, job: JobDO) -> str:
    """
    Preprocess for h5ad
    """
    try:
        job_id = str(job.id)
        task_dir = str(load_config().server.output_dir) + os.sep + job_id
        if not os.path.exists(task_dir):
            os.makedirs(task_dir)
        file_name = job_id
        gene_type_arr = []
        ensembl_id_arr = []
        pretrain_uncover_gene_arr = []
        for var_info in adata.var_names:
            if (
                    var_info in gene_name_type_dict
                    and gene_name_id_combine_dict[var_info] in gene_token_info
            ):
                gene_type_arr.append(gene_name_type_dict[var_info])
                ensembl_id_arr.append(gene_name_id_combine_dict[var_info])
            elif str(var_info).startswith("ENSG") and var_info in gene_token_info:
                gene_type_arr.append(gene_id_type_dict[var_info])
                ensembl_id_arr.append(var_info)
            else:
                pretrain_uncover_gene_arr.append(var_info)
        if len(pretrain_uncover_gene_arr) != 0:
            logger.warning(f"Gene not in token file will be remove")
            adata = adata[:, adata.var_names.drop(pretrain_uncover_gene_arr)]
        if adata.n_obs == 0:
            raise Exception("Anndata.var_names should be gene name")
        total_genes_per_row = adata.X.sum(axis=1)
        filename = f"{task_dir}/{file_name}.loom"
        loompy.create(
            filename,
            adata.X.T,
            {
                "ensembl_id": np.array(ensembl_id_arr),
                "gene_type": gene_type_arr,
            },
            {"n_counts": total_genes_per_row, "barcode": np.array(adata.obs_names)},
        )
        logger.info(f"{filename} is done")
        del adata
        return task_dir
    except Exception as e:
        logger.error(f"{traceback.print_exc()}")
        raise e

def get_and_save_cell_embedding(input_data_path: str, pretrain_model_path: str, output_directory: str, suffix: str):
    emb_extractor = EmbExtractor(model_type="Pretrained",
                         num_classes=0,
                         filter_data=None,
                         max_ncells=None,
                         emb_layer=-1,
                         emb_label=None,
                         labels_to_plot=None,
                         forward_batch_size=1,
                         nproc=1)

    embs = emb_extractor.extract_embs(pretrain_model_path,
                              input_data_path,
                              output_directory,
                              suffix)
    logger.info(f"cell embedding generate in {os.path.join(output_directory, suffix)}")
    logger.info(embs)
    return embs

def process_embeddings(raw_cell_emb):
    linear_layer = torch.nn.Linear(len(raw_cell_emb[0]), 128)
    emb_data = torch.tensor(raw_cell_emb[0])
    result =  linear_layer(emb_data)
    logger.info(f"细胞的维度: {result.shape}")
    # 将结果转换为 NumPy 数组
    if result.is_cuda:
        result = result.cpu()
    result_np = result.detach().numpy()
    return result_np

def generate_cell_embedding(adata: AnnData, job: JobDO):
    task_dir = preprocess(adata=adata, job=job)
    tk = TranscriptomeTokenizer(custom_attr_name_dict={"barcode": "barcode"})
    output_prefix="rank_value_encoding"
    logger.info("Tokenize data start")
    tk.tokenize_data(task_dir, task_dir, output_prefix)
    logger.info("Tokenize data end")
    rank_value_encoding_path = os.path.join(task_dir, output_prefix + ".dataset")
    logger.info(f"Rank value encoding done: {rank_value_encoding_path}")
    server_config = load_config().server
    output_dir = server_config.output_dir
    suffix = str(job.id)
    model_dir = server_config.model_dir + os.sep + "geneformer"
    raw_cell_emb =  get_and_save_cell_embedding(rank_value_encoding_path, model_dir, output_dir, suffix)
    return raw_cell_emb


