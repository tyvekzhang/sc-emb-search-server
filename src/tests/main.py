import scanpy as sc
from matplotlib import pyplot as plt
import pickle  # 导入 pickle 模块

sc.set_figure_params(dpi=100)
plt.rcParams["figure.figsize"] = [6, 4]

import warnings
warnings.filterwarnings("ignore")

from scimilarity.utils import lognorm_counts, align_dataset
from scimilarity import CellQuery

# 加载模型和数据
model_path = "/data/tyvek/model_v1.1"
cq = CellQuery(model_path)
data_path = "/data/tyvek/h5ad/anno_zheng68k.h5ad"
adams = sc.read(data_path)

# 数据预处理
adams.layers['counts'] = adams.X.copy()
adams = align_dataset(adams, cq.gene_order)
adams = lognorm_counts(adams)
adams.obsm["X_scimilarity"] = cq.get_embeddings(adams.X)

# 查询特定细胞
query_cell = adams[adams.obs.index == "1"]
query_embedding = query_cell.obsm["X_scimilarity"]

# 搜索最近的邻居
k = 10
nn_idxs, nn_dists, results_metadata = cq.search_nearest(query_embedding, k=k)
print(results_metadata)

# 将 results_metadata 保存为 .pkl 文件
output_path = "/data/tyvek/results_metadata.pkl"  # 指定保存路径
with open(output_path, "wb") as f:
    pickle.dump(results_metadata, f)

print(f"results_metadata 已保存到 {output_path}")