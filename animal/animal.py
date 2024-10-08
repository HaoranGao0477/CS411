from typing import Any, Optional

from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_management.migration import Migration
from wildlife_tracker.migration_management.migration_path import MigrationPath

class Animal:

    def __init__(self,
                animal_id: int,
                size: int,
                species: str,
                current_date: str,
                current_location: str,
                age: Optional[List[int]] = None,
                animals: Optional[List[int]] = None,
                health_status: Optional[str] = None) -> None:
        self.animal_id = animal_id
        self.current_date = current_date
        self.current_location = current_location
        self.size = size
        self.species = species
        self.age = age or None
        self.animals = animals or []
        self.health_status = health_status or []

    


    def get_animal_by_id(self,animal_id: int) -> Optional[Animal]:
        pass

    def get_animal_details(self, animal_id) -> dict[str, Any]:
        pass







