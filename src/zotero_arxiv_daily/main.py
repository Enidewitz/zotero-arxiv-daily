import os
import sys
import logging
from omegaconf import DictConfig
import hydra
from loguru import logger
import dotenv
from zotero_arxiv_daily.executor import Executor

# 禁用 tokenizers 的并行处理
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 加载 .env 文件中的环境变量
dotenv.load_dotenv()

# ===== 在 Hydra 之前打印调试信息 =====
print("=" * 60)
print("INITIAL DEBUG - BEFORE HYDRA:")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# 检查配置文件
config_locations = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/default.yaml")),
    os.path.abspath("config/default.yaml"),
    os.path.abspath("../../config/default.yaml"),
    os.path.abspath("./config/default.yaml"),
]

print("\nChecking config file locations:")
for i, path in enumerate(config_locations):
    print(f"\nLocation {i+1}: {path}")
    print(f"  Exists: {os.path.exists(path)}")
    if os.path.exists(path):
        print(f"  Readable: {os.access(path, os.R_OK)}")
        try:
            print(f"  File size: {os.path.getsize(path)} bytes")
            with open(path, 'r') as f:
                content = f.read()
                print(f"  Content preview: {content[:200]}...")  # Preview the first 200 characters
        except Exception as e:
            print(f"  Error reading: {e}")

# 列出目录内容
print("\nListing directories:")
for dir_path in ['.', '..', '../..', 'config', './config', '../../config']:
    abs_dir = os.path.abspath(dir_path)
    if os.path.exists(abs_dir) and os.path.isdir(abs_dir):
        print(f"\nContents of {dir_path} ({abs_dir}):")
        try:
            files = os.listdir(abs_dir)
            for file in files[:10]:  # 只显示前10个文件
                file_path = os.path.join(abs_dir, file)
                file_type = "DIR" if os.path.isdir(file_path) else "FILE"
                print(f"  [{file_type}] {file}")
        except Exception as e:
            print(f"  Error listing: {e}")

print("=" * 60)
# ===== 调试信息结束 =====

@hydra.main(version_base=None, config_path="../../config", config_name="default")
def main(config: DictConfig):
    # 调试打印配置信息
    print(f"Debug mode: {config.executor.debug}")
    print(f"Executor source: {config.executor.source}")
    
    # Configure loguru log level based on config
    log_level = "DEBUG" if config.executor.debug else "INFO"
    logger.remove()  # 移除默认的日志处理器
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 设置其它日志器的级别
    for logger_name in logging.root.manager.loggerDict:
        if "zotero_arxiv_daily" in logger_name:
            continue
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # 如果启用了调试模式，则输出调试信息
    if config.executor.debug:
        logger.info("Debug mode is enabled")
    
    # 确保 executor.source 被正确加载
    source = config.executor.get("source", ["arxiv"])  # 设置默认值为 ['arxiv']
    logger.info(f"Executor source: {source}")
    
    # 初始化 Executor 对象并运行
    executor = Executor(config)
    executor.run()

if __name__ == '__main__':
    main()
