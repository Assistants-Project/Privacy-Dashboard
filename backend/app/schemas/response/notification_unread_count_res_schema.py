from ...extensions import ma


class NotificationUnreadCountResSchema(ma.Schema):
    unread_count = ma.Integer()
