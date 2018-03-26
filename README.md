# Backend-task-weavedin

# Requirements
- MySQL
- pipenv `pip install pipenv`

# Setup
- `git clone https://github.com/dnpuneeth/Backend-task-weavedin`
- `cd Backend-task-weavedin`
- `vi config.py # Set Database, Username, Password`
- `./setup-db`
- ```py
    from config import session; import inventory; import models
    user = session.query(models.User).filter_by(id=1).one() if session.query(models.User).filter_by(id=1).count() > 0 else models.User(name="Puneeth"); im = inventory.InventoryManagement(session, user)
    item = im.add_item('Blue Jeans', 'Levis', 'Fashion', 'P-ABC123')
    variant = im.add_variant(item, 10, 10, 1, color="Red")
    im.edit_item(item, product_code='PX-ABC123')
    im.edit_variant(variant, color="Orange")
    im.user_log()
  ```