$baseUrl = "http://localhost:8000"

# 1. Create groups first
$groups = @(
    @{name="Low Income"; low_ppp=0; high_ppp=5000; description="Least developed"},
    @{name="Lower-Middle Income"; low_ppp=5001; high_ppp=15000; description="Developing nations"},
    @{name="Upper-Middle Income"; low_ppp=15001; high_ppp=30000; description="Emerging markets"},
    @{name="High Income"; low_ppp=30001; high_ppp=100000; description="Developed economies"}
)

foreach ($group in $groups) {
    $body = $group | ConvertTo-Json
    Invoke-RestMethod -Uri "$baseUrl/groups" -Method Post -Body $body -ContentType "application/json"
}

# 2. Get group IDs
$groupsList = Invoke-RestMethod -Uri "$baseUrl/groups" -Method Get
$highIncomeGroup = $groupsList | Where-Object { $_.name -eq "High Income" } | Select-Object -First 1

# 3. Create United States
$usa = @{
    cname = "United States"
    ppp = 85810
    carbon_budget = 5000.0
    group_id = $highIncomeGroup.id
} | ConvertTo-Json

$usaResult = Invoke-RestMethod -Uri "$baseUrl/countries" -Method Post -Body $usa -ContentType "application/json"

# 4. Create Lithium resource
$lithium = @{
    rname = "Lithium"
    price = 200.0
    description = "tonnes"
} | ConvertTo-Json

$lithiumResult = Invoke-RestMethod -Uri "$baseUrl/resources" -Method Post -Body $lithium -ContentType "application/json"

# 5. Link USA to Lithium
$usaLithium = @{
    country_id = $usaResult.id
    resource_id = $lithiumResult.id
    supply = 1000
    demand = 200
    quantity = 1000.0
    unit = "tonnes"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/resources/country-resources" -Method Post -Body $usaLithium -ContentType "application/json"

Write-Host "Setup complete!" -ForegroundColor Green