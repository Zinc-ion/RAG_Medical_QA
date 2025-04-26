# 禁用 wandb（Weights & Biases）的在线日志记录功能，避免联网记录训练信息
#export WANDB_MODE=disabled

# 指定训练数据的绝对路径，注意修改为实际文件路径
train_data="C://Users//PC//Desktop//learn_pytorch//LightRAG_QA_Sys//Finetune//data//train_data.jsonl"

# 设置训练超参数：训练轮数、每设备的批次大小、梯度累计步数以及分组大小（用于分组排序任务）
num_train_epochs=4
per_device_train_batch_size=16
gradient_accumulation_steps=2
train_group_size=11

# 指定使用的 GPU 数量（测试时设为 2）
num_gpus=1

# 如果环境变量 HF_HUB_CACHE 未设置，则将其设置为 Hugging Face Hub 的默认缓存目录
if [ -z "$HF_HUB_CACHE" ]; then
    export HF_HUB_CACHE="$HOME/.cache/huggingface/hub"
fi

# 定义模型参数，包括模型名称、缓存目录等
model_args="\
    --model_name_or_path BAAI/bge-reranker-v2-m3 \
    --cache_dir $HF_HUB_CACHE \
"

# 定义数据参数：训练数据路径、缓存路径、分组大小、查询和段落的最大长度、对齐选项以及是否使用知识蒸馏
data_args="\
    --train_data $train_data \
    --cache_path ~/.cache \
    --train_group_size $train_group_size \
    --query_max_len 256 \
    --passage_max_len 256 \
    --pad_to_multiple_of 8 \
    --knowledge_distillation False \
"

# 定义训练参数：输出目录、是否覆盖现有输出、学习率、是否启用 FP16 混合精度训练、训练轮数、批次大小、梯度累计、数据加载器参数、
# 预热比例、梯度检查点、权重衰减、使用 DeepSpeed 配置、日志记录及保存步数
training_args="\
    --output_dir ./test_encoder_only_base_bge-rerankerv2m3-base \
    --overwrite_output_dir \
    --learning_rate 6e-5 \
    --fp16 \
    --report_to wandb \
    --wandb_project LightRAG_Reranker \  # 新增项目名称设置
    --wandb_run_name ep-$num_train_epochs-bs-$per_device_train_batch_size-gas-$gradient_accumulation_steps \  # 新增运行名称设置
    --num_train_epochs $num_train_epochs \
    --per_device_train_batch_size $per_device_train_batch_size \
    --gradient_accumulation_steps $gradient_accumulation_steps \
    --dataloader_drop_last True \
    --warmup_ratio 0.1 \
    --gradient_checkpointing \
    --weight_decay 0.01 \
    --deepspeed C://Users//PC//Desktop//learn_pytorch//LightRAG_QA_Sys//FlagEmbedding//examples//finetune//ds_stage0.json \
    --logging_steps 1 \
    --save_steps 1000 \
"

# 构造最终的命令，使用 torchrun 启动多 GPU 训练，调用具体的训练脚本，并传入之前定义的模型、数据和训练参数
cmd="torchrun --nproc_per_node $num_gpus \
    -m FlagEmbedding.finetune.reranker.encoder_only.base \
    $model_args \
    $data_args \
    $training_args \
"

# 打印构造的命令，便于调试和检查参数设置
echo $cmd

# 执行命令，启动训练
eval $cmd
