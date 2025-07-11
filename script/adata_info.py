import os
import anndata
from pathlib import Path

# 输入和输出目录
input_dir = r"D:\Container\Download\Fdm\mouse"
output_dir = r"D:\Container\Download\Fdm\mouse_clean"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历输入目录中的所有.h5ad文件
for filename in os.listdir(input_dir):
    if filename.endswith(".h5ad"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        print(f"Processing: {filename}")

        # 读取h5ad文件
        adata = anndata.read_h5ad(input_path)

        # 检查var中是否有gene_name列
        if "gene_name" in adata.var.columns:
            # 将gene_name设置为var的索引
            adata.var.index = list(adata.var["gene_name"])
            print(f"  Set 'gene_name' as index for var")

            # 保存处理后的文件
            adata.write_h5ad(output_path)
            print(f"  Saved to: {output_path}")
        else:
            print(f"  Warning: 'gene_name' column not found in var, skipping modification")
            # 如果没有gene_name列，直接原样保存
            adata.write_h5ad(output_path)
            print(f"  Saved original file to: {output_path}")

print("All files processed!")