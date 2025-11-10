# Flux_Atlas: Economic Resource Trading Simulation

## Overview
NH25_Flux_Atlas is a sophisticated economic simulation platform that models resource trading between countries using psychologically-informed bidding behaviors and cluster-based auction mechanisms.

## Key Features
- Dynamic resource trading simulation
- Cluster-based auction system
- Psychologically modeled bidding behavior
- Real-time API integration
- Interactive bidding interface
- Turn-based simulation mode

## Mathematical Model

### Laplace-Based Bidding
The simulation uses a modified Laplace distribution to model bidding behavior based on supply-demand dynamics. Our bidding function combines market dynamics with psychological distance decay:

$$ v_{value} = base_{price} \cdot (1.0 + max_{increase} \cdot w) $$

where:

$$ max_{increase} = max(0.0, min(1.0, \frac{demand}{supply} - 1.0)) $$
$$ w = e^{-\frac{|quantity - demand|}{b}} $$
$$ b = max(|demand| \cdot k, min_b) $$

The key components are:
- `w`: Laplace decay factor (psychological willingness to deviate from ideal quantity)
- `b`: Scale parameter controlling bid sensitivity
- `distance`: Absolute difference between offered quantity and demanded quantity
- `k`: Sensitivity multiplier for demand-based scaling
- `min_b`: Minimum scale parameter to prevent division by zero

```python
v_value = base_price * (1.0 + max_increase * w)
where:
- max_increase = max(0.0, min(1.0, (demand/supply) - 1.0))
- w = exp(-distance/b)  # Laplace decay
- b = max(abs(demand) * k, min_b)  # Sensitivity
- distance = |quantity - demand|
```

### Vickrey Auction Mechanism
After countries compute their bid values using the Laplace-based psychological model, the auction follows a Vickrey (second-price sealed-bid) mechanism:

1. Each country submits their sealed bid `v_value` computed from the Laplace function
2. The highest bidder wins the auction
3. The winner pays the second-highest bid price (or base price if single bidder)

This mechanism is chosen because:
- It incentivizes truthful bidding - countries' best strategy is to bid their true valuation
- Reduces strategic manipulation - winning price depends on others' bids
- Balances market efficiency with fair pricing
- Prevents winner's curse and aggressive overbidding

Mathematically:
$$p_{final} = \begin{cases} 
v_{2nd\text{-}highest} & \text{if multiple bids} \\
base_{price} & \text{if single bidder}
\end{cases}$$

Where $p_{final}$ is the final price per unit that the winning country pays.

### Cluster-Based Distribution System

Our simulation implements a sophisticated cluster-based distribution system that ensures fair market access across different economic tiers:

#### Batch Halving Mechanism
```
Initial Quantity: Q
Round 1: Q/2
Round 2: Q/4
Round 3: Q/8
Round 4: Q/8 (remainder)
```

This halving mechanism serves multiple purposes:
- Allows countries with smaller demands to participate in later rounds
- Prevents market monopolization by larger economies
- Creates multiple opportunities for price discovery
- Ensures efficient resource distribution across all economic clusters

#### Economic Clustering
Countries are grouped into economic clusters (e.g., Emerging Markets, Developing Nations, High-Income Nations). Each cluster:
- Receives a proportional allocation of the auctioned resource
- Participates in independent parallel auctions
- Competes within their economic peer group
- Has equal access to each batch round

### Market Participant Behaviors

#### Seller Decision Making
Countries decide to sell based on several factors:
1. **Supply-Driven Probability**: Higher resource supply increases likelihood of initiating auction
   ```python
   auction_probability = min(0.3, supply_amount / total_world_supply)
   ```
2. **Conservative Quantity Selection**: Countries offer 10-30% of their supply
   ```python
   auction_quantity = supply * random.uniform(0.1, 0.3)
   ```
3. **Multi-Round Strategy**: Resources not sold in one round cascade to next batch

#### Buyer Psychology
The bidding strategy incorporates demand-matching and quantity optimization:

1. **Demand Alignment**:
   $$bid\_urgency = \frac{|quantity - demand|}{demand}$$
   - Lower difference → Higher bid probability
   - Perfect quantity match maximizes bid value

2. **Supply-Demand Ratio Impact**:
   $$bid\_modifier = \frac{demand}{available\_supply}$$
   - High demand/low supply → Aggressive bidding
   - Low demand/high supply → Conservative bidding

3. **Quantity Sensitivity**:
   - Large quantity mismatch reduces bid probability
   - Small batches attract countries with precise demands
   - Batch size reduction increases participation from smaller economies

This multi-faceted approach creates a dynamic market where:
- Resources are distributed efficiently across economic tiers
- Countries participate based on realistic economic behaviors
- Market access is democratized through the batch system
- Price discovery occurs at multiple levels

### Future Metrics (Placeholder)
_Future enhancement planned for incorporating additional economic indicators:_
- GDP influence
- Political relations
- Transportation costs

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
```bash
# Clone repository
git clone https://github.com/your-repo/NH25_flux_Atlas.git
cd NH25_flux_Atlas

# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp api/.env.example api/.env
# Edit .env with your database credentials

# Start API server
cd api
python3 run.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Project Structure
```
NH25_flux_Atlas/
├── api/                  # FastAPI backend
│   ├── app/             # API implementation
│   └── run.py           # API entry point
├── auction/             # Auction logic
│   ├── auction.py       # Base auction classes
│   └── turn_based_simulation.py  # Turn-based logic
├── frontend/           # React frontend
├── models/             # Data models
└── requirements.txt    # Python dependencies
```

## API Documentation
Once running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Running a Basic Simulation
```python
from auction.turn_based_simulation import TurnBasedSimulation

sim = TurnBasedSimulation(max_turns=5)
sim.run(verbosity="verbose")
```

### Starting Interactive Bidding
```python
from auction.auction_manager import run_bidding_simulation

run_bidding_simulation(
    bidder_country=japan,
    seller_country=russia,
    resource_name="PETROLEUM",
    total_quantity=50.0,
    base_price=0.5
)
```

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## Contributors
- Neamur
- Arush
- Cong
- Jacob
- Chrea
- Shashreek

## License
See the LICENSE file for details.

## Acknowledgments
- NeurAlbertaTech Hackathon 2025


<a href="https://github.com/Aarushb/NH25_flux_Atlas/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Aarushb/NH25_flux_Atlas" />
</a>
