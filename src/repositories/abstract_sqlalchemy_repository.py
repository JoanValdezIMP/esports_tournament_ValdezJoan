from .abstract_repository import AbstractRepository

class SqlAlchemyRepository(AbstractRepository[T, ID]):
    def __init__(self, unit_of_work: SqlAlchemyUnitOfWork, model_class: T):
        self.model_class = model_class

        self.session = unit_of_work.session
    
    def add(self, entity: T):
        self.session.add(entity)

    def get(self, entity_id: ID) -> Optional[T]:
        return self.session.get(self.model_class, entity_id)