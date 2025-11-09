# NH25_flux_Atlas - AI Coding Agent Instructions

## Project Overview

This is a **Nathacks 2025 hackathon project** simulating global resource trading through cluster-based auctions. The system models countries grouped by PPP (Purchasing Power Parity), managing their resource supply/demand and conducting Vickrey (second-price) sealed-bid auctions.

## Architecture

### Core Components

1. **`models/`** - Data models and business logic

   - `country.py`: Country entities with PPP, budget, resources (supply), and demand
   - `cluster.py`: ClusterInfo groups countries, calculates budgets, and distributes auction batches
   - `cluster_enums.py`: Hardcoded country clusters (GROUP1-GROUP6) with initial budgets
   - `country_data.py`: Hardcoded resource allocations for all countries
   - `resourcess.py`: Resource dataclass and GlobalResources constants

2. **`auction/`** - Auction mechanics

   - `auction.py`: Individual sealed-bid auction logic with status management
   - `auction_manager.py`: **Main simulation entry point** - orchestrates Vickrey auctions using Laplace valuation

3. **`frontend/`** - TypeScript/React (minimal implementation)
   - Uses `clsx` and `tailwind-merge` for styling utilities

### Data Flow Architecture

```
CountryClusters (cluster_enums.py)
  ├─> ClusterInfo.assign_auction_quantity()
  │   └─> Calculates proportional batch distribution
  │
  └─> Country objects (auto-load resources from country_data.py)
      ├─> Supply: country_resources dict
      ├─> Demand: country_demands dict
      └─> Budget: Calculated from cluster PPP distribution
```

### Key Design Patterns

#### 1. **Auto-initialization Pattern**

Countries automatically load resources in `__post_init__`:

```python
# Country class auto-loads data from country_data.py
def __post_init__(self):
    if self.name in country_resources:
        self.resources = country_resources[self.name].copy()
    if self.name in country_demands:
        self.demand = country_demands[self.name].copy()
```

#### 2. **Proportional Distribution Formula**

Auctions distribute quantities proportionally:

```python
# In cluster.py
proportional_share = float(self.country_count) / float(total_countries_in_world)
self.auction_quantity = total_auction_quantity * proportional_share
```

#### 3. **Batch Halving Algorithm**

Clusters divide auction quantity into batches:

- Batch 1: quantity / 2
- Batch 2: remaining / 2
- Batch n-1: all remaining
  (See `ClusterInfo._calculate_and_store_batches()`)

#### 4. **Laplace Valuation Model**

Bidders calculate max willingness-to-pay:

```python
# AuctionManager.laplace() returns (v_value, accepted)
multiplier = 1.0 + max_increase * math.exp(-distance / b)
v_value = base_price * multiplier
```

## Running the Simulation

### Main Entry Point

```bash
python auction/auction_manager.py
```

**Critical**: The simulation uses **live Country objects** from `CountryClusters` enums:

```python
# MUST get actual object, not create new instance
for country in CountryClusters.GROUP5.value.countries:
    if country.name == "Russia":
        seller_country = country
```

### Workflow

1. Seller is selected from a cluster (e.g., Russia from GROUP5)
2. System calculates proportional auction quantities across all clusters
3. Each cluster's batches are auctioned sequentially
4. Bidders use Laplace formula to determine max bid
5. Winner pays second-highest bid (Vickrey mechanism)
6. Budgets and resources update in-place on Country objects

## Development Conventions

### Code Organization

- **Dataclasses everywhere**: Models use `@dataclass` with `field(default_factory=...)`
- **Type hints**: All function signatures include type hints
- **Enums for clusters**: `CountryClusters` is an Enum with ClusterInfo values
- **`__main__` blocks**: Most model files include test code in `if __name__ == "__main__"`

### Import Patterns

```python
# Relative imports within models/
from .country import Country
from .cluster import ClusterInfo

# Path manipulation for cross-package imports
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### Data Mutability

- Country objects are **mutable** - budgets and resources update directly during auctions
- Use `.copy()` when initializing resources to avoid shared references
- `country_resources` and `country_demands` are module-level dicts in `country_data.py`

## Critical Implementation Details

### Supply/Demand Analysis

Countries have built-in analysis methods:

```python
country.get_supply_demand_gap("PETROLEUM")  # Returns dict with status: SURPLUS/DEFICIT/BALANCED
country.get_export_resources()  # List of resources with surplus
country.get_import_needs()  # List of resources with deficit
```

### Budget Calculation

Two-level budget distribution:

1. **Cluster level**: Hardcoded in `cluster_enums.py` (e.g., GROUP1 = $5B, GROUP6 = $120B)
2. **Country level**: Auto-calculated proportional to PPP within cluster
   ```python
   country.budget = (country.ppp / cluster_total_ppp) * cluster.budget
   ```

### Resource Units

Resources have heterogeneous units (billion barrels, million tonnes, GW capacity):

```python
Resource(amount=80.0, unit="billion barrels")
```

Always preserve units when transferring resources.

## Frontend Integration

- Frontend is a **stub** - primary logic is Python-based simulation
- TypeScript lives in `frontend/src/lib/`
- No backend API currently - would need to expose Python simulation via REST/WebSocket

## Common Pitfalls

1. **Don't create new Country instances** - use existing objects from `CountryClusters`
2. **Check `live_auction_stock`** - simulation tracks remaining inventory separately
3. **Vickrey pricing** - winner pays second-highest bid, NOT their own bid
4. **Budget validation** - always verify `winner.budget >= total_cost` before transaction
5. **Resource existence** - check both `has_resource()` and `get_demand()` before operations

## Testing Approach

Run individual modules with embedded test blocks:

```bash
python models/country.py  # Test country + resource loading
python models/cluster_enums.py  # Test budget calculations
python auction/auction_manager.py  # Full simulation
```

## Extension Points

- Add new countries: Update `cluster_enums.py` and `country_data.py`
- New resources: Add to `GlobalResources` and country data dicts
- Alternative auction mechanisms: Implement alongside `AuctionManager.laplace()`
- Frontend visualization: Consume Python simulation state via API layer
