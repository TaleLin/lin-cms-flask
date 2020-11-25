from app.lin.interface import UserIdentityInterface


class UserIdentity(InfoCrud):
    __tablename__ = 'lin_user_identity'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment='用户id')
    identity_type = Column(String(100), nullable=False)
    identifier = Column(String(100))
    credential = Column(String(100))
