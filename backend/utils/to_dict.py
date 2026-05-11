from sqlalchemy import inspect


def to_dict(obj, only=None):
        if only:
            return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs if c.key in only}
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}