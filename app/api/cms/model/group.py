from lin import Group as LinGroup
from lin import db, manager


class Group(LinGroup):
    def _set_fields(self):
        self._exclude = ["delete_time", "create_time", "update_time", "is_deleted"]

    @classmethod
    def select_by_user_id(cls, user_id) -> list:
        """
        根据用户Id，通过User-Group关联表，获取所属用户组对象列表
        """
        query = (
            db.session.query(manager.user_group_model.group_id)
            .join(
                manager.user_model,
                manager.user_model.id == manager.user_group_model.user_id,
            )
            .filter(manager.user_model.delete_time == None, manager.user_model.id == user_id)
        )
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        groups = result.all()
        return groups
