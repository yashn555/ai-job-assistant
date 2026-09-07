import os
import re
import uuid
import logging
import urllib.parse
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

logger = logging.getLogger("backend.database")
logging.basicConfig(level=logging.INFO)

# MongoDB Configuration
RAW_MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("DATABASE_URL", "")

def sanitize_mongo_uri(uri: str) -> str:
    if not uri or "<db_username>" in uri or "<db_password>" in uri:
        return uri
    try:
        if "://" in uri and "@" in uri:
            prefix, rest = uri.split("://", 1)
            last_at_idx = rest.rfind("@")
            auth_part = rest[:last_at_idx]
            host_part = rest[last_at_idx + 1:]
            
            if ":" in auth_part:
                user, pwd = auth_part.split(":", 1)
                user_clean = urllib.parse.unquote(user)
                pwd_clean = urllib.parse.unquote(pwd)
                user_encoded = urllib.parse.quote_plus(user_clean)
                pwd_encoded = urllib.parse.quote_plus(pwd_clean)
                return f"{prefix}://{user_encoded}:{pwd_encoded}@{host_part}"
    except Exception as e:
        logger.warning(f"Error sanitizing Mongo URI: {e}")
    return uri

MONGODB_URI = sanitize_mongo_uri(RAW_MONGODB_URI)

mongo_client = None
mongo_db = None
use_mongodb = False

# Base for declarative SQLAlchemy-style model definitions
Base = declarative_base()

def ensure_mongo_indexes():
    """Ensure indexes on all MongoDB collections."""
    if mongo_db is None:
        return
    try:
        def safe_index(collection, key, **kwargs):
            try:
                collection.create_index(key, **kwargs)
            except Exception:
                pass

        safe_index(mongo_db.users, "email", unique=True)
        safe_index(mongo_db.users, "id")
        safe_index(mongo_db.applications, "user_id")
        safe_index(mongo_db.applications, "id")
        safe_index(mongo_db.candidate_profile, "user_id", unique=True)
        safe_index(mongo_db.app_settings, "user_id", unique=True)
        safe_index(mongo_db.support_tickets, "user_id")
        logger.info("MongoDB Atlas indexes verified.")
    except Exception as idx_err:
        logger.warning(f"Mongo index creation notice: {idx_err}")

# Connect to MongoDB Atlas
if MONGODB_URI and not ("<db_username>" in MONGODB_URI or "<db_password>" in MONGODB_URI):
    try:
        import pymongo
        mongo_client = pymongo.MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        # Test connection ping
        mongo_client.admin.command('ping')
        
        # Extract default db name or default to job_assistant
        db_name = "job_assistant"
        try:
            parsed_db = MONGODB_URI.split("/")[-1].split("?")[0]
            if parsed_db:
                db_name = parsed_db
        except Exception:
            pass
        if not db_name or db_name.strip() == "":
            db_name = "job_assistant"

        mongo_db = mongo_client[db_name]
        use_mongodb = True
        logger.info(f"Successfully connected to MongoDB Atlas database: '{db_name}'")
        ensure_mongo_indexes()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {e}")
        use_mongodb = False
        mongo_client = None
        mongo_db = None
else:
    logger.warning("MongoDB URI is not configured or contains placeholder values.")


def _build_id_query_val(val: Any) -> Any:
    """Creates a query value matching both int and str representations of an ID."""
    if val is None:
        return None
    if isinstance(val, int):
        return {"$in": [val, str(val)]}
    if isinstance(val, str) and val.isdigit():
        return {"$in": [val, int(val)]}
    return val


# ==========================================
# MongoDB Session & Query Adapters
# ==========================================
class MongoQuery:
    def __init__(self, model_cls, mongo_db, session=None):
        self.model_cls = model_cls
        self.mongo_db = mongo_db
        self.session = session
        self.collection_name = getattr(model_cls, "__tablename__", model_cls.__name__.lower())
        self.collection = mongo_db[self.collection_name]
        self._filters: Dict[str, Any] = {}
        self._sort_field: Optional[str] = None
        self._sort_dir: int = 1

    def filter(self, *expressions):
        for expr in expressions:
            if hasattr(expr, "left") and hasattr(expr, "right"):
                col_name = getattr(expr.left, "name", str(expr.left).split(".")[-1])
                val = getattr(expr.right, "value", expr.right)
                op_name = getattr(expr.operator, "__name__", "")
                
                if op_name in ("eq", "__eq__", "equal_to", ""):
                    if col_name in ("id", "user_id"):
                        self._filters[col_name] = _build_id_query_val(val)
                    else:
                        self._filters[col_name] = val
                elif op_name in ("ne", "__ne__", "not_equal_to"):
                    self._filters[col_name] = {"$ne": val}
                elif op_name in ("in_", "in_op"):
                    self._filters[col_name] = {"$in": list(val) if isinstance(val, (list, tuple, set)) else [val]}
                else:
                    self._filters[col_name] = val
            elif isinstance(expr, dict):
                for k, v in expr.items():
                    if k in ("id", "user_id"):
                        self._filters[k] = _build_id_query_val(v)
                    else:
                        self._filters[k] = v
        return self

    def filter_by(self, **kwargs):
        for k, val in kwargs.items():
            if k in ("id", "user_id"):
                self._filters[k] = _build_id_query_val(val)
            else:
                self._filters[k] = val
        return self

    def order_by(self, expr):
        if hasattr(expr, "desc") or (hasattr(expr, "modifier") and "DESC" in str(expr)):
            col_name = getattr(expr, "element", expr)
            col_name = getattr(col_name, "name", str(col_name).split(".")[-1])
            self._sort_field = col_name
            self._sort_dir = -1
        else:
            col_name = getattr(expr, "name", str(expr).split(".")[-1])
            self._sort_field = col_name
            self._sort_dir = 1
        return self

    def _doc_to_model(self, doc: Optional[Dict[str, Any]]):
        if not doc:
            return None
        doc = dict(doc)
        if "_id" in doc:
            mongo_id = doc.pop("_id")
            if "id" not in doc or doc["id"] is None:
                doc["id"] = str(mongo_id)
        
        # Instantiate model object
        instance = self.model_cls()
        for k, v in doc.items():
            setattr(instance, k, v)
        
        # Automatically track loaded instance in session so modifications persist on db.commit()
        if self.session is not None:
            self.session.track(instance)
            
        return instance

    def first(self):
        cursor = self.collection.find(self._filters)
        if self._sort_field:
            cursor = cursor.sort(self._sort_field, self._sort_dir)
        doc = cursor.limit(1)
        docs = list(doc)
        return self._doc_to_model(docs[0]) if docs else None

    def all(self) -> List[Any]:
        cursor = self.collection.find(self._filters)
        if self._sort_field:
            cursor = cursor.sort(self._sort_field, self._sort_dir)
        return [self._doc_to_model(d) for d in cursor]


class MongoSession:
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db
        self._to_insert: List[Any] = []
        self._to_delete: List[Any] = []
        self._tracked_instances: List[Any] = []

    def track(self, instance):
        if instance not in self._tracked_instances and instance not in self._to_insert:
            self._tracked_instances.append(instance)

    def query(self, model_cls):
        return MongoQuery(model_cls, self.mongo_db, session=self)

    def add(self, instance):
        if instance not in self._to_insert:
            self._to_insert.append(instance)
        if instance in self._tracked_instances:
            self._tracked_instances.remove(instance)

    def delete(self, instance):
        if instance not in self._to_delete:
            self._to_delete.append(instance)
        if instance in self._to_insert:
            self._to_insert.remove(instance)
        if instance in self._tracked_instances:
            self._tracked_instances.remove(instance)

    def _persist_instance(self, instance):
        col_name = getattr(instance, "__tablename__", instance.__class__.__name__.lower())
        col = self.mongo_db[col_name]
        
        # Convert instance to dict
        data = {}
        for k, v in instance.__dict__.items():
            if not k.startswith("_"):
                data[k] = v
        
        # Auto-assign IDs if needed
        if col_name == "users":
            if "id" not in data or data["id"] is None:
                last_user = col.find_one(sort=[("id", -1)])
                last_id = last_user.get("id", 0) if (last_user and isinstance(last_user.get("id"), int)) else 0
                next_id = max(last_id, col.count_documents({})) + 1
                data["id"] = next_id
                instance.id = next_id
        elif col_name == "applications":
            if "id" not in data or data["id"] is None:
                data["id"] = str(uuid.uuid4())
                instance.id = data["id"]
        elif col_name in ("candidate_profile", "app_settings"):
            if "id" not in data or data["id"] is None:
                data["id"] = data.get("user_id", 1)
                instance.id = data["id"]
        else:
            if "id" not in data or data["id"] is None:
                last_doc = col.find_one(sort=[("id", -1)])
                last_id = last_doc.get("id", 0) if (last_doc and isinstance(last_doc.get("id"), int)) else 0
                next_id = max(last_id, col.count_documents({})) + 1
                data["id"] = next_id
                instance.id = next_id

        if "created_at" not in data or data["created_at"] is None:
            data["created_at"] = datetime.utcnow()
            instance.created_at = data["created_at"]

        # Persist by canonical unique keys to prevent duplicate overwrites or misses
        if col_name in ("candidate_profile", "app_settings") and "user_id" in data and data["user_id"] is not None:
            uid = data["user_id"]
            filter_query = {"user_id": _build_id_query_val(uid)}
            col.replace_one(filter_query, data, upsert=True)
        elif col_name == "users" and ("id" in data or "email" in data):
            if "id" in data and data["id"] is not None:
                uid = data["id"]
                filter_query = {"id": _build_id_query_val(uid)}
            elif "email" in data and data["email"]:
                filter_query = {"email": data["email"]}
            else:
                filter_query = {"_id": data.get("_id")}
            col.replace_one(filter_query, data, upsert=True)
        elif "id" in data and data["id"] is not None:
            filter_query = {"id": _build_id_query_val(data["id"])}
            col.replace_one(filter_query, data, upsert=True)
        else:
            col.insert_one(data)

    def commit(self):
        # Save explicitly added instances
        for instance in list(self._to_insert):
            self._persist_instance(instance)
            if instance not in self._tracked_instances:
                self._tracked_instances.append(instance)
        
        # Save modified tracked instances
        for instance in list(self._tracked_instances):
            self._persist_instance(instance)

        # Process deletions
        for instance in list(self._to_delete):
            col_name = getattr(instance, "__tablename__", instance.__class__.__name__.lower())
            col = self.mongo_db[col_name]
            inst_id = getattr(instance, "id", None)
            if inst_id is not None:
                col.delete_one({"id": _build_id_query_val(inst_id)})
            elif hasattr(instance, "user_id") and getattr(instance, "user_id") is not None:
                col.delete_many({"user_id": _build_id_query_val(getattr(instance, "user_id"))})

        self._to_insert.clear()
        self._to_delete.clear()

    def refresh(self, instance):
        col_name = getattr(instance, "__tablename__", instance.__class__.__name__.lower())
        col = self.mongo_db[col_name]
        doc = None
        if col_name in ("candidate_profile", "app_settings") and hasattr(instance, "user_id") and instance.user_id is not None:
            doc = col.find_one({"user_id": _build_id_query_val(instance.user_id)})
        elif hasattr(instance, "id") and instance.id is not None:
            doc = col.find_one({"id": _build_id_query_val(instance.id)})
        elif hasattr(instance, "email") and getattr(instance, "email"):
            doc = col.find_one({"email": instance.email})
            
        if doc:
            for k, v in doc.items():
                if k != "_id":
                    setattr(instance, k, v)

    def rollback(self):
        self._to_insert.clear()
        self._to_delete.clear()

    def close(self):
        self._to_insert.clear()
        self._to_delete.clear()


def get_db():
    if not (use_mongodb and mongo_db is not None):
        raise RuntimeError("MongoDB connection is not established. Please check MONGODB_URI in .env")
    session = MongoSession(mongo_db)
    try:
        yield session
    finally:
        session.close()


def is_mongodb_active() -> bool:
    return bool(use_mongodb and mongo_db is not None)


def get_mongodb_instance():
    return mongo_db if use_mongodb else None


def init_db():
    """Initializes MongoDB indexes."""
    if use_mongodb and mongo_db is not None:
        ensure_mongo_indexes()
