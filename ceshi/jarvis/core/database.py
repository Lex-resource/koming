from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, ForeignKey, Index, BigInteger, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from datetime import datetime
import uuid
import json
from typing import Optional, List, Dict, Any, Generator
import os

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), default="新对话")
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "title": self.title,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trace_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    agent_name = Column(String(100), nullable=True)
    operation_type = Column(String(50), nullable=False)
    action = Column(String(200), nullable=True)
    details = Column(JSON, default={})
    result = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_audit_user_created", "user_id", "created_at"),
        Index("idx_audit_operation_created", "operation_type", "created_at"),
        Index("idx_audit_trace", "trace_id"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trace_id": str(self.trace_id) if self.trace_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "agent_name": self.agent_name,
            "operation_type": self.operation_type,
            "action": self.action,
            "details": self.details,
            "result": self.result,
            "duration": self.duration,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(String(100), unique=True, nullable=False)
    category = Column(String(100), nullable=False)
    source = Column(String(200), nullable=True)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_data_category_created", "category", "created_at"),
        Index("idx_data_source", "source"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "record_id": self.record_id,
            "category": self.category,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SystemState(Base):
    __tablename__ = "system_state"

    key = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Database:
    """PostgreSQL数据库管理"""

    def __init__(self, db_url: str = None):
        if db_url is None:
            db_url = os.getenv(
                "DATABASE_URL",
                f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@"
                f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'jarvis')}"
            )
        
        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def init_db(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator:
        """获取数据库会话的上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_user(self, username: str, email: str, metadata: Dict = None) -> User:
        """创建用户"""
        with self.get_session() as session:
            user = User(username=username, email=email, metadata=metadata or {})
            session.add(user)
            session.flush()
            return user.to_dict()

    def get_user(self, user_id: str = None, username: str = None) -> Optional[Dict]:
        """获取用户"""
        with self.get_session() as session:
            query = session.query(User)
            if user_id:
                query = query.filter(User.id == user_id)
            elif username:
                query = query.filter(User.username == username)
            else:
                return None
            user = query.first()
            return user.to_dict() if user else None

    def create_conversation(self, user_id: str, title: str = None, metadata: Dict = None) -> Dict:
        """创建对话"""
        with self.get_session() as session:
            conversation = Conversation(
                user_id=user_id,
                title=title or "新对话",
                metadata=metadata or {}
            )
            session.add(conversation)
            session.flush()
            return conversation.to_dict()

    def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """获取用户对话列表"""
        with self.get_session() as session:
            conversations = session.query(Conversation).filter(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()
            return [c.to_dict() for c in conversations]

    def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> Dict:
        """添加消息"""
        with self.get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            session.add(message)
            
            conversation = session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            session.flush()
            return message.to_dict()

    def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict]:
        """获取对话消息"""
        with self.get_session() as session:
            messages = session.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).limit(limit).all()
            return [m.to_dict() for m in messages]

    def add_audit_log(self, operation_type: str, user_id: str = None,
                      agent_name: str = None, action: str = None,
                      details: Dict = None, result: str = None,
                      duration: float = None) -> Dict:
        """添加审计日志"""
        with self.get_session() as session:
            trace_id = uuid.uuid4()
            audit_log = AuditLog(
                trace_id=trace_id,
                user_id=user_id,
                agent_name=agent_name,
                operation_type=operation_type,
                action=action,
                details=details or {},
                result=result[:500] if result else None,
                duration=duration
            )
            session.add(audit_log)
            session.flush()
            return audit_log.to_dict()

    def get_audit_logs(self, user_id: str = None, operation_type: str = None,
                       agent_name: str = None, limit: int = 100) -> List[Dict]:
        """查询审计日志"""
        with self.get_session() as session:
            query = session.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if operation_type:
                query = query.filter(AuditLog.operation_type == operation_type)
            if agent_name:
                query = query.filter(AuditLog.agent_name == agent_name)
            
            logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
            return [log.to_dict() for log in logs]

    def add_data_record(self, record_id: str, category: str, source: str,
                       content: Dict, metadata: Dict = None, tags: List[str] = None) -> Dict:
        """添加数据记录"""
        with self.get_session() as session:
            record = DataRecord(
                record_id=record_id,
                category=category,
                source=source,
                content=content,
                metadata=metadata or {},
                tags=tags or []
            )
            session.add(record)
            session.flush()
            return record.to_dict()

    def get_data_records(self, category: str = None, source: str = None,
                        limit: int = 100) -> List[Dict]:
        """查询数据记录"""
        with self.get_session() as session:
            query = session.query(DataRecord)
            
            if category:
                query = query.filter(DataRecord.category == category)
            if source:
                query = query.filter(DataRecord.source == source)
            
            records = query.order_by(DataRecord.created_at.desc()).limit(limit).all()
            return [r.to_dict() for r in records]

    def set_system_state(self, key: str, value: Any) -> None:
        """设置系统状态"""
        with self.get_session() as session:
            state = SystemState(key=key, value=value)
            session.merge(state)

    def get_system_state(self, key: str) -> Optional[Any]:
        """获取系统状态"""
        with self.get_session() as session:
            state = session.query(SystemState).filter(SystemState.key == key).first()
            return state.value if state else None

    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        with self.get_session() as session:
            return {
                "total_users": session.query(User).count(),
                "total_conversations": session.query(Conversation).count(),
                "total_messages": session.query(Message).count(),
                "total_audit_logs": session.query(AuditLog).count(),
                "total_data_records": session.query(DataRecord).count()
            }

    def vacuum(self):
        """清理数据库"""
        with self.engine.connect() as conn:
            conn.execute("VACUUM ANALYZE")


db = Database()
