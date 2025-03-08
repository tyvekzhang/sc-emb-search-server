import scanpy as sc
from matplotlib import pyplot as plt

sc.set_figure_params(dpi=100)
plt.rcParams["figure.figsize"] = [6, 4]

import warnings

warnings.filterwarnings("ignore")
from scimilarity.utils import lognorm_counts, align_dataset
from scimilarity import CellQuery
model_path = "/data/tyvek/query_model_v1"
cq = CellQuery(model_path)
data_path = "/data/tyvek/h5ad/adamson_perturb_processed.h5ad"
adams = sc.read(data_path)
adams = align_dataset(adams, cq.gene_order)
adams = lognorm_counts(adams)
adams.obsm["X_scimilarity"] = cq.get_embeddings(adams.X)
query_cell = adams[adams.obs.index == "10"]
query_embedding = query_cell.obsm["X_scimilarity"]
k=1000
nn_idxs, nn_dists, results_metadata = cq.search_nearest(query_embedding, k=k)
print(results_metadata)