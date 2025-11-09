from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from resources import Resource
from country import Country


class AuctionStatus(Enum):
    """Status of an auction."""
    PENDING = "pending"
    BIDDING_OPEN = "bidding_open"
    BIDDING_CLOSED = "bidding_closed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Bid:
    """Represents a sealed bid in an auction."""
    country: Country
    bid_price_per_unit: float  # Price per unit bidder is willing to pay
    timestamp: datetime = field(default_factory=datetime.now)
    is_revealed: bool = False
    
    def get_total_bid(self, quantity: float) -> float:
        """Calculate total bid amount for given quantity."""
        return self.bid_price_per_unit * quantity
    
    def __repr__(self) -> str:
        if self.is_revealed:
            return f"Bid(country={self.country.name}, price_per_unit=${self.bid_price_per_unit:.2f})"
        else:
            return f"Bid(country={self.country.name}, price=SEALED)"


@dataclass
class Auction:
    """Represents a single sealed-bid auction."""
    seller: Country
    resource_name: str
    quantity: float
    resource_unit: str
    asking_price_per_unit: float  # Seller's asking price per unit
    current_market_price: float   # Current market price per unit
    status: AuctionStatus = AuctionStatus.PENDING
    bids: List[Bid] = field(default_factory=list)
    winner: Optional[Country] = None
    final_price_per_unit: Optional[float] = None
    
    @property
    def total_asking_price(self) -> float:
        """Total price seller is asking for."""
        return self.asking_price_per_unit * self.quantity
    
    @property
    def total_market_value(self) -> float:
        """Total market value of the resource."""
        return self.current_market_price * self.quantity
    
    @property
    def final_total_price(self) -> Optional[float]:
        """Total final price if auction is completed."""
        if self.final_price_per_unit:
            return self.final_price_per_unit * self.quantity
        return None
    
    def open_bidding(self) -> bool:
        """Open the auction for bidding."""
        if not self.seller.has_resource(self.resource_name):
            return False
        
        seller_resource = self.seller.get_resource(self.resource_name)
        if seller_resource.amount < self.quantity:
            return False
        
        self.status = AuctionStatus.BIDDING_OPEN
        return True
    
    def submit_bid(self, country: Country, bid_price_per_unit: float) -> bool:
        """Submit a sealed bid."""
        if self.status != AuctionStatus.BIDDING_OPEN:
            return False
        
        if country == self.seller:
            return False
        
        # Calculate total bid amount
        total_bid = bid_price_per_unit * self.quantity
        
        # Check if country has enough budget
        if country.budget < total_bid:
            return False
        
        # Check if bid meets asking price
        if bid_price_per_unit < self.asking_price_per_unit:
            return False
        
        # Check if country already bid
        for bid in self.bids:
            if bid.country == country:
                return False
        
        # Submit sealed bid
        bid = Bid(country=country, bid_price_per_unit=bid_price_per_unit, is_revealed=False)
        self.bids.append(bid)
        return True
    
    def close_bidding(self) -> bool:
        """Close bidding for this auction."""
        if self.status != AuctionStatus.BIDDING_OPEN:
            return False
        
        self.status = AuctionStatus.BIDDING_CLOSED
        return True
    
    def reveal_bids(self) -> None:
        """Reveal all sealed bids."""
        if self.status != AuctionStatus.BIDDING_CLOSED:
            return
        
        for bid in sorted(self.bids, key=lambda b: b.bid_price_per_unit, reverse=True):
            bid.is_revealed = True
            total = bid.get_total_bid(self.quantity)
    
    def determine_winner(self) -> bool:
        """Determine the winner and complete the transaction."""
        if self.status != AuctionStatus.BIDDING_CLOSED:
            return False
        
        if not self.bids:
            self.status = AuctionStatus.CANCELLED
            return False
        
        # Reveal all bids
        self.reveal_bids()
        
        # Find highest bid
        highest_bid = max(self.bids, key=lambda b: b.bid_price_per_unit)
        winner = highest_bid.country
        final_price_per_unit = highest_bid.bid_price_per_unit
        total_price = final_price_per_unit * self.quantity
        
        # Transfer resource from seller to winner
        seller_resource = self.seller.get_resource(self.resource_name)
        seller_resource.amount -= self.quantity
        
        # Add to winner's resources
        if winner.has_resource(self.resource_name):
            winner.resources[self.resource_name].amount += self.quantity
        else:
            winner.resources[self.resource_name] = Resource(self.quantity, self.resource_unit)
        
        # Transfer money
        winner.budget -= total_price
        self.seller.budget += total_price
        
        # Update auction status
        self.winner = winner
        self.final_price_per_unit = final_price_per_unit
        self.status = AuctionStatus.COMPLETED
        
        
        return True
    
    def __repr__(self) -> str:
        return f"Auction({self.resource_name}, seller={self.seller.name}, quantity={self.quantity}, status={self.status.value})"
    
