import logging
from datetime import datetime
from starlette.requests import Request

# Cấu hình logger
logger = logging.getLogger("login_logger")
logger.setLevel(logging.INFO)

# Ghi vào file login_logs.txt
file_handler = logging.FileHandler("login_logs.txt")
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_login(email: str, request: Request, method: str = "manual"):
    ip = request.client.host if request.client else "unknown"
    message = f"[{method.upper()} LOGIN] Email: {email} | IP: {ip}"
    logger.info(message)
