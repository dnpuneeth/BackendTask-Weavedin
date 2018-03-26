from datetime import datetime, date, time
from sqlalchemy.orm import joinedload
from models import User, Spec, Item, ItemSpec, Variant, VariantSpec, select, _get_datetime


class InventoryManagement:
    def __init__(self, session, user):
        self.user = user
        self.session = session
    
    def add_item(self, name, brand, category, product_code, **kwargs):
        item = Item(user=self.user)
        self.session.add(item)

        spec_names = {
            'name': name, 'brand': brand, 'category': category, 'product_code': product_code
        }
        spec_names.update(kwargs)
        spec_names = dict((k.lower(), v) for k,v in spec_names.items())

        specs = Spec.ensure(self.session, self.user, spec_names.keys())
        
        for (name, value) in spec_names.items():
            spec = select(specs, 'name', name)
            assert(spec is not None)
            item_spec = ItemSpec(item=item, spec=spec, value=value, user=self.user)
            self.session.add(item_spec)
        self.session.commit()
        return item

    def add_variant(self, item, cost_price, selling_price, quantity, **kwargs):
        variant = Variant(item=item, user=self.user)
        self.session.add(variant)
        spec_names = {
            'cost_price': cost_price, 'selling_price': selling_price, 'quantity': quantity
        }
        spec_names.update(kwargs)
        specs = Spec.ensure(self.session, self.user, spec_names.keys())

        for (name, value) in spec_names.items():
            spec = select(specs, 'name', name)
            assert(spec is not None)
            variant_spec = VariantSpec(variant=variant, spec=spec, value=value, user=self.user)
            self.session.add(variant_spec)

        self.session.commit()
        return variant

    def delete_variant(self, variant):
        self.session.delete(variant)
        self.session.commit()
        
    def edit_item(self, item, **kwargs):
        item_specs = item.item_specs
        specs = Spec.ensure(self.session, self.user, kwargs.keys())

        for (name, value) in kwargs.items():
            item_spec = select(item_specs, lambda x: x.spec.name, name)
            spec = select(specs, 'name', name)
            if item_spec is not None:
                if item_spec.value == value: continue
                item_spec.active = False
                item_spec.expired_at = _get_datetime()
            item_spec = ItemSpec(item=item, spec=spec, value=value, user=self.user)
            self.session.add(item_spec)
        self.session.commit()

    def edit_variant(self, variant1, **kwargs):
        variant_specs = variant1.variant_specs
        specs = Spec.ensure(self.session, self.user, kwargs.keys())
        
        for (name, value) in kwargs.items():
            variant_spec = select(variant_specs, lambda x: x.spec.name, name)
            spec = select(specs, 'name', name)
            if variant_spec is not None:
                if variant_spec.value == value: continue
                variant_spec.active = False
                variant_spec.expired_at = _get_datetime()
            new_variant_spec = VariantSpec(
                variant=variant1, spec=spec, value=value, user=self.user
            )
            self.session.add(new_variant_spec)
        self.session.commit()

    def add_spec(self, name):
        spec = Spec.Spec(name=name, user=self.user)
        self.session.add(spec)
        self.session.commit()

    def add_variant_spec(self, variant, spec, value):
        spec_val = variant_Spec.VariantSpec(variant=variant, spec=spec, value=value, user=self.user)
        self.session.add(spec_val)
        self.session.commit()

    def delete(self, type):
        try:
            self.session.delete(type)
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def user_log(self, user=None):
        expired_item_specs = self.session.query(ItemSpec).filter_by(
            active=False
        ).order_by(ItemSpec.expired_at.desc()).all()
        expired_variant_specs = self.session.query(VariantSpec).filter_by(
            active=False
        ).order_by(VariantSpec.expired_at.desc()).all()

        all_changes = expired_item_specs + expired_variant_specs
        all_changes = sorted(all_changes, key=lambda x: x.expired_at)
        FORMAT='| {0: <12} | {1: <19} | {2: <15} | {3: <15} |'
        print (FORMAT.format("Type", "Expired At", "Value", "User"))
        for change in all_changes:
            print (FORMAT.format(
                change.__class__.__name__, change.expired_at.isoformat(),
                change.value, change.user_id
            ))