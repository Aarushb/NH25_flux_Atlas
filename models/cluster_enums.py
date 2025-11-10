from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import requests

from .country import Country
from .cluster import ClusterInfo


class CountryClusters(Enum):
    """Dynamic clusters loaded from API groups."""
    
    @classmethod
    def load_from_api(cls, api_base_url: str = "http://localhost:8000") -> List[ClusterInfo]:
        """
        Load all clusters from API groups.
        
        Returns:
            List of ClusterInfo objects populated from database
        """
        try:
            # Get all groups
            groups_response = requests.get(f"{api_base_url}/groups")
            groups_response.raise_for_status()
            groups = groups_response.json()
            
            clusters = []
            for group in groups:
                cluster = ClusterInfo.from_group_id(group['id'], api_base_url)
                if cluster:
                    clusters.append(cluster)
            
            return clusters
            
        except requests.RequestException as e:
            print(f"Error loading clusters from API: {e}")
            return []
    
    @classmethod
    def get_cluster_by_name(cls, cluster_name: str, api_base_url: str = "http://localhost:8000") -> Optional[ClusterInfo]:
        """Get a specific cluster by name."""
        clusters = cls.load_from_api(api_base_url)
        for cluster in clusters:
            if cluster.name.lower() == cluster_name.lower():
                return cluster
        return None
    
    @classmethod
    def get_all_countries(cls, api_base_url: str = "http://localhost:8000") -> List[Country]:
        """Get all countries from all clusters."""
        clusters = cls.load_from_api(api_base_url)
        all_countries = []
        for cluster in clusters:
            all_countries.extend(cluster.countries)
        return all_countries


def get_cluster_country_budgets(cluster: ClusterInfo) -> Dict[str, float]:
    """
    Calculate budget allocation for all countries in a specific cluster.
    
    Args:
        cluster: ClusterInfo object (not enum anymore)
    """
    return cluster.calculate_country_budgets()


if __name__ == "__main__":
    print("=== Loading Clusters from API ===\n")
    
    clusters = CountryClusters.load_from_api()
    
    for cluster in clusters:
        print(f"--- {cluster.name} ---")
        print(f"PPP Range: ${cluster.min_ppp} - ${cluster.max_ppp}")
        print(f"Total Cluster Budget: ${cluster.budget}B")
        print(f"Countries ({cluster.country_count}):")
        
        for country in cluster.countries:
            print(f"  {country.name}: PPP=${country.ppp}, Budget=${country.budget:.2f}B")
        
        print()