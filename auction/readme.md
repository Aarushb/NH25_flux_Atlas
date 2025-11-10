File: turn_based_simulation.py — main implementation: TurnBasedSimulation, BatchAuction, ClusterAuctionState
Valuation helper: AuctionManager.laplace
Models used: Country, Resource, ClusterInfo, cluster list CountryClusters
Summary (concise)

Countries act once per turn in TurnBasedSimulation.country_turn, which calls decide_action to choose between: NOTHING, BID, START_AUCTION.
Bidding uses a Laplace valuation from AuctionManager.laplace to compute a per-unit v_value and an acceptance flag; bids are stored on BatchAuction.bids via BatchAuction.add_bid.
Auctions are cluster-based: starting a cluster auction (start_cluster_auction) calls each cluster's ClusterInfo.assign_auction_quantity to split the seller's total quantity into per-cluster batch quantities; per-cluster BatchAuctions are created by ClusterAuctionState.create_batch_auctions_for_turn.
Each batch runs for 4 rounds (BatchAuction.rounds_remaining), advanced by advance_all_batches. Finalization uses a Vickrey (second-price) rule in BatchAuction.finalize: winner pays second-highest bid (or base price if single bidder). On finalize, money and resource amounts are transferred immediately (seller.resource.amount decreases; buyer.resource.amount increases).
Countries that are selling (tracked in TurnBasedSimulation.countries_currently_selling) cannot place bids while selling.
Demand in the simulation: countries' demand is read from Country.demand to decide whether to bid; the turn-based simulation does not mutate demand entries itself — only resource amounts and budgets are changed on sale finalization.
Algorithm (step-by-step / pseudocode)
# TurnBasedSimulation main loop (simplified)
for turn in 1..max_turns:
    for country in all_countries:
        action = decide_action(country)
        if action.type == "BID":
            # place_bid_on_batch uses AuctionManager.laplace(base_price, supply, demand, quantity)
            # if accepted -> BatchAuction.add_bid(country, v_value)
        elif action.type == "START_AUCTION":
            # start_cluster_auction:
            #  - check seller has resource
            #  - compute per-cluster quantities via ClusterInfo.assign_auction_quantity(total_quantity, world_total)
            #  - create ClusterAuctionState and create batch #1 across clusters
            #  - mark seller as currently selling (countries_currently_selling)
    # advance all active batch auctions: decrement rounds_remaining
    # finalize batches with rounds_remaining == 0:
    #  - BatchAuction.finalize sorts bids desc, winner = top bid
    #  - price_per_unit = second_highest_v_value or base_price
    #  - transfer money (winner.budget -= total_cost; seller.budget += total_cost)
    #  - transfer resources (seller.resources[res].amount -= quantity; winner.resources[res].amount += quantity)
    #  - mark batch completed and move to completed_batch_auctions
    # progress cluster auctions:
    #  - when all clusters' batches for current batch_number are completed:
    #    - if more batches remain: create next batch auctions across clusters
    #    - else: mark cluster auction complete and allow seller to sell again

Important details / rules extracted from code

Who can bid: any country that is not currently selling and that belongs to the batch's cluster (country ∈ cluster.countries) and has positive demand for the resource — see decide_action.
Bid uniqueness and affordability: BatchAuction.add_bid rejects duplicate bids from same country and verifies bidder has budget >= v_value * quantity.
Bid valuation: AuctionManager.laplace(base_price, supply, demand, quantity) returns (v_value, accepted); the simulation uses that v_value as the per-unit bid when adding a bid — see place_bid_on_batch.
Auction mechanics:
Batches live for 4 rounds (configured by BatchAuction.rounds_remaining default).
Finalize uses Vickrey pricing: winner pays second-highest v_value (or base price if single bidder).
If winner cannot afford final cost at finalize time, the batch fails (no transfer).
Supply/demand mutation:
Supply (resource amounts) changes only when a batch finalizes: seller.resource.amount decreases and winner.resource.amount increases.
Budgets change at finalize (money transfers).
Demand entries are read-only in this simulation code (no demand updates are performed here).
Seller restrictions:
While a seller has an active cluster auction (some batches not yet finished), they are in countries_currently_selling and cannot bid nor start another auction.
Pointers to read exact implementations

Main simulation and decisions: turn_based_simulation.py — see methods: decide_action, start_cluster_auction, place_bid_on_batch, advance_all_batches, finalize_completed_batches, progress_cluster_auctions.
Bid valuation: AuctionManager.laplace.
Country model and accessors: Country including get_resource, get_demand, fields resources, demand, budget.
Cluster distribution helpers: ClusterInfo methods get_batch_quantity and assign_auction_quantity, and cluster list: CountryClusters.
Resource type: Resource.