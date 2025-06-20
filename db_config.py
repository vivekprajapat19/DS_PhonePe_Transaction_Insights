from sqlalchemy import create_engine

def db_connection():
    # 🔁 Replace these with your actual MySQL credentials
    username = "root"
    password = "*k123pr#"
    host = "localhost"
    database = "PhonePe_Transaction"

    connection_string = f"mysql+pymysql://{username}:{password}@{host}/{database}"
    engine = create_engine(connection_string)
    return engine
