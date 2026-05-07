from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, ForeignKey, Index, BigInteger, JSON, select, and_, or_, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import uuid
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
import os
import asyncio

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    title = Column(String(500), default="新对话")
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_conv_user_updated", "user_id", "updated_at"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), nullable=False, index=True)
    role = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_msg_conv_created", "conversation_id", "created_at"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trace_id = Column(String(36), default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), nullable=True, index=True)
    agent_name = Column(String(100), nullable=True, index=True)
    operation_type = Column(String(50), nullable=False, index=True)
    action = Column(String(200), nullable=True)
    details = Column(JSON, default={})
    result = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_audit_type_created", "operation_type", "created_at"),
        Index("idx_audit_agent_created", "agent_name", "created_at"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "trace_id": self.trace_id,
            "user_id": self.user_id,
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    record_id = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    source = Column(String(200), nullable=True, index=True)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_data_cat_source", "category", "source"),
    )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "record_id": self.record_id,
            "category": self.category,
            "source": self.source,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags or [],
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


class AsyncDatabase:
    """异步PostgreSQL数据库管理 - 单例模式"""
    
    _instance = None
    _init_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        db_url = os.getenv(
            "DATABASE_URL",
            f"postgresql+asyncpg://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'postgres')}@"
            f"{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'jarvis')}"
        )
        
        self.async_engine = create_async_engine(
            db_url,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        self.async_session = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._connection_retry_times = 3
        self._connection_retry_delay = 2.0

    async def init_db(self):
        """异步初始化数据库表"""
        for attempt in range(self._connection_retry_times):
            try:
                async with self.async_engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                print("✓ 数据库表初始化成功")
                return
            except Exception as e:
                if attempt < self._connection_retry_times - 1:
                    print(f"⚠️ 数据库初始化失败，{self._connection_retry_delay}秒后重试 ({attempt + 1}/{self._connection_retry_times})")
                    await asyncio.sleep(self._connection_retry_delay)
                else:
                    print(f"❌ 数据库初始化失败: {e}")
                    raise

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        for attempt in range(self._connection_retry_times):
            try:
                async with self.async_session() as session:
                    try:
                        yield session
                        await session.commit()
                    except Exception:
                        await session.rollback()
                        raise
            except Exception as e:
                if attempt < self._connection_retry_times - 1:
                    print(f"⚠️ 数据库连接失败，重试中 ({attempt + 1}/{self._connection_retry_times})")
                    await asyncio.sleep(self._connection_retry_delay)
                else:
                    raise ConnectionError(f"数据库连接失败，已重试{self._connection_retry_times}次: {e}")

    async def create_user(self, username: str, email: str, metadata: Dict = None) -> Dict:
        async with self.get_session() as session:
            user = User(username=username, email=email, metadata=metadata or {})
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user.to_dict()

    async def get_user(self, user_id: str = None, username: str = None) -> Optional[Dict]:
        async with self.get_session() as session:
            query = select(User)
            if user_id:
                query = query.where(User.id == user_id)
            elif username:
                query = query.where(User.username == username)
            else:
                return None
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user.to_dict() if user else None

    async def create_conversation(self, user_id: str, title: str = None, metadata: Dict = None) -> Dict:
        async with self.get_session() as session:
            conversation = Conversation(
                user_id=user_id,
                title=title or "新对话",
                metadata=metadata or {}
            )
            session.add(conversation)
            await session.flush()
            await session.refresh(conversation)
            return conversation.to_dict()

    async def get_conversations(self, user_id: str, limit: int = 50) -> List[Dict]:
        async with self.get_session() as session:
            query = (
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
            )
            result = await session.execute(query)
            return [c.to_dict() for c in result.scalars().all()]

    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> Dict:
        async with self.get_session() as session:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            session.add(message)
            
            query = select(Conversation).where(Conversation.id == conversation_id)
            result = await session.execute(query)
            conversation = result.scalar_one_or_none()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            await session.flush()
            await session.refresh(message)
            return message.to_dict()

    async def get_messages(self, conversation_id: str, limit: int = 100) -> List[Dict]:
        async with self.get_session() as session:
            query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
                .limit(limit)
            )
            result = await session.execute(query)
            return [m.to_dict() for m in result.scalars().all()]

    async def add_audit_log(self, operation_type: str, user_id: str = None,
                           agent_name: str = None, action: str = None,
                           details: Dict = None, result: str = None,
                           duration: float = None) -> Dict:
        async with self.get_session() as session:
            trace_id = str(uuid.uuid4())
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
            await session.flush()
            await session.refresh(audit_log)
            return audit_log.to_dict()

    async def get_audit_logs(self, user_id: str = None, operation_type: str = None,
                            agent_name: str = None, limit: int = 100) -> List[Dict]:
        async with self.get_session() as session:
            query = select(AuditLog)
            if user_id:
                query = query.where(AuditLog.user_id == user_id)
            if operation_type:
                query = query.where(AuditLog.operation_type == operation_type)
            if agent_name:
                query = query.where(AuditLog.agent_name == agent_name)
            
            query = query.order_by(AuditLog.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return [log.to_dict() for log in result.scalars().all()]

    async def add_data_record(self, record_id: str, category: str, source: str,
                           content: Dict, metadata: Dict = None, tags: List[str] = None) -> Dict:
        async with self.get_session() as session:
            record = DataRecord(
                record_id=record_id,
                category=category,
                source=source,
                content=content,
                metadata=metadata or {},
                tags=tags or []
            )
            session.add(record)
            await session.flush()
            await session.refresh(record)
            return record.to_dict()

    async def get_data_records(self, category: str = None, source: str = None,
                              limit: int = 100) -> List[Dict]:
        async with self.get_session() as session:
            query = select(DataRecord)
            if category:
                query = query.where(DataRecord.category == category)
            if source:
                query = query.where(DataRecord.source == source)
            
            query = query.order_by(DataRecord.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return [r.to_dict() for r in result.scalars().all()]

    async def set_system_state(self, key: str, value: Any) -> None:
        async with self.get_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(SystemState).where(SystemState.key == key)
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.value = value
            else:
                session.add(SystemState(key=key, value=value))

    async def get_system_state(self, key: str) -> Optional[Any]:
        async with self.get_session() as session:
            query = select(SystemState).where(SystemState.key == key)
            result = await session.execute(query)
            state = result.scalar_one_or_none()
            return state.value if state else None

    async def get_statistics(self) -> Dict[str, int]:
        async with self.get_session() as session:
            stats = {}
            for table_name, model in [
                ("users", User), ("conversations", Conversation),
                ("messages", Message), ("audit_logs", AuditLog),
                ("data_records", DataRecord)
            ]:
                query = select(func.count(model.id))
                result = await session.execute(query)
                stats[f"total_{table_name}"] = result.scalar() or 0
            return stats


db = AsyncDatabase()
