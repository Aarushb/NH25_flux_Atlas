"""
Turn-based auction simulation using the same cluster-based batch system as auction_manager.py.

Each turn, countries can:
1. Start an auction for their resources (using cluster batch distribution)
2. Place a bid on an existing batch auction
3. Do nothing

Rules:
- Auctions follow the cluster batch system (proportional distribution + halving batches)
- Each batch auction lasts 4 rounds
- Countries currently selling cannot bid on other auctions
- Countries can start a new auction only when their previous auction completes all batches
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import random
import time

from models.resourcess import Resource
from models.country import Country
from models.cluster import ClusterInfo
from models.cluster_enums import CountryClusters
from auction_manager import AuctionManager


@dataclass
class BatchAuction:
    """
    Represents a single batch within a cluster's auction sequence.
    Each batch lasts exactly 1 turn:
    - Turn N: Batch created, bidding happens
    - Turn N+1: Batch finalized, results shown
    """
    batch_id: str  # Format: "auction_{auction_id}_cluster_{cluster_name}_batch_{batch_num}"
    parent_auction_id: int
    cluster: ClusterInfo
    batch_number: int
    seller: Country
    resource_name: str
    quantity: float
    resource_unit: str
    base_price: float
    turn_created: int  # Track when batch was created
    bids: List[tuple] = field(default_factory=list)  # List of (country, v_value)
    is_finalized: bool = False
    winner: Optional[Country] = None
    final_price_per_unit: float = 0.0
    
    def add_bid(self, country: Country, v_value: float) -> bool:
        """Add a bid from a country using Laplace valuation."""
        # Can't bid on finalized batch
        if self.is_finalized:
            return False
            
        # Check if country already bid
        for existing_bidder, _ in self.bids:
            if existing_bidder.name == country.name:
                return False
        
        # Check if bidder has enough budget
        total_cost = v_value * self.quantity
        if country.budget < total_cost:
            return False
        
        self.bids.append((country, v_value))
        return True
    
    def finalize(self) -> bool:
        """
        Finalize batch using Vickrey (second-price) mechanism.
        Returns True if there was a successful trade, False otherwise.
        """
        if self.is_finalized:
            return False
            
        self.is_finalized = True
        
        if len(self.bids) == 0:
            return False
        
        # Sort bids by v_value (highest first)
        sorted_bids = sorted(self.bids, key=lambda x: x[1], reverse=True)
        
        self.winner, winner_bid_v_value = sorted_bids[0]
        
        # Vickrey pricing: winner pays second-highest bid or base price
        if len(sorted_bids) == 1:
            self.final_price_per_unit = self.base_price
        else:
            _, second_highest_v_value = sorted_bids[1]
            self.final_price_per_unit = second_highest_v_value
        
        total_cost = self.final_price_per_unit * self.quantity
        
        # Verify winner has budget
        if self.winner.budget < total_cost:
            self.winner = None  # Clear winner if they can't afford
            return False
        
        # Transfer money
        self.winner.budget -= total_cost
        self.seller.budget += total_cost
        
        # Transfer resources
        seller_resource = self.seller.get_resource(self.resource_name)
        seller_resource.amount -= self.quantity
        
        winner_resource = self.winner.get_resource(self.resource_name)
        if winner_resource:
            winner_resource.amount += self.quantity
        else:
            self.winner.resources[self.resource_name] = Resource(
                amount=self.quantity, 
                unit=self.resource_unit
            )
        
        return True


@dataclass
class ClusterAuctionState:
    """
    Tracks the state of a country's auction across all cluster batches.
    Maps directly to how auction_manager.py distributes across clusters.
    """
    auction_id: int
    seller: Country
    resource_name: str
    total_quantity: float
    resource_unit: str
    base_price: float
    start_turn: int
    batch_auctions: Dict[str, BatchAuction] = field(default_factory=dict)  # cluster_name -> BatchAuction
    current_batch_number: int = 1
    all_batches_complete: bool = False
    
    def create_batch_auctions_for_turn(self, batch_number: int, all_clusters: List, current_turn: int) -> List[BatchAuction]:
        """
        Create batch auctions for a specific batch number across all clusters.
        Returns list of BatchAuction objects for this batch.
        """
        new_batches = []
        
        for cluster_enum in all_clusters:
            cluster_info = cluster_enum.value
            
            # Get the quantity for this batch in this cluster
            quantity = cluster_info.get_batch_quantity(batch_number)
            
            if quantity is None or quantity <= 0:
                continue  # This cluster doesn't have this batch
            
            # Create batch auction
            batch_id = f"auction_{self.auction_id}_cluster_{cluster_info.name}_batch_{batch_number}"
            
            batch = BatchAuction(
                batch_id=batch_id,
                parent_auction_id=self.auction_id,
                cluster=cluster_info,
                batch_number=batch_number,
                seller=self.seller,
                resource_name=self.resource_name,
                quantity=quantity,
                resource_unit=self.resource_unit,
                base_price=self.base_price,
                turn_created=current_turn
            )
            
            self.batch_auctions[cluster_info.name] = batch
            new_batches.append(batch)
        
        return new_batches


@dataclass
class TurnBasedSimulation:
    """
    Turn-based simulation using cluster-based batch distribution.
    Integrates the auction_manager.py logic with country agency.
    """
    all_countries: List[Country] = field(default_factory=list)
    active_batch_auctions: List[BatchAuction] = field(default_factory=list)
    completed_batch_auctions: List[BatchAuction] = field(default_factory=list)
    active_cluster_auctions: Dict[int, ClusterAuctionState] = field(default_factory=dict)  # auction_id -> state
    turn_number: int = 0
    max_turns: int = 100
    next_auction_id: int = 1
    countries_currently_selling: Set[str] = field(default_factory=set)
    max_batches: int = 4  # Since all clusters now have 5 countries = 4 batches
    
    def __post_init__(self):
        """Initialize all countries from clusters."""
        if not self.all_countries:
            for cluster_enum in CountryClusters:
                self.all_countries.extend(cluster_enum.value.countries)
    
    def run(self, verbosity: str = "concise"):
        """Main simulation loop."""
        if verbosity != "none":
            print("="*70)
            print("TURN-BASED CLUSTER AUCTION SIMULATION")
            print("="*70)
            print(f"Total Countries: {len(self.all_countries)}")
            print(f"Max Turns: {self.max_turns}")
            print("Batch Duration: 1 turn per batch")
            print("Cluster System: Proportional distribution + halving batches\n")
        
        for turn in range(1, self.max_turns + 1):
            self.turn_number = turn
            
            if verbosity == "verbose":
                print(f"\n{'='*70}")
                print(f"TURN {turn}")
                print(f"{'='*70}")
                print(f"Active Batch Auctions: {len(self.active_batch_auctions)}")
                print(f"Active Cluster Auctions: {len(self.active_cluster_auctions)}")
            elif verbosity == "concise":
                print(f"\n=== TURN {turn} | Batch Auctions: {len(self.active_batch_auctions)} | Cluster Auctions: {len(self.active_cluster_auctions)} ===")
            
            # Phase 1: Finalize batches from previous turn (show results FIRST)
            self.finalize_previous_turn_batches(verbosity)
            
            # Phase 2: Each country takes their turn (start auctions, place bids)
            for country in self.all_countries:
                self.country_turn(country, verbosity)
            
            # Phase 3: Progress cluster auctions to next batch if current batch is done
            self.progress_cluster_auctions(verbosity)
            
            # Add 2-second delay between turns
            time.sleep(2)
        
        if verbosity != "none":
            print(f"\n{'='*70}")
            print(f"SIMULATION COMPLETE - {self.turn_number} turns")
            print(f"Total Batches Completed: {len(self.completed_batch_auctions)}")
            print(f"{'='*70}")
    
    def country_turn(self, country: Country, verbosity: str):
        """A single country's turn to decide action."""
        action = self.decide_action(country)
        
        if action["type"] == "NOTHING":
            if verbosity == "verbose":
                print(f"  {country.name}: No action")
        
        elif action["type"] == "START_AUCTION":
            success = self.start_cluster_auction(
                country,
                action["resource"],
                action["quantity"],
                action["base_price"]
            )
            if success and verbosity != "none":
                if verbosity == "concise":
                    print(f"  {country.name} started auction: {action['quantity']:.4f} {action['resource']} @ ${action['base_price']:.4f}B/unit")
                elif verbosity == "verbose":
                    print(f"  {country.name}: Started cluster auction for {action['quantity']:.4f} {action['resource']}")
        
        elif action["type"] == "BID":
            success = self.place_bid_on_batch(country, action["batch"], verbosity)
            if success and verbosity == "verbose":
                print(f"  {country.name}: Bid on batch {action['batch'].batch_id}")
    
    def decide_action(self, country: Country) -> Dict:
        """
        AI decision logic for country actions.
        
        Priority:
        1. If currently selling, cannot bid (skip turn)
        2. Bid on batch auctions for resources you need
        3. Start cluster auction for surplus resources (if not already selling)
        4. Do nothing
        """
        # Rule: If currently selling, cannot bid
        if country.name in self.countries_currently_selling:
            return {"type": "NOTHING"}
        
        # Try to bid on existing batch auctions for needed resources
        demand_dict = country.demand
        
        for batch in self.active_batch_auctions:
            # Skip if this is our own auction
            if batch.seller.name == country.name:
                continue
            
            # Skip if not in this batch's cluster
            if country not in batch.cluster.countries:
                continue
            
            # Check if we need this resource
            if batch.resource_name in demand_dict:
                demand_amount = demand_dict[batch.resource_name].amount
                
                # Check if we haven't bid yet
                already_bid = any(bidder.name == country.name for bidder, _ in batch.bids)
                
                if not already_bid and demand_amount > 0:
                    # We want to bid on this batch
                    return {
                        "type": "BID",
                        "batch": batch
                    }
        
        # Try to start an auction (if not currently selling)
        if country.name not in self.countries_currently_selling:
            # Check if country has ANY resources with surplus or just any resources
            available_resources = []
            for resource_name, resource in country.resources.items():
                if resource.amount > 0:
                    available_resources.append(resource_name)
            
            if available_resources and random.random() < 0.3:  # 30% chance to auction
                resource_name = random.choice(available_resources)
                supply = country.get_resource(resource_name).amount
                demand_res = country.get_demand(resource_name)
                demand = demand_res.amount if demand_res else 0.0
                
                # Sell a portion of what we have (10-30% of supply)
                quantity = supply * random.uniform(0.1, 0.3)
                
                if quantity > 0.01:  # Minimum quantity threshold
                    base_price = 0.05 * random.uniform(0.8, 1.2)  # Randomize base price
                    return {
                        "type": "START_AUCTION",
                        "resource": resource_name,
                        "quantity": quantity,
                        "base_price": base_price
                    }
        
        return {"type": "NOTHING"}
    
    def start_cluster_auction(self, seller: Country, resource_name: str, total_quantity: float, base_price: float) -> bool:
        """
        Start a cluster auction (like auction_manager.py's run_simulation).
        Calculates proportional distribution and creates batches.
        """
        # Check if already selling
        if seller.name in self.countries_currently_selling:
            return False
        
        # Check if seller has the resource
        seller_resource = seller.get_resource(resource_name)
        if not seller_resource or seller_resource.amount < total_quantity:
            return False
        
        # Calculate proportional distribution (same as auction_manager.py)
        total_countries_in_world = sum(cluster_enum.value.country_count for cluster_enum in CountryClusters)
        
        for cluster_enum in CountryClusters:
            cluster_info = cluster_enum.value
            cluster_info.assign_auction_quantity(total_quantity, total_countries_in_world)
        
        # Create cluster auction state
        auction_state = ClusterAuctionState(
            auction_id=self.next_auction_id,
            seller=seller,
            resource_name=resource_name,
            total_quantity=total_quantity,
            resource_unit=seller_resource.unit,
            base_price=base_price,
            start_turn=self.turn_number
        )
        
        # Create batch 1 auctions for all clusters
        batch_1_auctions = auction_state.create_batch_auctions_for_turn(1, CountryClusters, self.turn_number)
        self.active_batch_auctions.extend(batch_1_auctions)
        
        self.active_cluster_auctions[self.next_auction_id] = auction_state
        self.countries_currently_selling.add(seller.name)
        self.next_auction_id += 1
        
        return True
    
    def place_bid_on_batch(self, country: Country, batch: BatchAuction, verbosity: str) -> bool:
        """
        Place a bid on a batch auction using Laplace valuation (same as auction_manager.py).
        """
        # Get country's supply and demand
        supply_res = country.get_resource(batch.resource_name)
        supply = supply_res.amount if supply_res else 0.0
        
        demand_res = country.get_demand(batch.resource_name)
        if not demand_res:
            return False
        demand = demand_res.amount
        
        # Calculate v_value using Laplace (same as auction_manager.py)
        v_value, accepted = AuctionManager.laplace(
            base_price=batch.base_price,
            supply=supply,
            demand=demand,
            quantity=batch.quantity
        )
        
        if not accepted:
            return False
        
        # Add bid to batch
        return batch.add_bid(country, v_value)
    
    def finalize_previous_turn_batches(self, verbosity: str):
        """
        Finalize batches that were created in the previous turn.
        This shows the results BEFORE new actions happen.
        """
        batches_to_finalize = [b for b in self.active_batch_auctions 
                               if not b.is_finalized and b.turn_created < self.turn_number]
        
        for batch in batches_to_finalize:
            had_winner = batch.finalize()
            
            if verbosity != "none":
                if had_winner:
                    total_paid = batch.final_price_per_unit * batch.quantity
                    if verbosity == "concise":
                        print(f"  ✓ Batch #{batch.batch_id}: {batch.seller.name} → {batch.winner.name} | {batch.quantity:.4f} {batch.resource_name} for ${total_paid:.4f}B")
                    elif verbosity == "verbose":
                        print(f"  ✓ Batch COMPLETE: {batch.batch_id}")
                        print(f"     {batch.seller.name} → {batch.winner.name}")
                        print(f"     {batch.quantity:.4f} {batch.resource_unit} for ${total_paid:.4f}B")
                else:
                    if verbosity == "concise":
                        print(f"  ✗ Batch #{batch.batch_id}: No valid bids")
            
            # Remove from active and mark as complete
            self.active_batch_auctions.remove(batch)
            self.completed_batch_auctions.append(batch)
    
    def progress_cluster_auctions(self, verbosity: str):
        """
        Check if all batches for current batch number are finalized.
        If so, create next batch's auctions.
        """
        auctions_to_remove = []
        
        for auction_id, auction_state in self.active_cluster_auctions.items():
            # Check if all batches for current batch number are finalized
            current_batch_complete = True
            for cluster_name, batch in auction_state.batch_auctions.items():
                if not batch.is_finalized:
                    current_batch_complete = False
                    break
            
            if current_batch_complete:
                # Move to next batch
                auction_state.current_batch_number += 1
                
                if auction_state.current_batch_number > self.max_batches:
                    # All batches complete
                    auction_state.all_batches_complete = True
                    auctions_to_remove.append(auction_id)
                    
                    # Seller can now start new auctions
                    if auction_state.seller.name in self.countries_currently_selling:
                        self.countries_currently_selling.remove(auction_state.seller.name)
                    
                    if verbosity == "concise":
                        print(f"  ✓✓ Cluster Auction #{auction_id} COMPLETE: All batches finished")
                else:
                    # Create next batch auctions
                    auction_state.batch_auctions.clear()  # Clear previous batch tracking
                    next_batches = auction_state.create_batch_auctions_for_turn(
                        auction_state.current_batch_number,
                        CountryClusters,
                        self.turn_number
                    )
                    self.active_batch_auctions.extend(next_batches)
                    
                    if verbosity == "verbose":
                        print(f"  → Cluster Auction #{auction_id}: Moving to Batch {auction_state.current_batch_number}")
        
        # Remove completed auctions
        for auction_id in auctions_to_remove:
            del self.active_cluster_auctions[auction_id]


if __name__ == "__main__":
    # Create and run simulation
    sim = TurnBasedSimulation(max_turns=50)
    sim.run(verbosity="concise")  # Options: "none", "concise", "verbose"
    
    # Print summary statistics
    print("\n" + "="*70)
    print("AUCTION STATISTICS")
    print("="*70)
    successful_auctions = [b for b in sim.completed_batch_auctions if b.winner is not None]
    failed_auctions = [b for b in sim.completed_batch_auctions if b.winner is None]
    
    print(f"Total Batches Completed: {len(sim.completed_batch_auctions)}")
    print(f"  - Successful: {len(successful_auctions)}")
    print(f"  - Failed (no bids): {len(failed_auctions)}")
    
    total_value_traded = sum(b.final_price_per_unit * b.quantity for b in successful_auctions)
    print(f"Total Value Traded: ${total_value_traded:.4f}B")
    
    # Count unique sellers
    unique_sellers = set(b.seller.name for b in successful_auctions)
    print(f"Countries that sold resources: {len(unique_sellers)}")
    
    # Count unique buyers
    unique_buyers = set(b.winner.name for b in successful_auctions)
    print(f"Countries that bought resources: {len(unique_buyers)}")
    print("="*70)

