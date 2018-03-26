from datetime import datetime, date, time

import pytz
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


def _get_datetime():
    return datetime.utcnow()#.replace(tzinfo=pytz.utc)

def select(iterable, key, value):
    """Selects first object with attribute matching key and value"""
    if callable(key):
        return next((item for item in iterable if key(item) == value), None)
    else:
        return next((item for item in iterable if getattr(item, key) == value), None)

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key = True )
    name = Column(VARCHAR(20))
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)


class Spec(Base):
    __tablename__ = 'specs'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)

    user = relationship(User)


    @classmethod
    def ensure(cls, session, user, spec_names):
        """Ensures specs with the given name to be available in the database

        Args:
            session: (sqlalchemy.orm.session.Session) SQLAlchemy session object.
            user: (models.User) User performing the operation
            spec_names (:obj:`list` of :obj:`str`) List of spec names to be ensured.

        Returns:
            (:obj:`list` of :obj:`models.Spec`) List of specs.
        """
        specs = session.query(Spec).filter(Spec.name.in_(tuple(spec_names)))

        # Optimisation as most specs would eventually get created.
        if specs.count() == len(spec_names):
            return specs
        
        # Look for missing ones and create.
        for name in spec_names:
            if next((spec for spec in specs if spec.name == name), None) is None:
                session.add(Spec(name=name, user=user))
        session.commit()
        return specs  # Commit reloads specs


class Item(Base):
    __tablename__ = 'items'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)

    user = relationship(User)


class Variant(Base):
    __tablename__ = 'variants'
    __table_args__ = {'extend_existing':True}
    id = Column(Integer, primary_key = True )
    item_id = Column('item_id', Integer, ForeignKey(Item.id))
    #active = Column(Boolean, unique=False, default=True)
    item = relationship(Item, backref=backref(
        'variants', uselist=True, cascade='delete,all'
    ))
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)

    user = relationship(User)



class ItemSpec(Base):
    __tablename__ = 'item_specs'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key = True )
    value = Column(VARCHAR(20))
    active = Column(Boolean, unique=False, default=True)
    expired_at = Column(DATETIME)
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)

    item_id = Column('item_id', Integer, ForeignKey(Item.id))
    spec_id = Column('spec_id', Integer, ForeignKey(Spec.id))
    user_id = Column('user_id', Integer, ForeignKey(User.id))

    item = relationship(
        Item,
        backref=backref(
            'item_specs', uselist=True, cascade='delete,all',
            primaryjoin="and_(Item.id==ItemSpec.item_id, ItemSpec.active==1)"
        )
    )
    spec = relationship(Spec, lazy='joined')
    user = relationship(User)


class VariantSpec(Base):
    __tablename__ = 'variant_specs'
    __table_args__ = {'extend_existing':True}
    
    id = Column(Integer, primary_key = True )
    value = Column(VARCHAR(20))
    active = Column(Boolean, unique=False, default=True)
    expired_at = Column(DATETIME)
    created_at = Column(DATETIME, default=_get_datetime)
    updated_at = Column(DATETIME, onupdate=_get_datetime)

    variant_id = Column('variant_id', Integer, ForeignKey(Variant.id))
    spec_id = Column('spec_id', Integer, ForeignKey(Spec.id))
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    
    variant = relationship(
        Variant,
        backref=backref(
            'variant_specs', uselist=True, cascade='delete,all',
            primaryjoin="and_(Variant.id==VariantSpec.variant_id, VariantSpec.active==1)"
        )
    )
    spec = relationship(Spec, lazy='joined')
    user = relationship(User)
