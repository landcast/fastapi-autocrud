from contextlib import contextmanager
from datetime import datetime
import enum
from loguru import logger

from sqlalchemy import Column, String, Integer, DateTime, Float, Enum, event, text
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import CreateTable


Base = declarative_base()
metadata = Base.metadata


class DeleteEnum(enum.IntEnum):
    """
    Using enum.IntEnum instead of enum.Enum
    because this class instance will be used
    for json serialization, the enum.Enum
    not support json.dumps(obj)
    The start value should be from 1, not 0
    because generated mysql enum using
    1 as start value by default
    """
    IN_FORCE = 1
    DELETED = 2


class EntityMixin(object):
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, nullable=False) # for optimistic lock implementation
    delete_flag = Column(Enum(DeleteEnum), nullable=False,
                         server_default=DeleteEnum.IN_FORCE.name)
    created_at = Column(DateTime, nullable=False, default=datetime.now,
                        server_default=text('CURRENT_TIMESTAMP'),
                        comment='created time')
    updated_at = Column(DateTime, nullable=False, default=datetime.now,
                        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='last updated time', index=True)
    updated_by = Column(String(60), nullable=True,
                        comment='last updated operator name', index=True)
    
    __mapper_args__ = {
        "version_id_col": version_id
    }

    def to_dict(self):
        return model_to_dict(self)

    def from_dict(self, model_dict):
        return model_from_dict(self, model_dict)


class UserBaseMixin(EntityMixin):
    username = Column(String(60), nullable=False, unique=True,
                      comment='user provided unique name')
    password = Column(String(255), nullable=False,
                      comment='user provided password with cryption')
    mobile = Column(String(20), nullable=True,
                    comment='mobile no provided by user')
    telno = Column(String(40), nullable=True,
                   comment='tel no provided by user')
    email = Column(String(60), nullable=True,
                   comment='email address provided by user')
    gender = Column(Integer, nullable=True, comment='gender/sex')
    birth = Column(DateTime, nullable=True, comment='user birth date')
    avatar = Column(String(255), nullable=True, comment='user logo image url')
    lang = Column(String(20), nullable=True, comment='user language setting')
    verify_type = Column(String(20), nullable=True,
                        comment='user info verify type')
    nickname = Column(String(60), nullable=True, comment='user nick name')
    user_tag = Column(String(20), nullable=True, comment='user tag')
    last_login_ip = Column(String(20), nullable=True)
    last_login_time = Column(DateTime, nullable=True)
    last_login_device = Column(String(50), nullable=True)
    first_name = Column(String(50), nullable=True, comment='first name')
    last_name = Column(String(50), nullable=True, comment='last name')
    govtid_type = Column(Integer, nullable=True, 
                        comment='government identity type')
    govtid = Column(String(50), nullable=True, comment='government identity no')
    profession = Column(String(50), nullable=True)
    profile = Column(String(255), nullable=True, comment='self introduction')
    department = Column(String(255), nullable=True,
                        comment='belonging organization description')
    organization = Column(String(255), nullable=True,
                          comment='belonging organization description')
    home_address = Column(String(255), nullable=True)
    office_address = Column(String(255), nullable=True)
    location_lng = Column(Float, nullable=True,
                          comment='longitude value of GPS')
    location_lat = Column(Float, nullable=True, comment='latitude value of GPS')
    social_token = Column(String(255), nullable=True, comment='oauth token')
    im_token = Column(String(255), nullable=True,
                      comment='im saas services token')
    class_token = Column(String(255), nullable=True,
                         comment='class-room services user token')


class SystemUser(UserBaseMixin, Base):
    __tablename__ = 'system_user'
    id = Column(Integer, primary_key=True)


class ActionEventTypeEnum(enum.IntEnum):
    """
    UNKNOWN:未知
    TEACHER_CHECK:教师审核
    TEACHER_TALK:教师沟通
    STUDENT_TALK:学生沟通
    """
    UNKNOWN = 1
    TEACHER_CHECK = 2
    TEACHER_TALK = 3
    STUDENT_TALK = 4


class ActionEvent(EntityMixin, Base):
    __tablename__ = 'action_event'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, comment='用户')
    user_type = Column(String(150), nullable=False, comment='用户类型')
    action_event_type = Column(Enum(ActionEventTypeEnum), nullable=False,
                               server_default=ActionEventTypeEnum.UNKNOWN.name)
    action_event_desc = Column(String(2000), nullable=True, comment='事件内容')
    action_event_domain = Column(String(50), nullable=True,
                                 comment='事件所属业务领域')
    before_state = Column(String(120), nullable=True, comment='事件发生前状态')
    after_state = Column(String(120), nullable=True, comment='事件发生后状态')
    primary_table_name = Column(String(120), nullable=True,
                                comment='事件对应主数据表的名称')
    primary_data_id = Column(Integer, nullable=False, comment='事件对应主数据表的记录主键')
    remark = Column(String(1000), nullable=True, comment='标记信息')


if __name__ == "__main__":
    logger.info(CreateTable(SystemUser.__table__).compile(dialect=mysql.dialect()))