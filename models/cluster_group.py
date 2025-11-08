from .config import cluster
from typing import Dict
from pydantic import BaseModel, Field, ValidationError
from pydantic import field_validator 
from enum import Enum

class Cluster: 
    def __init__(self,k:Dict[str,int]):
        self.group= k
        self.
class Countries(Enum,str):



class Agent:
    def __init__(self,k:Dict[str,int], country:str):
        self.country = country
        self.
        
