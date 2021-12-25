from datetime import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, \
    Integer, String, DateTime, Boolean, ForeignKey, Float, extract, BigInteger
from sqlalchemy.orm import mapper, sessionmaker


class Database:
    """Database"""

    class User:
        """Table User"""

        def __init__(self, user_id, is_active=True):
            self.id = None
            self.user_id = user_id
            self.is_active = is_active

    class Profile:
        """Table Profile"""

        def __init__(self, user_id, first_name, last_name, position,
                     number=None, created=None, is_active=True,
                     is_staff=False):
            self.id = None
            self.user_id = user_id
            self.first_name = first_name
            self.last_name = last_name
            self.position = position
            self.number = number
            self.created = created
            self.is_active = is_active
            self.is_staff = is_staff

    class WorkShop:
        """Table Workshop"""

        def __init__(self, name, description, is_active=True):
            self.id = None
            self.name = name
            self.description = description
            self.is_active = is_active

    class Product:
        """Table Product"""

        def __init__(self, product_name, is_active=True):
            self.id = None
            self.product_name = product_name
            self.is_active = is_active

    class Operation:
        """Table Operation"""

        def __init__(
                self, operation_name, workshop_id, product_id, price,
                is_active=True):
            self.id = None
            self.operation_name = operation_name
            self.workshop_id = workshop_id
            self.product_id = product_id
            self.price = price
            self.is_active = is_active

    class Instruction:
        """Table for instructions"""

        def __init__(self, instruction_name, url, is_active=True):
            self.id = None
            self.instruction_name = instruction_name
            self.url = url
            self.is_active = is_active

    class Work:
        """Table Work"""

        def __init__(
                self, w_user_id, w_workshop, w_product, w_operation,
                w_price, w_active, w_quantity
        ):
            self.id = None
            self.w_user_id = w_user_id
            self.w_workshop = w_workshop
            self.w_product = w_product
            self.w_operation = w_operation
            self.w_price = w_price
            self.w_active = w_active
            self.w_quantity = w_quantity

    def __init__(self):
        # self.database_engine = create_engine(
        #     f'sqlite:///database/sqlite.db3',
        #     echo=False, pool_recycle=7200,
        #     connect_args={'check_same_thread': False}
        # )
        self.database_engine = create_engine(
            'mysql+pymysql://root:123456@127.0.0.1/mydb',
            echo=False, pool_recycle=7200
        )
        self.database_engine.connect()
        self.metadata = MetaData()

        user = Table(
            'user', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', BigInteger, unique=True),
            Column('is_active', Boolean, default=True),
        )

        profile = Table(
            'profile', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user_id', ForeignKey('user.user_id'), unique=True),
            Column('first_name', String(64)),
            Column('last_name', String(64)),
            Column('position', String(64)),
            Column('number', String(32)),
            Column('created', DateTime, default=datetime.now),
            Column('is_active', Boolean, default=True),
            Column('is_staff', Boolean, default=False)
        )

        workshop = Table(
            'workshop', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(128), unique=True),
            Column('description', String(256), nullable=True),
            Column('is_active', Boolean, default=True)
        )

        product = Table(
            'product', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('product_name', String(128), unique=True),
            Column('is_active', Boolean, default=True)
        )

        operation = Table(
            'operation', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('operation_name', String(128), unique=False),
            Column('workshop_id', ForeignKey('workshop.id')),
            Column('product_id', ForeignKey('product.id')),
            Column('price', Float),
            Column('is_active', Boolean, default=True)
        )

        instruction = Table(
            'instruction', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('instruction_name', String(128)),
            Column('url', String(512)),
            Column('is_active', Boolean, default=True),
        )

        work = Table(
            'work', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('w_user_id', ForeignKey('profile.user_id'), index=True),
            Column('w_workshop', String(128)),
            Column('w_product', String(128)),
            Column('w_operation', String(128)),
            Column('w_price', Float),
            Column('w_active', Boolean, default=True),
            Column('w_quantity', Integer, nullable=True),
            Column('w_start_datetime', DateTime, default=datetime.now),
            Column('w_stop_datetime', DateTime, default=datetime.now),
        )

        self.metadata.create_all(self.database_engine)

        mapper(self.User, user)
        mapper(self.Profile, profile)
        mapper(self.WorkShop, workshop)
        mapper(self.Product, product)
        mapper(self.Operation, operation)
        mapper(self.Work, work)
        mapper(self.Instruction, instruction)

        session = sessionmaker(bind=self.database_engine)
        self.session = session()

    # Work
    def get_work_data(self, user_id, month, year):
        """Get data work"""
        data_work = [data_work._asdict() for data_work in self.session.query(
            self.Work.w_user_id, self.Work.w_workshop,
            self.Work.w_product, self.Work.w_operation,
            self.Work.w_price, self.Work.w_quantity,
        ).filter_by(w_active=False).filter_by(w_user_id=user_id).filter(
            extract('month', self.Work.w_stop_datetime) == month).filter(
            extract('year', self.Work.w_stop_datetime) == year)]
        return data_work

    def add_work(self, user_id, workshop, product, operation, price, active,
                 quantity=None):
        """Add work"""
        if not self.session.query(self.Work).filter_by(
                w_user_id=user_id).filter_by(w_active=True).count():
            work_row = self.Work(user_id, workshop, product, operation, price,
                                 active, quantity)
            self.session.add(work_row)
        else:
            self.session.query(self.Work).filter_by(
                w_user_id=user_id).filter_by(w_active=True).update(
                {
                    self.Work.w_active: False,
                    self.Work.w_quantity: quantity,
                    self.Work.w_stop_datetime: datetime.now(),
                }, synchronize_session=False
            )
        self.session.commit()

    def check_work_active(self, user_id):
        """Check work active"""
        if self.session.query(self.Work).filter_by(
                w_user_id=user_id).filter_by(w_active=True).count():
            return True
        return False

    def get_work(self, user_id):
        """Get work"""
        work = [work._asdict() for work in self.session.query(
            self.Work.id, self.Work.w_user_id, self.Work.w_workshop,
            self.Work.w_product, self.Work.w_operation, self.Work.w_price,
        ).filter_by(w_user_id=user_id).filter_by(w_active=True)]
        return work[0]

    def get_salary(self, user_id, year, month, day=None):
        """Get salary"""
        result = 0
        if day:
            data = [salary._asdict() for salary in self.session.query(
                self.Work.w_price, self.Work.w_quantity,
            ).filter_by(w_active=False).filter_by(w_user_id=user_id).filter(
                extract('month', self.Work.w_stop_datetime) == month).filter(
                extract('year', self.Work.w_stop_datetime) == year).filter(
                extract('day', self.Work.w_stop_datetime) == day)]
        else:
            data = [salary._asdict() for salary in self.session.query(
                self.Work.w_price, self.Work.w_quantity,
            ).filter_by(w_active=False).filter_by(w_user_id=user_id).filter(
                extract('month', self.Work.w_stop_datetime) == month).filter(
                extract('year', self.Work.w_stop_datetime) == year)]
        for salary in data:
            result += salary['w_price'] * salary['w_quantity']
        return '%.2f' % result

    # User and Profile
    def add_user(self, user_id):
        """Add user in database"""
        if not self.session.query(self.User).filter_by(
                user_id=user_id).count():
            user_row = self.User(user_id)
            self.session.add(user_row)
            self.session.commit()
            return True
        return False

    def add_profile(self, user_id, first_name, last_name, position, number,
                    is_staff=False):
        """Add profile in database"""
        if not self.session.query(self.Profile).filter_by(
                user_id=user_id).count():
            profile = self.Profile(user_id=user_id,
                                   first_name=first_name,
                                   last_name=last_name,
                                   position=position,
                                   number=number,
                                   is_active=True,
                                   is_staff=is_staff)
            self.session.add(profile)
        else:
            self.session.query(self.Profile).filter_by(
                user_id=user_id).update(
                {
                    self.Profile.first_name: first_name,
                    self.Profile.last_name: last_name,
                    self.Profile.position: position,
                    self.Profile.number: number
                }, synchronize_session=False
            )
        self.session.commit()

    def del_profile(self, user_id):
        """Delete profile and user"""
        delete_user = self.session.query(self.Profile).filter_by(
            user_id=user_id).update(
            {self.Profile.is_active: False}, synchronize_session=False
        )
        self.session.commit()
        return delete_user

    def recovery_profile(self, user_id):
        """Recovery profile"""
        recovery_profile = self.session.query(self.Profile).filter_by(
            user_id=user_id).filter_by(is_active=False).update(
            {self.Profile.is_active: True}, synchronize_session=False
        )
        self.session.commit()
        return recovery_profile

    def check_user(self, user_id):
        """Check user in database"""
        if self.session.query(self.Profile).filter_by(
                is_active=True).filter_by(user_id=user_id).count():
            return False
        return True

    def check_old_user(self, user_id):
        """Check old user in database"""
        if self.session.query(self.Profile).filter_by(
                user_id=user_id).filter_by(is_active=False).count():
            return True
        return False

    def check_user_register(self, user_id):
        """Check user register"""
        if self.session.query(self.User).filter_by(
                user_id=user_id).count():
            return True
        return False

    def get_profile(self, user_id, is_active=False):
        """Get profile"""
        profile = [profile._asdict() for profile in self.session.query(
            self.Profile.id, self.Profile.user_id, self.Profile.first_name,
            self.Profile.last_name, self.Profile.position
        ).filter_by(is_staff=False).filter_by(is_active=is_active).filter_by(
            user_id=user_id
        )]
        return profile[0]

    def get_profiles(self, limit=False, yet=0, next=False, list_id=False):
        """Get list profiles"""
        if next and list_id:
            profiles = [profile._asdict() for profile in self.session.query(
                self.Profile.id, self.Profile.user_id, self.Profile.first_name,
                self.Profile.last_name, self.Profile.position,
                self.Profile.number
            ).filter_by(is_staff=False).filter_by(is_active=True).where(
                self.Profile.id >= list_id[0]).where(
                self.Profile.id > yet).limit(limit)]
        else:
            profiles = [profile._asdict() for profile in self.session.query(
                self.Profile.id, self.Profile.user_id, self.Profile.first_name,
                self.Profile.last_name, self.Profile.position,
                self.Profile.number
            ).filter_by(is_staff=False).filter_by(is_active=True).where(
                self.Profile.id > yet).limit(limit)]
        return profiles

    def len_profiles(self):
        """Len profiles"""
        profiles = [profile._asdict() for profile in self.session.query(
            self.Profile.id).filter_by(is_staff=False).filter_by(
            is_active=True)]
        return len(profiles)

    # Workshop
    def check_workshop(self, name, edit=False):
        """Check workshop in database"""
        if edit:
            return True
        elif self.session.query(self.WorkShop).filter_by(
                is_active=True).filter_by(name=name).count():
            return False
        return True

    def check_old_workshop(self, name):
        """Check old workshop in database"""
        if self.session.query(self.WorkShop).filter_by(
                name=name).filter_by(is_active=False).count():
            return True
        return False

    def get_workshop(self, name, is_active=False):
        """Get workshop"""
        workshop = [workshop._asdict() for workshop in self.session.query(
            self.WorkShop.id, self.WorkShop.name, self.WorkShop.description
        ).filter_by(is_active=is_active).filter_by(name=name)]
        return workshop[0]

    def get_workshops(self, limit=False, yet=0, next=False, list_id=False):
        """Get list workshops"""
        if next and list_id:
            workshops = [workshop._asdict() for workshop in self.session.query(
                self.WorkShop.id, self.WorkShop.name, self.WorkShop.description
            ).filter_by(is_active=True).where(
                self.WorkShop.id >= list_id[0]).where(
                self.WorkShop.id > yet).limit(limit)]
        else:
            workshops = [workshop._asdict() for workshop in self.session.query(
                self.WorkShop.id, self.WorkShop.name, self.WorkShop.description
            ).filter_by(is_active=True).where(self.WorkShop.id > yet).limit(
                limit)]
        return workshops

    def len_workshops(self):
        """Len workshops"""
        workshops = [workshop._asdict() for workshop in self.session.query(
            self.WorkShop.id).filter_by(is_active=True)]
        return len(workshops)

    def get_workshops_active(self, name):
        """Check workshop is_active"""
        result = []
        workshops = [workshop._asdict() for workshop in self.session.query(
            self.WorkShop.name).filter_by(is_active=True)]
        for workshop in workshops:
            if workshop['name'] != name:
                result.append(workshop['name'])
        return result

    def del_workshop(self, name):
        """Delete workshop"""
        delete_workshop = self.session.query(self.WorkShop).filter_by(
            name=name).update(
            {self.WorkShop.is_active: False}, synchronize_session=False
        )
        self.session.commit()
        return delete_workshop

    def recovery_workshop(self, name):
        """Recovery workshop"""
        recovery_workshop = self.session.query(self.WorkShop).filter_by(
            name=name).filter_by(is_active=False).update(
            {self.WorkShop.is_active: True}, synchronize_session=False
        )
        self.session.commit()
        return recovery_workshop

    def add_workshop(self, name, description):
        """Add workshop in database"""
        if not self.session.query(self.WorkShop).filter_by(
                name=name).count():
            workshop = self.WorkShop(name, description)
            self.session.add(workshop)
            self.session.commit()

    def edit_workshop(self, id, name, description):
        """Edit workshop in database"""
        if self.session.query(self.WorkShop).filter_by(
                id=id).count():
            self.session.query(self.WorkShop).filter_by(
                id=id).update(
                {
                    self.WorkShop.name: name,
                    self.WorkShop.description: description,
                    self.WorkShop.is_active: True
                }, synchronize_session=False
            )
            self.session.commit()

    # Products
    def get_products(self, limit=False, yet=0, next=False, list_id=False):
        """Get products in database"""
        if next and list_id:
            products = [product._asdict() for product in self.session.query(
                self.Product.id, self.Product.product_name
            ).filter_by(is_active=True).where(
                self.Product.id >= list_id[0]).limit(limit)]
        else:
            products = [product._asdict() for product in self.session.query(
                self.Product.id, self.Product.product_name
            ).filter_by(is_active=True).where(self.Product.id > yet).limit(
                limit)]
        return products

    def len_products(self):
        """Len products"""
        products = [product._asdict() for product in self.session.query(
            self.Product.id).filter_by(is_active=True)]
        return len(products)

    def get_product(self, product_name, is_active=False):
        """Get product in database"""
        product = [product._asdict() for product in self.session.query(
            self.Product.id, self.Product.product_name
        ).filter_by(is_active=is_active).filter_by(product_name=product_name)]
        return product[0]

    def get_products_active(self, product_name):
        """Check product is_active"""
        result = []
        products = [product._asdict() for product in self.session.query(
            self.Product.product_name).filter_by(is_active=True)]
        for product in products:
            if product['product_name'] != product_name:
                result.append(product['product_name'])
        return result

    def recovery_product(self, product_name):
        """Recovery product"""
        recovery_product = self.session.query(self.Product).filter_by(
            product_name=product_name).filter_by(is_active=False).update(
            {self.Product.is_active: True}, synchronize_session=False
        )
        self.session.commit()
        return recovery_product

    def check_product(self, product_name, edit=False):
        """Check product in database"""
        if edit:
            return True
        elif self.session.query(self.Product).filter_by(
                is_active=True).filter_by(product_name=product_name).count():
            return False
        return True

    def check_old_product(self, product_name):
        """Check old product in database"""
        if self.session.query(self.Product).filter_by(
                product_name=product_name).filter_by(is_active=False).count():
            return True
        return False

    def add_product(self, id, product_name, edit=False):
        """Add or edit product in database"""
        if not self.session.query(self.Product).filter_by(
                id=id).count() and not edit:
            product = self.Product(product_name)
            self.session.add(product)
        elif self.session.query(self.Product).filter_by(
                id=id).count() and edit:
            self.session.query(self.Product).filter_by(
                id=id).update(
                {
                    self.Product.product_name: product_name,
                    self.Product.is_active: True
                }, synchronize_session=False
            )
        self.session.commit()

    def del_product(self, product_name):
        """Delete product in database"""
        delete_product = self.session.query(self.Product).filter_by(
            product_name=product_name).update(
            {self.Product.is_active: False}, synchronize_session=False
        )
        self.session.commit()
        return delete_product

    # Operations
    def get_operations(self):
        """Get list operations"""
        operations = [operation._asdict() for operation in
                      self.session.query(
                          self.Operation.id, self.Operation.operation_name,
                          self.WorkShop.name,
                          self.Product.product_name, self.Operation.price
                      ).filter_by(is_active=True).join(
                          self.Product).filter_by(
                          is_active=True).join(self.WorkShop).filter_by(
                          is_active=True)]
        return operations

    def get_operations_yet(
            self, product, limit=False, yet=0, next=False, list_id=False):
        """Get operations yet"""
        if next and list_id:
            operations = [operation._asdict() for operation in
                          self.session.query(
                              self.Operation.id, self.Operation.operation_name,
                              self.WorkShop.name,
                              self.Product.product_name, self.Operation.price
                          ).filter_by(is_active=True).join(
                              self.Product).filter_by(
                              is_active=True).filter_by(
                              product_name=product).join(
                              self.WorkShop).filter_by(is_active=True).where(
                              self.Operation.id >= list_id[0]).limit(limit)]
        else:
            operations = [operation._asdict() for operation in
                          self.session.query(
                              self.Operation.id, self.Operation.operation_name,
                              self.WorkShop.name,
                              self.Product.product_name, self.Operation.price
                          ).filter_by(is_active=True).join(
                              self.Product).filter_by(
                              is_active=True).filter_by(
                              product_name=product).join(
                              self.WorkShop).filter_by(is_active=True).where(
                              self.Operation.id > yet).limit(limit)]
        return operations

    def search_operations(self, product, limit=False, yet=0, next=False,
                          list_id=False):
        """Search operations (product)"""
        operations = [operation._asdict() for operation in self.session.query(
            self.Operation.id, self.Operation.operation_name,
            self.WorkShop.name,
            self.Product.product_name, self.Operation.price
        ).filter_by(is_active=True).join(self.Product).filter_by(
            is_active=True).filter_by(product_name=product).join(
            self.WorkShop).filter_by(is_active=True).where(
            self.Operation.id > yet).limit(limit)]
        return operations

    def get_operations_keyboard(self, workshop_id, product_id):
        """Get list operations for keyboard"""
        operations = [operation._asdict() for operation in self.session.query(
            self.Operation.id, self.Operation.operation_name,
            self.WorkShop.name,
            self.Product.product_name, self.Operation.price
        ).filter_by(is_active=True).filter_by(
            workshop_id=workshop_id).filter_by(
            product_id=product_id).join(self.Product, self.WorkShop)]
        return operations

    def get_operation_check(self, workshop_id, product_id, operation_name,
                            ):
        """Check operation"""
        if self.session.query(self.Operation).filter_by(
                workshop_id=workshop_id).filter_by(
            product_id=product_id).filter_by(
            operation_name=operation_name).count():
            return True
        return False

    def get_operation(self, id, is_active=False):
        """Get operation"""
        operation = [operation._asdict() for operation in self.session.query(
            self.Operation.id, self.Operation.operation_name,
            self.WorkShop.name, self.Product.product_name,
            self.Operation.price).filter_by(
            is_active=is_active).filter_by(id=id).join(
            self.Product, self.WorkShop)]
        return operation[0]

    def get_operation_active(self, operation_name):
        """Check operation is_active"""
        result = []
        result_dict = {}
        operations = [operation._asdict() for operation in self.session.query(
            self.Operation.operation_name, self.WorkShop.name,
            self.Product.product_name).filter_by(is_active=True).join(
            self.WorkShop, self.Product
        )]
        for operation in operations:
            result_dict[operation['operation_name']] = [operation['name'],
                                                        operation[
                                                            'product_name']]
            if result_dict != operation_name:
                result.append(result_dict)
            result_dict = {}
        return result

    def get_operation_name(
            self, operation_name, workshop_id, product_id, is_active=False):
        """Get operation (name)"""
        operation = [operation._asdict() for operation in self.session.query(
            self.Operation.id, self.Operation.operation_name,
            self.WorkShop.name, self.Product.product_name,
            self.Operation.price).filter_by(
            is_active=is_active).filter_by(
            operation_name=operation_name).filter_by(
            workshop_id=workshop_id).filter_by(product_id=product_id).join(
            self.Product, self.WorkShop)]
        return operation[0]

    def del_operation(self, id):
        """Delete operation"""
        delete_operation = self.session.query(self.Operation).filter_by(
            id=id).update(
            {self.Operation.is_active: False}, synchronize_session=False
        )
        self.session.commit()
        return delete_operation

    def recovery_operation(self, id):
        """Recovery operation"""
        recovery_operation = self.session.query(self.Operation).filter_by(
            id=id).filter_by(is_active=False).update(
            {self.Operation.is_active: True}, synchronize_session=False
        )
        self.session.commit()
        return recovery_operation

    def check_operation(
            self, operation_name, workshop_id, product_id, edit=False):
        """Check workshop in database"""
        if edit:
            return True
        elif self.session.query(self.Operation).filter_by(
                is_active=True).filter_by(
            operation_name=operation_name).filter_by(
            workshop_id=workshop_id).filter_by(product_id=product_id).count():
            return False
        return True

    def check_old_operation(self,
                            operation_name, workshop_id, product_id):
        """Check old operation in database"""
        if self.session.query(self.Operation).filter_by(
                operation_name=operation_name).filter_by(
            workshop_id=workshop_id).filter_by(
            product_id=product_id
        ).filter_by(is_active=False).count():
            return True
        return False

    def add_operation(
            self, id, operation_name, workshop_id, product_id,
            price, edit=False):
        """Add or edit operation in database"""
        if not self.session.query(self.Operation).filter_by(
                id=id).count() and not edit:
            operation = self.Operation(
                operation_name, workshop_id, product_id, price)
            self.session.add(operation)
        elif self.session.query(self.Operation).filter_by(
                id=id).count() and edit:
            self.session.query(self.Operation).filter_by(
                id=id).update(
                {
                    self.Operation.operation_name: operation_name,
                    self.Operation.workshop_id: workshop_id,
                    self.Operation.product_id: product_id,
                    self.Operation.price: price,
                    self.Operation.is_active: True
                }, synchronize_session=False
            )
        self.session.commit()

    # Instruction
    def get_instructions(self, limit=False, yet=0, next=False, list_id=False):
        """Get list instruction"""
        if next and list_id:
            instruction = [instruction._asdict() for instruction in
                           self.session.query(
                               self.Instruction.id,
                               self.Instruction.instruction_name,
                               self.Instruction.url,
                           ).filter_by(is_active=True).where(
                               self.Instruction.id >= list_id[0]).limit(limit)]
        else:
            instruction = [instruction._asdict() for instruction in
                           self.session.query(
                               self.Instruction.id,
                               self.Instruction.instruction_name,
                               self.Instruction.url,
                           ).filter_by(is_active=True).where(
                               self.Instruction.id > yet).limit(limit)]
        return instruction

    def len_instructions(self):
        """Len instructions"""
        instruction = [instruction._asdict() for instruction in
                       self.session.query(
                           self.Instruction.id,
                       ).filter_by(is_active=True)]
        return len(instruction)

    def get_instruction(self, url, is_active=False):
        """Get product in database"""
        instruction = [instruction._asdict() for instruction in
                       self.session.query(
                           self.Instruction.id,
                           self.Instruction.instruction_name,
                           self.Instruction.url
                       ).filter_by(is_active=is_active).filter_by(url=url)]
        return instruction[0]

    def add_instruction(self, instruction_name, url, edit=False, old_url=None):
        """Add or edit instruction in database"""
        if not self.session.query(self.Instruction).filter_by(
                url=url).count() and not edit:
            instruction = self.Instruction(instruction_name, url)
            self.session.add(instruction)
        elif self.session.query(self.Instruction).filter_by(
                url=old_url).count() and edit:
            self.session.query(self.Instruction).filter_by(
                url=old_url).update(
                {
                    self.Instruction.instruction_name: instruction_name,
                    self.Instruction.url: url,
                    self.Instruction.is_active: True,
                }, synchronize_session=False
            )
        self.session.commit()

    def instruction_edit_name(self, old_url, instruction_name):
        """Instruction edit name"""
        if self.session.query(self.Instruction).filter_by(
                url=old_url).count():
            self.session.query(self.Instruction).filter_by(
                url=old_url).update(
                {
                    self.Instruction.instruction_name: instruction_name,
                    self.Instruction.is_active: True,
                }, synchronize_session=False
            )
        self.session.commit()

    def check_instruction_name(self, instruction_name, is_active=True):
        """Check instruction name"""
        if self.session.query(self.Instruction).filter_by(
                is_active=is_active).filter_by(
            instruction_name=instruction_name).count():
            return False
        return True

    def check_instruction_url(self, url, is_active=True):
        """Check instruction url"""
        if self.session.query(self.Instruction).filter_by(
                is_active=is_active).filter_by(url=url).count():
            return False
        return True

    def del_instruction(self, url):
        """Delete instruction"""
        delete_instruction = self.session.query(self.Instruction).filter_by(
            url=url).update(
            {self.Instruction.is_active: False}, synchronize_session=False
        )
        self.session.commit()
        return delete_instruction

    def recovery_instruction(self, url):
        """Recovery instruction"""
        recovery_instruction = self.session.query(self.Instruction).filter_by(
            url=url).filter_by(is_active=False).update(
            {self.Instruction.is_active: True}, synchronize_session=False
        )
        self.session.commit()
        return recovery_instruction


if __name__ == '__main__':
    test_db = Database()
