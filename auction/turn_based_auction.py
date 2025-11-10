"""
Turn-Based Auction World Simulation

This file creates a persistent, turn-based simulation where all 30
countries act as AI agents, deciding each turn whether to SELL resources,
BID on active auctions, or do NOTHING.

The simulation runs in discrete turns, with a built-in delay:
-   Turn 1: Bids are PLACED (by AI or Human).
-   Turn 2: Bids from Turn 1 are FINALIZED (Vickrey applied).

This system is designed to run continuously and allows for human
players to "hook in" by manually submitting bids or starting auctions,
overriding the AI's decisions.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
import random
import math
import time

# --- Import All Model and Logic Helpers ---
from models.country import Country
from models.cluster import ClusterInfo
from models.cluster_enums import CountryClusters
from models.resourcess import Resource
# from auction_manager import AuctionManager # <-- REMOVED THIS IMPORT

# -----------------------------------------------------------------
# --- DATA CLASSES FOR TRACKING BIDS AND AUCTIONS ---
# -----------------------------------------------------------------

@dataclass
class CountryBid:
    """Represents a single bid from a country for a specific batch."""
    country: Country
    bid_price_per_unit: float
    is_manual_override: bool = False # True if placed by a human
    timestamp: int = 0               # Turn number when bid was placed

@dataclass
class ClusterBatchAuction:
    """
    Represents ONE batch of an auction in ONE cluster.
    This is the object that countries bid on.
    """
    # --- Auction Details ---
    parent_auction_id: int
    batch_auction_id: str  # e.g., "1-GROUP1-B1"
    batch_number: int
    cluster: ClusterInfo
    
    # --- Item Details ---
    seller: Country
    resource_name: str
    quantity: float
    resource_unit: str
    base_price: float
    
    # --- State Tracking ---
    created_turn: int
    bids: Dict[str, CountryBid] = field(default_factory=dict) # country.name -> Bid
    is_finalized: bool = False
    winner: Optional[Country] = None
    final_price_per_unit: Optional[float] = None
    
    def add_bid(self, bid: CountryBid):
        """Add or update a bid. Manual bids always overwrite AI bids."""
        existing_bid = self.bids.get(bid.country.name)
        
        # Don't let an AI bid overwrite a manual (human) bid
        if existing_bid and existing_bid.is_manual_override and not bid.is_manual_override:
            return 
            
        # Add or overwrite
        self.bids[bid.country.name] = bid

    def finalize_vickrey(self) -> Tuple[bool, str]:
        """
        Apply Vickrey (second-price) mechanism to determine winner.
        This is called at the *start* of the next turn.
        """
        if self.is_finalized:
            return False, "Already finalized."
            
        self.is_finalized = True # Mark as processed
        
        if not self.bids:
            return False, "No bids."
        
        # Sort bids by price (highest first)
        sorted_bids = sorted(self.bids.values(), key=lambda b: b.bid_price_per_unit, reverse=True)
        
        winner_bid = sorted_bids[0]
        self.winner = winner_bid.country
        
        # Vickrey: winner pays second-highest price or base price
        if len(sorted_bids) == 1:
            self.final_price_per_unit = self.base_price
        else:
            self.final_price_per_unit = sorted_bids[1].bid_price_per_unit
        
        total_cost = self.final_price_per_unit * self.quantity
        
        # --- Edge Case: Check Winner's Budget ---
        if self.winner.budget < total_cost:
            self.winner = None # Winner fails, no transaction
            return False, f"Winner {winner_bid.country.name} has no budget (${winner_bid.country.budget:.2f}B < ${total_cost:.2f}B)"
        
        # --- Process Transaction ---
        # 1. Transfer money
        self.winner.budget -= total_cost
        self.seller.budget += total_cost
        
        # 2. Transfer resources
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
        
        # 3. Update Winner's Demand (as requested)
        winner_demand = self.winner.get_demand(self.resource_name)
        if winner_demand:
            winner_demand.amount *= 0.9998 # Decrease demand by 0.02%
            
        return True, f"{self.winner.name} wins, pays ${self.final_price_per_unit:.4f}/unit"

@dataclass
class MultiClusterAuction:
    """
    Represents one country's ENTIRE auction, distributed across all clusters.
    This class manages the lifecycle of all its child ClusterBatchAuctions.
    """
    auction_id: int
    seller: Country
    resource_name: str
    total_quantity: float
    base_price: float
    created_turn: int
    
    # cluster.name -> list of batches
    cluster_batches: Dict[str, List[ClusterBatchAuction]] = field(default_factory=dict)
    
    current_batch_number: int = 1
    is_complete: bool = False

    def get_active_batches(self) -> List[ClusterBatchAuction]:
        """Get all batches for the current batch number."""
        active = []
        for cluster_name, batches in self.cluster_batches.items():
            for batch in batches:
                if batch.batch_number == self.current_batch_number:
                    active.append(batch)
        return active

    def advance_to_next_batch(self) -> bool:
        """
        Move to the next batch number.
        Returns True if the auction is now complete.
        """
        self.current_batch_number += 1
        
        # Check if we have any batches for this next number
        for cluster_name, batches in self.cluster_batches.items():
            for batch in batches:
                if batch.batch_number == self.current_batch_number:
                    # Found a valid next batch, auction is not complete
                    return False 
        
        # No batches found for the new batch number. Auction is over.
        self.is_complete = True
        return True

# -----------------------------------------------------------------
# --- THE MAIN SIMULATION ENGINE ---
# -----------------------------------------------------------------

@dataclass
class TurnBasedAuctionSystem:
    """
    Main turn-based simulation engine.
    This class holds the state of the "world" and processes turns.
    """
    # --- World State ---
    all_countries: List[Country] = field(default_factory=list)
    all_clusters: List[ClusterInfo] = field(default_factory=list)
    turn_number: int = 0
    
    # --- Auction Tracking ---
    next_auction_id: int = 1
    next_batch_auction_id: int = 1
    
    # All active (non-complete) multi-cluster auctions
    active_auctions: Dict[int, MultiClusterAuction] = field(default_factory=dict)
    
    # All *individual batches* that are open for bidding THIS turn
    open_for_bidding: Dict[str, ClusterBatchAuction] = field(default_factory=dict)
    
    # Batches that received bids this turn and will be finalized NEXT turn
    pending_finalization: List[ClusterBatchAuction] = field(default_factory=list)

    # --- Country State ---
    countries_currently_selling: Set[str] = field(default_factory=set)
    
    # --- Statistics ---
    completed_transactions: int = 0
    total_value_traded: float = 0.0

    def __post_init__(self):
        """Initialize the world from CountryClusters enum."""
        if not self.all_countries:
            for cluster_enum in CountryClusters:
                cluster = cluster_enum.value
                self.all_clusters.append(cluster)
                self.all_countries.extend(cluster.countries)
            print(f"World Initialized: {len(self.all_countries)} countries, {len(self.all_clusters)} clusters.")

    def get_country_by_name(self, name: str) -> Optional[Country]:
        """Helper to find a country object by its name."""
        for c in self.all_countries:
            if c.name == name:
                return c
        return None

    # --- [FIXED] LAPLACE METHOD ---
    @staticmethod
    def laplace(base_price: float, supply: float, demand: float, quantity:float, min_b:int=1 , min_w:int=0.0001, k:int=0.1):
        """
        Calculates a country's max acceptable bid (v_value) for a given quantity.
        This is the "AI brain" for competitor bidders.
        (Moved from auction_manager.py)
        """
        # 1. Handle invalid base price
        if base_price <= 0:
            raise ValueError("Base price must be > 0")
    
        # 2. Avoid division by zero
        if supply <= 0:
            # If no internal supply, max_increase is 1 (willing to pay up to 2x base)
            max_increase = 1.0 
        else:
            # If demand > supply, calculate increase. If supply > demand, cap at 0 (no increase).
            max_increase = max(0.0, min(1.0, (demand / supply) - 1.0))
         
        # 3. Compute b (sensitivity), ensure it never hits zero
        b = max(abs(demand) * k, float(min_b))
    
        # 4. Distance from ideal offer (demand)
        distance = abs(quantity - demand)
    
        # 5. Laplace decay weight
        w = math.exp(- distance / b)
    
        # 6. Compute final adjusted value (v_value)
        multiplier = 1.0 + max_increase * w
        v = base_price * multiplier
    
        # 7. Threshold accept/reject (must be at least base price)
        if v < base_price:
            return v, False
            
        return v, True

    # --- PUBLIC API "HOOKS" ---

    def manual_start_auction(self, country: Country, resource_name: str, quantity: float, base_price: float) -> Optional[int]:
        """
        HOOK for a human to force their country to start an auction.
        Bypasses probability checks.
        """
        if country.name in self.countries_currently_selling:
            print(f"HOOK Error: {country.name} is already selling.")
            return None
            
        # Check stock
        seller_resource = country.get_resource(resource_name)
        if not seller_resource or seller_resource.amount < quantity:
            print(f"HOOK Error: {country.name} does not have {quantity} {resource_name} to sell.")
            return None
        
        # Manually create and process the auction
        auction_id = self._create_new_auction(country, resource_name, quantity, base_price)
        print(f"HOOK Success: {country.name} manually started Auction #{auction_id}.")
        return auction_id

    def manual_bid(self, country: Country, batch_auction_id: str, bid_price: float) -> bool:
        """
        HOOK for a human to join and bid on an active batch.
        This bid OVERWRITES any AI-generated bid.
        """
        batch = self.open_for_bidding.get(batch_auction_id)
        if not batch:
            print(f"HOOK Error: Batch Auction '{batch_auction_id}' is not open for bidding.")
            return False
            
        if country.name == batch.seller.name:
            print(f"HOOK Error: Seller cannot bid.")
            return False
            
        if country.budget < (bid_price * batch.quantity):
            print(f"HOOK Error: {country.name} budget is too low.")
            return False
            
        if bid_price < batch.base_price:
            print(f"HOOK Error: Bid ${bid_price} is below base price ${batch.base_price}.")
            return False
            
        # Create and add the manual bid
        manual_bid = CountryBid(
            country=country,
            bid_price_per_unit=bid_price,
            is_manual_override=True,
            timestamp=self.turn_number
        )
        batch.add_bid(manual_bid)
        
        # Add to finalization queue
        if batch.batch_auction_id not in [b.batch_auction_id for b in self.pending_finalization]:
            self.pending_finalization.append(batch)
            
        print(f"HOOK Success: {country.name} manually bid ${bid_price:.4f} on {batch_auction_id}.")
        return True

    # --- CORE SIMULATION TURN PHASES ---

    def process_turn(self, verbosity: str = "concise"):
        """Process one complete turn of the simulation."""
        self.turn_number += 1
        if verbosity == "verbose":
            print(f"\n{'='*80}")
            print(f"PROCESSING TURN {self.turn_number}")
            print(f"{'='*80}")
        elif verbosity == "concise":
            print(f"\n--- Turn {self.turn_number} ---")
            
        # --- Phase 4 (from Previous Turn) ---
        # Finalize bids placed *last* turn before doing anything new
        self.phase4_finalize_auctions(verbosity)
        
        # --- Phase 5 (from Previous Turn) ---
        # Advance auctions that are now complete
        self.phase5_advance_auctions(verbosity)

        # --- Phase 1: AI Country Decisions ---
        new_sellers, ai_bidders = self.phase1_decide_actions(verbosity)
        
        # --- Phase 2: Process New Auctions ---
        self.phase2_create_auctions(new_sellers, verbosity)
        
        # --- Phase 3: Process AI Bids ---
        self.phase3_process_ai_bids(ai_bidders, verbosity)

    def phase1_decide_actions(self, verbosity: str) -> Tuple[List[Tuple], List[Country]]:
        """AI countries decide to SELL, BID, or NOTHING."""
        new_sellers_info = [] # (country, resource, qty, price)
        ai_bidders = []       # list of Country objects
        
        for country in self.all_countries:
            if country.name in self.countries_currently_selling:
                continue # This country is busy selling

            # --- [ADJUSTED PROBABILITY] ---
            # Probability: 30% chance to SELL, 50% chance to BID, 20% NOTHING
            rand = random.random()
            
            # --- 30% Chance to SELL ---
            if rand < 0.30: 
                # Check for surplus (helper from country.py)
                exportable_resources = country.get_export_resources()
                if exportable_resources:
                    resource_name = random.choice(exportable_resources)
                    supply = country.get_resource(resource_name).amount
                    
                    # Sell 5-20% of total supply
                    quantity = supply * random.uniform(0.05, 0.20)
                    base_price = random.uniform(0.1, 0.5) # Random base price
                    
                    if quantity > 0.01: # Don't sell dust
                        new_sellers_info.append((country, resource_name, quantity, base_price))
                        if verbosity == "verbose":
                            print(f"  Phase 1: {country.name} decided to SELL {quantity:.2f} {resource_name}")
            
            # --- 50% Chance to BID (30% to 80%) ---
            elif rand < 0.80:
                # Check for needs (helper from country.py)
                if country.get_import_needs():
                    ai_bidders.append(country)
                    if verbosity == "verbose":
                        print(f"  Phase 1: {country.name} decided to BID")
            
            # --- 20% Chance to do NOTHING ---
            else:
                if verbosity == "verbose":
                    print(f"  Phase 1: {country.name} decided to do NOTHING")
        
        if verbosity == "concise" and (new_sellers_info or ai_bidders):
            print(f"  Phase 1: {len(new_sellers_info)} new AI sellers, {len(ai_bidders)} potential AI bidders.")
        return new_sellers_info, ai_bidders

    def phase2_create_auctions(self, new_sellers_info: List[Tuple], verbosity: str):
        """Process all new SELL actions from Phase 1."""
        for (seller, resource_name, quantity, base_price) in new_sellers_info:
            auction_id = self._create_new_auction(seller, resource_name, quantity, base_price)
            if auction_id > 0:
                if verbosity == "verbose":
                    print(f"  Phase 2: {seller.name} started Auction #{auction_id} for {quantity:.2f} {resource_name}")
                elif verbosity == "concise":
                    print(f"  Phase 2: New Auction #{auction_id} ({seller.name} selling {resource_name})")


    def _create_new_auction(self, seller: Country, resource_name: str, quantity: float, base_price: float) -> int:
        """Internal helper to create a new MultiClusterAuction and its batches."""
        # --- Edge Case: Check if seller has enough to sell ---
        seller_resource = seller.get_resource(resource_name)
        if not seller_resource or seller_resource.amount < quantity:
            # Don't start the auction if they don't have the stock
            return -1 # Return an invalid ID
            
        # Mark country as busy
        self.countries_currently_selling.add(seller.name)
        
        auction_id = self.next_auction_id
        self.next_auction_id += 1
        
        # Create the parent auction
        multi_auction = MultiClusterAuction(
            auction_id=auction_id,
            seller=seller,
            resource_name=resource_name,
            total_quantity=quantity,
            base_price=base_price,
            created_turn=self.turn_number
        )
        
        # Distribute quantity and create batches (using helpers from cluster.py)
        total_countries = sum(c.country_count for c in self.all_clusters)
        
        for cluster in self.all_clusters:
            # This calculates *and* creates the batch quantities (e.g., {1: 50.0, 2: 25.0})
            cluster.assign_auction_quantity(quantity, total_countries)
            
            multi_auction.cluster_batches[cluster.name] = []
            
            for batch_num, batch_qty in cluster.auction_batches.items():
                if batch_qty <= 0:
                    continue
                
                # Create the individual batch auction
                batch_auction_id = f"{auction_id}-{cluster.name}-B{batch_num}"
                batch_auction = ClusterBatchAuction(
                    parent_auction_id=auction_id,
                    batch_auction_id=batch_auction_id,
                    batch_number=batch_num,
                    cluster=cluster,
                    seller=seller,
                    resource_name=resource_name,
                    quantity=batch_qty,
                    resource_unit=seller.get_resource(resource_name).unit,
                    base_price=base_price,
                    created_turn=self.turn_number
                )
                
                multi_auction.cluster_batches[cluster.name].append(batch_auction)
                
                # --- This is key: Only Batch 1 is open for bidding now ---
                if batch_num == 1:
                    self.open_for_bidding[batch_auction_id] = batch_auction
        
        self.active_auctions[auction_id] = multi_auction
        return auction_id

    def phase3_process_ai_bids(self, ai_bidders: List[Country], verbosity: str):
        """AI bidders scan open auctions and place Laplace bids."""
        bids_placed = 0
        for bidder in ai_bidders:
            # Find which cluster this bidder is in
            my_cluster = None
            for c in self.all_clusters:
                if bidder in c.countries:
                    my_cluster = c
                    break
            
            if not my_cluster:
                continue # Should not happen

            # Scan all auctions open for bidding
            for batch_id, batch in self.open_for_bidding.items():
                # Only bid on auctions in our own cluster
                if batch.cluster.name != my_cluster.name:
                    continue
                
                # Don't bid if we're the seller (should be caught by phase 1, but good check)
                if batch.seller.name == bidder.name:
                    continue
                
                # Do we need this resource? (helper from country.py)
                demand_res = bidder.get_demand(batch.resource_name)
                if not demand_res or demand_res.amount <= 0:
                    continue
                
                # We need it! Calculate our AI bid using Laplace
                supply_res = bidder.get_resource(batch.resource_name)
                supply = supply_res.amount if supply_res else 0.0
                
                # --- [FIXED] Call the local static method ---
                v_value, accepted = self.laplace(
                    base_price=batch.base_price,
                    supply=supply,
                    demand=demand_res.amount,
                    quantity=batch.quantity
                )
                
                if accepted:
                    ai_bid = CountryBid(
                        country=bidder,
                        bid_price_per_unit=v_value,
                        is_manual_override=False,
                        timestamp=self.turn_number
                    )
                    batch.add_bid(ai_bid)
                    
                    if verbosity == "verbose":
                        print(f"  Phase 3: {bidder.name} bid ${v_value:.4f} on {batch.batch_auction_id}")
                    
                    # This batch now has a bid, add it to be finalized next turn
                    if batch.batch_auction_id not in [b.batch_auction_id for b in self.pending_finalization]:
                        self.pending_finalization.append(batch)
                    
                    bids_placed += 1
                elif verbosity == "verbose":
                     print(f"  Phase 3: {bidder.name} REJECTED batch {batch.batch_auction_id} (v_value: ${v_value:.4f})")

        
        if verbosity == "concise" and bids_placed > 0:
            print(f"  Phase 3: {bids_placed} AI bids placed on {len(self.pending_finalization)} batches.")

    def phase4_finalize_auctions(self, verbosity: str):
        """Finalize all auctions from the previous turn."""
        if not self.pending_finalization:
            if verbosity == "verbose":
                print("  Phase 4: No auctions to finalize.")
            return

        if verbosity == "verbose":
            print(f"  Phase 4: Finalizing {len(self.pending_finalization)} batches from Turn {self.turn_number-1}...")
        elif verbosity == "concise":
            print(f"  Phase 4: Finalizing {len(self.pending_finalization)} batches from Turn {self.turn_number-1}...")
            
        finalized_count = 0
        
        for batch in self.pending_finalization:
            success, message = batch.finalize_vickrey()
            
            if success:
                finalized_count += 1
                self.completed_transactions += 1
                self.total_value_traded += (batch.final_price_per_unit * batch.quantity)
                if verbosity == "verbose":
                    print(f"    - SUCCESS: Batch {batch.batch_auction_id}. {message}")
                elif verbosity == "concise":
                    total_paid = batch.final_price_per_unit * batch.quantity
                    print(f"  Phase 4: [{batch.batch_auction_id}] SOLD {batch.quantity:.2f} {batch.resource_name} to {batch.winner.name} for ${total_paid:.2f}B.")
            else:
                 if verbosity == "verbose":
                    print(f"    - FAILED: Batch {batch.batch_auction_id}. {message}")

        if verbosity == "concise" and finalized_count > 0:
            print(f"  Phase 4: {finalized_count} transactions completed.")
            
        # Clear the queue for this turn
        self.pending_finalization.clear()

    def phase5_advance_auctions(self, verbosity: str):
        """
        Clean up finalized batches from `open_for_bidding`,
        and advance `MultiClusterAuction`s to their next batch.
        """
        # 1. Remove all finalized batches from the open bidding pool
        finalized_ids = []
        for batch_id, batch in self.open_for_bidding.items():
            if batch.is_finalized:
                finalized_ids.append(batch_id)
        
        for batch_id in finalized_ids:
            del self.open_for_bidding[batch_id]
            
        # 2. Check parent auctions to see if they can be advanced
        # Get unique parent IDs from the batches that were just finalized
        auctions_to_check = set()
        for b in self.pending_finalization: # This should check all finalized, not just pending
             if b.is_finalized:
                auctions_to_check.add(b.parent_auction_id)
        
        # A bit inefficient, but necessary if a batch finalized with no bids
        # We need to find the parent auctions of all batches that were finalized
        # This is slightly buggy, let's rethink
        
        # Let's check ALL active auctions and see if they can advance
        auctions_to_check = list(self.active_auctions.keys())

        for auction_id in auctions_to_check:
            auction = self.active_auctions.get(auction_id)
            if not auction:
                continue
                
            # Are all batches for this *current* batch number finalized?
            current_batches = auction.get_active_batches()
            if not current_batches or all(b.is_finalized for b in current_batches):
                # Yes. Advance to next batch number
                is_now_complete = auction.advance_to_next_batch()
                
                if is_now_complete:
                    # This entire multi-cluster auction is done
                    if verbosity in ("concise", "verbose"):
                        print(f"  Phase 5: Auction #{auction.auction_id} ({auction.seller.name}) is COMPLETE.")
                    if auction.seller.name in self.countries_currently_selling:
                        self.countries_currently_selling.remove(auction.seller.name)
                    del self.active_auctions[auction_id]
                else:
                    # Not complete, add the *next* batch of auctions to the open pool
                    next_batches = auction.get_active_batches() # Gets new current_batch_number
                    for b in next_batches:
                        self.open_for_bidding[b.batch_auction_id] = b
                    if verbosity in ("concise", "verbose"):
                        print(f"  Phase 5: Auction #{auction.auction_id} advanced to Batch {auction.current_batch_number}. {len(next_batches)} new batches opened.")

# -----------------------------------------------------------------
# --- EXAMPLE EXECUTION ---
# -----------------------------------------------------------------

if __name__ == "__main__":
    # 1. Initialize the simulation world
    sim = TurnBasedAuctionSystem()
    
    print("\n" + "="*80)
    print("--- STARTING PERSISTENT SIMULATION ---")
    print("--- Press Ctrl+C to stop ---")
    print("="*80)
    
    try:
        # 2. Run the simulation forever
        while True:
            # --- [FIXED] Run in VERBOSE mode ---
            sim.process_turn(verbosity="verbose")
            time.sleep(2) # 2-second delay per turn
            
    except KeyboardInterrupt:
        # 3. Stop the simulation and print final stats
        print("\n" + "="*80)
        print("--- SIMULATION STOPPED BY USER ---")
        print("--- FINAL WORLD STATE ---")
        print(f"Total Turns: {sim.turn_number}")
        print(f"Total Transactions: {sim.completed_transactions}")
        print(f"Total Value Traded: ${sim.total_value_traded:.2f}B")
        print("\n--- Country Budgets & Petroleum ---")
        for country in sim.all_countries:
            petrol = country.get_resource("PETROLEUM")
            petrol_amt = petrol.amount if petrol else 0.0
            print(f"  {country.name:<13} | Budget: ${country.budget:6.2f}B | PETROLEUM: {petrol_amt:.2f}")
        
        sys.exit(0)
