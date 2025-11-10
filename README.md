# NH25_Flux_Atlas: Economic Resource Trading Simulation

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

### Laplace-Based Bidding Psychology
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
- NeurAlbertaTech Hackathon 2023
- Economic simulation research community
- FastAPI and React communities

## Status
Project is: _in active development_



<a href="https://github.com/Aarushb/NH25_flux_Atlas/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Aarushb/NH25_flux_Atlas" />
</a>