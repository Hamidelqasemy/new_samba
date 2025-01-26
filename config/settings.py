import os

class Config:
    SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB