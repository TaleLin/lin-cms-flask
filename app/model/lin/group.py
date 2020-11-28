from app.lin.model import Group as LinGroup, manager, db


class Group(LinGroup):
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
            .filter(
                manager.user_model.delete_time == None, manager.user_model.id == user_id
            )
        )
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        groups = result.all()
        return groups

    @classmethod
    def select_ids_by_user_id(cls, user_id) -> list:
        """
        根据用户ID，通过User-Group关联表，获取所属用户组的Id列表
        """
        query = (
            db.session.query(manager.user_group_model.group_id)
            .join(
                manager.user_model,
                manager.user_model.id == manager.user_group_model.user_id,
            )
            .filter(
                manager.user_model.delete_time == None, manager.user_model.id == user_id
            )
        )
        result = (
            db.session.query(cls.id)
            .filter(cls.delete_time == None)
            .filter(cls.id.in_(query))
        )
        # [(1,),(2,),...] => [1,2,...]
        group_ids = [x[0] for x in result.all()]
        return group_ids
