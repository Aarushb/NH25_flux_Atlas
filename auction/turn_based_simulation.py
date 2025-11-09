"""
Turn-based auction simulation where each country takes turns to:
1. Do nothing
2. Start an auction (if they have surplus resources)
3. Place a bid on an existing auction (if they have demand)
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
import io
from contextlib import redirect_stdout

from models.country import Country
from models.cluster_enums import CountryClusters
from auction import Auction, AuctionStatus
from auction_manager import AuctionManager


@dataclass
class TurnBasedSimulation:
    """Manages turn-based simulation where countries act sequentially."""
    all_countries: List[Country] = field(default_factory=list)
    active_auctions: List[Auction] = field(default_factory=list)
    auction_start_turns: List[tuple] = field(default_factory=list)  # List of (auction, start_turn)
    turn_number: int = 0
    max_turns: int = 100
    auction_duration: int = 3  # Auctions stay open for 3 turns
    initial_budgets: Dict[str, float] = field(default_factory=dict)
    initial_resources: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize all countries from clusters."""
        if not self.all_countries:
            for cluster_enum in CountryClusters:
                self.all_countries.extend(cluster_enum.value.countries)
        
        # Store initial state for comparison
        for country in self.all_countries:
            self.initial_budgets[country.name] = country.budget
            self.initial_resources[country.name] = {
                resource_name: resource.amount 
                for resource_name, resource in country.resources.items()
            }
    
    def run(self):
        """Main simulation loop - each turn, every country gets to act."""
        print("="*70)
        print("TURN-BASED AUCTION SIMULATION")
        print("="*70)
        print(f"Total Countries: {len(self.all_countries)}")
        print(f"Max Turns: {self.max_turns}\n")
        
        for turn in range(1, self.max_turns + 1):
            self.turn_number = turn
            print(f"\n{'='*70}")
            print(f"TURN {turn}")
            print(f"{'='*70}")
            print(f"Active Auctions: {len(self.active_auctions)}")
            
            # Each country takes a turn
            for country in self.all_countries:
                self.country_turn(country)
            
            # Process auction closings (auctions that have been open for 1+ turns)
            self.process_auction_closings()
        
        print(f"\n--- Reached maximum turns ({self.max_turns}). Ending simulation. ---")
        self.print_final_state()
    
    def country_turn(self, country: Country):
        """A single country's turn to decide action."""
        action = self.decide_action(country)
        
        if action["type"] == "NOTHING":
            pass  # Do nothing
        
        elif action["type"] == "START_AUCTION":
            self.start_auction(country, action["resource"], action["quantity"], action["base_price"])
        
        elif action["type"] == "BID":
            self.place_bid(country, action["auction"], action["bid_price"])
    
    def decide_action(self, country: Country) -> Dict:
        """
        AI decision logic for what action a country should take.
        Priority:
        1. Bid on auctions for resources you need
        2. Start auction for surplus resources
        3. Do nothing
        """
        # Check if there are auctions for resources this country needs
        import_needs = country.get_import_needs()
        
        for auction in self.active_auctions:
            if auction.status == AuctionStatus.BIDDING_OPEN:
                # Check if this is a resource we need
                if auction.resource_name in import_needs:
                    # Check if we haven't bid yet
                    already_bid = any(bid.country == country for bid in auction.bids)
                    if not already_bid and auction.seller != country:
                        # Calculate bid using Laplace
                        bid_price = self.calculate_bid_price(country, auction)
                        if bid_price and country.budget >= bid_price * auction.quantity:
                            return {
                                "type": "BID",
                                "auction": auction,
                                "bid_price": bid_price
                            }
        
        # Check if we should start an auction
        # Countries can auction ANY resource they have (not just surplus)
        available_resources = [r for r in country.resources.keys() if country.resources[r].amount > 0]
        
        if available_resources and random.random() < 0.2:  # 20% chance to auction
            resource_name = random.choice(available_resources)
            supply = country.get_resource(resource_name).amount
            
            # Sell a small portion (5-15%) of what they have
            quantity = supply * random.uniform(0.05, 0.15)
            
            if quantity > 0.01:  # Minimum quantity threshold
                base_price = 0.05  # Simple base price
                return {
                    "type": "START_AUCTION",
                    "resource": resource_name,
                    "quantity": quantity,
                    "base_price": base_price
                }
        
        return {"type": "NOTHING"}
    
    def calculate_bid_price(self, country: Country, auction: Auction) -> Optional[float]:
        """Calculate bid price using Laplace valuation."""
        demand_res = country.get_demand(auction.resource_name)
        if not demand_res:
            return None
        
        supply_res = country.get_resource(auction.resource_name)
        supply = supply_res.amount if supply_res else 0.0
        demand = demand_res.amount
        
        v_value, accepted = AuctionManager.laplace(
            base_price=auction.asking_price_per_unit,
            supply=supply,
            demand=demand,
            quantity=auction.quantity
        )
        
        return v_value if accepted else None
    
    def start_auction(self, seller: Country, resource_name: str, quantity: float, base_price: float):
        """Country starts an auction."""
        seller_resource = seller.get_resource(resource_name)
        if not seller_resource or seller_resource.amount < quantity:
            return  # Can't auction what you don't have
        
        auction = Auction(
            seller=seller,
            resource_name=resource_name,
            quantity=quantity,
            resource_unit=seller_resource.unit,
            asking_price_per_unit=base_price,
            current_market_price=base_price  # Simplified
        )
        
        # Suppress verbose output from open_bidding()
        with redirect_stdout(io.StringIO()):
            if auction.open_bidding():
                self.active_auctions.append(auction)
                self.auction_start_turns.append((auction, self.turn_number))  # Track when it started
    
    def place_bid(self, country: Country, auction: Auction, bid_price: float):
        """Country places a bid on an auction."""
        # Suppress verbose output from submit_bid()
        with redirect_stdout(io.StringIO()):
            auction.submit_bid(country, bid_price)
    
    def process_auction_closings(self):
        """Close and resolve auctions that have been open for the specified duration."""
        auctions_to_remove = []
        
        for auction in self.active_auctions:
            # Find when this auction started
            start_turn = None
            for auc, turn in self.auction_start_turns:
                if auc is auction:
                    start_turn = turn
                    break
            
            if start_turn is None:
                continue  # Skip if not found
            
            turns_open = self.turn_number - start_turn
            
            # Only close auction if it's been open for the full duration
            if auction.status == AuctionStatus.BIDDING_OPEN and turns_open >= self.auction_duration:
                if len(auction.bids) > 0:
                    # Suppress verbose output from close_bidding and determine_winner
                    with redirect_stdout(io.StringIO()):
                        auction.close_bidding()
                        auction.determine_winner()
                    
                    # Only print the result
                    if auction.winner:
                        total_paid = auction.final_price_per_unit * auction.quantity
                        print(f"  ✓ AUCTION RESULT: {auction.seller.name} sold {auction.quantity:.2f} {auction.resource_name} to {auction.winner.name} for ${total_paid:.2f}B ({len(auction.bids)} bids)")
                    
                    auctions_to_remove.append(auction)
                else:
                    # No bids after full duration - cancel auction
                    auction.status = AuctionStatus.CANCELLED
                    auctions_to_remove.append(auction)
        
        # Remove completed/cancelled auctions
        for auction in auctions_to_remove:
            self.active_auctions.remove(auction)
            # Remove from tracking list
            self.auction_start_turns = [(auc, turn) for auc, turn in self.auction_start_turns if auc is not auction]
    
    def any_trading_opportunities(self) -> bool:
        """Check if any country has trading opportunities."""
        for country in self.all_countries:
            if country.get_export_resources() and country.get_import_needs():
                return True
        return False
    
    def print_final_state(self):
        """Print final simulation state with changes."""
        print("\n" + "="*70)
        print("FINAL SIMULATION STATE")
        print("="*70)
        print(f"Total Turns: {self.turn_number}")
        
        print("\n" + "="*70)
        print("BUDGET AND RESOURCE CHANGES")
        print("="*70)
        
        for cluster_enum in CountryClusters:
            print(f"\n--- {cluster_enum.name} ---")
            for country in cluster_enum.value.countries:
                initial_budget = self.initial_budgets[country.name]
                budget_change = country.budget - initial_budget
                budget_symbol = "+" if budget_change >= 0 else ""
                
                print(f"\n  {country.name}:")
                print(f"    Budget: ${initial_budget:6.2f}B → ${country.budget:6.2f}B ({budget_symbol}${budget_change:6.2f}B)")
                
                # Show resource changes
                all_resources = set(self.initial_resources.get(country.name, {}).keys()) | set(country.resources.keys())
                
                if all_resources:
                    print(f"    Resources:")
                    for resource_name in sorted(all_resources):
                        initial = self.initial_resources.get(country.name, {}).get(resource_name, 0.0)
                        current_resource = country.get_resource(resource_name)
                        current = current_resource.amount if current_resource else 0.0
                        change = current - initial
                        
                        if change != 0:  # Only show resources that changed
                            change_symbol = "+" if change >= 0 else ""
                            unit = current_resource.unit if current_resource else "units"
                            print(f"      {resource_name}: {initial:.2f} → {current:.2f} ({change_symbol}{change:.2f} {unit})")


if __name__ == "__main__":
    # Create and run simulation
    sim = TurnBasedSimulation(max_turns=50)
    sim.run()
