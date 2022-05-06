from lin import GroupPermission as LinGroupPermission
from lin import db


class GroupPermission(LinGroupPermission):
    @classmethod
    def delete_batch_by_group_id_and_permission_ids(cls, group_id, permission_ids: list, commit=False):
        cls.query.filter_by(group_id=group_id).filter(cls.permission_id.in_(permission_ids)).delete(
            synchronize_session=False
        )
        if commit:
            db.session.commit()
