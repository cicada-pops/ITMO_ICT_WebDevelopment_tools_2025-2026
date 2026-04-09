from enum import Enum


class HackathonStatus(str, Enum):
    planned = "planned"
    ongoing = "ongoing"
    finished = "finished"


class TeamRole(str, Enum):
    lead = "lead"
    developer = "developer"
    designer = "designer"
    pm = "pm"
    analyst = "analyst"
