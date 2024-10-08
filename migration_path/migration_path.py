from typing import Optional

from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_management.migration import Migration
from wildlife_tracker.migration_management.migration_path import MigrationPath

class MigrationPath:
    def __init__(self,
                migration_path: MigrationPath
                start_date: str
                start_location: Habitat
                destination: Habitat
                status: str = "Scheduled"
                duration: Optional[int] = None)
        self.migration_path = migration_path
        self.start_date= start_date
        self.start_location = start_location
        self.destination = destination
        self.status = status
        self.duration = duration or []

