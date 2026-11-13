from dotenv import load_dotenv
import os 
load_dotenv()


NAMESPACE = os.getenv("NAMESPACE","test")
INDEX_NAME = os.getenv("INDEX_NAME","eshop")
DB_PASSWORD = os.getenv("DB_PASSWORD","test")
DB_NAME = os.getenv("DB_NAME","test")