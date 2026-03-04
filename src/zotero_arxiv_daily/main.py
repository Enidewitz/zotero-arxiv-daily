import os
import sys
import logging
from omegaconf import DictConfig
import hydra
from loguru import logger
import dotenv
from zotero_arxiv_daily.executor import Executor
os.environ["TOKENIZERS_PARALLELISM"] = "false"
dotenv.load_dotenv()

# ===== 在 Hydra 之前打印调试信息 =====
print("=" * 60)
print("INITIAL DEBUG - BEFORE HYDRA:")
print(f"Current working directory: {os.getcwd()}")
print(f"Script location: {__file__}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# 检查配置文件
config_locations = [
    # 绝对路径构建
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
                print(f"  Content preview: {content[:200]}...")
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
def main(config:DictConfig):
    # Configure loguru log level based on config
    log_level = "DEBUG" if config.executor.debug else "INFO"
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    for logger_name in logging.root.manager.loggerDict:
        if "zotero_arxiv_daily" in logger_name:
            continue
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    if config.executor.debug:
        logger.info("Debug mode is enabled")
    
    executor = Executor(config)
    executor.run()

if __name__ == '__main__':
    main()
