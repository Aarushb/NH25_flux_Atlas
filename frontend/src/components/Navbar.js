import {useState} from "react";
import Dropdown from '../components/ui/dropdown-menu'; // Import the reusable component
import '../index.css'


const countries = [
    "World",
    "Somalia",
    "Mozambique",
    "Chad",
    "Haiti",
    "Pakistan",
    "Nigeria",
    "Kenya",
    "Bangladesh",
    "India",
    "South Africa",
    "Sri Lanka",
    "Indonesia",
    "Vietnam",
    "Iran",
    "Brazil",
    "China",
    "Azerbaijan",
    "Chile",
    "Oman",
    "Latvia",
    "Slovakia",
    "Russia",
    "Kuwait",
    "Japan",
    "France",
    "Saudi Arabia",
    "Germany",
    "United States",
    "Switzerland",
    "Australia",
];

const resources = ["Aluminum", "Oil", "Natural Gas", "Uranium"];


const Navbar = () => {
    // Set the default country from your list
    const [selectedCountry, setSelectedCountry] = useState(countries[0]);

    return (
        <nav className="navbar">
            <div className="nav-links">
                {/* === Country Dropdown === */}
                <Dropdown
                    trigger={
                        <button className="nav-button">
                            {selectedCountry} <span className="arrow">▼</span>
                        </button>
                    }
                >
                    {/* We map over the countries list to create the menu items.
            The onClick handler updates the selected country.
          */}
                    {countries.map((country) => (
                        <button
                            key={country}
                            className="dropdown-item"
                            onClick={() => setSelectedCountry(country)}
                        >
                            {country}
                        </button>
                    ))}
                </Dropdown>

                {/* === Resources Dropdown === */}
                <Dropdown
                    trigger={
                        <button className="nav-button">
                            <span>Resources</span>
                            <span>▼</span>
                        </button>
                    }
                >
                    {/* This loop now correctly handles an array of strings */}
                    {resources.map((resource) => (

                            {resource}

                    ))}
                </Dropdown>
            </div>
        </nav>
    );
}

export default Navbar