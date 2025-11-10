import '../index.css'
import france from '../images/france.jpg'
import bfaso from '../images/bfaso.jpg'
import canada from '../images/canada.jpg'
import us from '../images/us.webp'
import Chart from "react-apexcharts"
import Carbon from "../images/carbon.jpg"
import Trades from "../images/trades.png"
import Fairness from "../images/fairness.png"
import {ComposableMap,Geographies,Geography} from "react-simple-maps";
import Marquee from "react-fast-marquee";
import {useEffect, useState} from "react";



const dummy_data = [
    {time:"7:10", value:101.2},
    {time:"8:00", value: 203.5},
    {time:"9:10", value:250.0},
    {time:"10:00", value: 283.5},
    {time:"11:10", value:320.3},
    {time:"12:00", value: 203.5},
    {time:"13:10", value:101.2},
    {time:"14:00", value: 155.0},
]

const leaders = [
    {country:"France", flag: france, nus_score:90, rank_change:"1↑"},
    {country:"Burkina Faso", flag: bfaso, nus_score:76, rank_change:"5↑"},
    {country:"Canada", flag: canada, nus_score:87, rank_change:"3↑"},
    {country:"U.S", flag: us, nus_score:45, rank_change:"5↓"},
    {country:"France", flag: france, nus_score:90, rank_change:"1↑"},
    {country:"Burkina Faso", flag: bfaso, nus_score:76, rank_change:"5↑"},
    {country:"Canada", flag: canada, nus_score:87, rank_change:"3↑"},
    {country:"U.S", flag: us, nus_score:45, rank_change:"5↓"},
    {country:"France", flag: france, nus_score:90, rank_change:"1↑"},
    {country:"Burkina Faso", flag: bfaso, nus_score:76, rank_change:"5↑"},
    {country:"Canada", flag: canada, nus_score:87, rank_change:"3↑"},
    {country:"U.S", flag: us, nus_score:45, rank_change:"5↓"},
]




const ScoreCards = () => {

    return(
        <div className="scorecards">

            <div className="carbon">
                <h5>Global Carbon Score </h5>

                <div>
                    <img src={Carbon} alt={"Carbon"}/>
                    <h4> 90 </h4>
                </div>

            </div>

            <div className="fairness">
                <h5>Fairness score</h5>

                <div>
                    <img src={Fairness} alt="Trades"/>
                    <h4> 85 </h4>
                </div>
            </div>

            <div className="trades">
                <h5>Trades this year</h5>

                <div>
                    <img src={Trades} alt="Trades"/>
                    <h4> 1M </h4>
                </div>
            </div>

        </div>
    )
}


const initialTickers = [
    { symbol: "TESLA", price: 195.35, change: +1.25, percent: +0.64, ecoScore: 9 },
    { symbol: "NEO-TECH", price: 87.12, change: -0.85, percent: -0.97, ecoScore: 8 },
    { symbol: "SOLAR-X", price: 34.56, change: +0.12, percent: +0.35, ecoScore: 10 },
    { symbol: "GREENCO", price: 102.45, change: -0.45, percent: -0.44, ecoScore: 7 },
];

const TickerButton = ({text, style}) => {
    return(
        <button style={style}>
            {text}
        </button>
    )
}

const marketData = [
    {
        region: "Americas",
        indices: [
            { name: "DOW JONES", value: 36025.76, net: 274.24, ytd: 17.78, ytdCur: 17.77 },
            { name: "S&P 500", value: 4733.77, net: 36.73, ytd: 25.94, ytdCur: 25.92 },
            { name: "NASDAQ", value: 15669.41, net: 149.84, ytd: 21.74, ytdCur: 21.72 },
            { name: "S&P/TSX Comp", value: 21250.15, net: 179.71, ytd: 21.83, ytdCur: 21.04 },
            { name: "S&P/BMV IPC", value: 52623.85, net: 227.20, ytd: 19.44, ytdCur: 15.34 },
            { name: "IBOVESPA", value: 104884.00, net: -360.90, ytd: -11.90, ytdCur: -19.18 },
        ]
    },
    {
        region: "EMEA",
        indices: [
            { name: "Euro Stoxx 50", value: 4265.86, net: 48.80, ytd: 20.08, ytdCur: 11.42 },
            { name: "FTSE 100", value: 7373.34, net: 31.68, ytd: 14.13, ytdCur: 12.09 },
            { name: "CAC 40", value: 7106.15, net: 54.48, ytd: 28.01, ytdCur: 18.78 },
            { name: "DAX", value: 15756.31, net: 162.84, ytd: 14.85, ytdCur: 6.57 },
            { name: "IBEX 35", value: 8563.70, net: 104.60, ytd: 6.07, ytdCur: -1.58 },
            { name: "FTSE MIB", value: 27016.22, net: 188.29, ytd: 21.51, ytdCur: 12.75 },
            { name: "OMX STKH30", value: 2385.63, net: 50.82, ytd: 27.25, ytdCur: 15.22 },
            { name: "SWISS MKT", value: 12785.32, net: 71.42, ytd: 19.45, ytdCur: 15.19 },
        ]
    },
    {
        region: "Asia/Pacific",
        indices: [
            { name: "NIKKEI", value: 28798.37, net: 236.16, ytd: 4.93, ytdCur: -5.33 },
            { name: "HAN SENG", value: 23193.64, net: 91.31, ytd: -14.83, ytdCur: -15.32 },
            { name: "CSI 300", value: 4948.74, net: 34.29, ytd: -5.04, ytdCur: -2.70 },
            { name: "S&P/ASX 200", value: 7387.57, net: 22.80, ytd: 12.15, ytdCur: 5.67 },
        ]
    }
];


const TopTickers = () => {

    return(
    <div className="top-tickers">

     <div className="top-line">
        <TickerButton text={"MSG"} style={{background:"teal"}}/>
         <TickerButton text={"PgFd"} style={{background:"teal"}}/>
         <TickerButton text={"PgBk"} style={{background:"teal"}}/>
         <TickerButton text={"MSG"} style={{background:"red"}}/>
         <TickerButton text={"PgFd"} style={{background:"yellow"}}/>
         <TickerButton text={"PgBk"} style={{background:"yellow"}}/>
         <TickerButton text={"MSG"} style={{background:"yellow"}}/>
         <TickerButton text={"PgFd"} style={{background:"lightblue"}}/>
         <TickerButton text={"PgBk"} style={{background:"blue"}}/>
         <TickerButton text={"MSG"} style={{background:"blue"}}/>
         <TickerButton text={"PgFd"} style={{background:"brown"}}/>
         <TickerButton text={"PgBk"} style={{background:"turquoise"}}/>
     </div>


            <table className="market-data">
            <thead className={"parameters"}>
            <tr>
            {Object.keys(marketData[0].indices[0]).map((key, index) => (
                <th className="parameter">
                    {key}
                </th>
            ))}
            </tr>
            </thead>

            <tbody className="region-data">
            {marketData.map((region, index)=> (
                <>
                <tr>
               <td className="region" colSpan="5">{region.region} </td>
                </tr>

                    {region.indices.map((index, key) => (
                        <tr>
                            {Object.keys(index).map((key) => (
                                <td key={key}>{index[key]}</td>
                            ))}

                        </tr>
                    ))}


                </>
            ))}
        </tbody>
            </table>


    </div>

    )
}

const BottomTickers = () => {
    const [tickers, setTickers] = useState(initialTickers);

    useEffect(() => {
        const interval = setInterval(() => {
            setTickers(prev =>
                prev.map(t => ({
                    ...t,
                    price: +(t.price + (Math.random() - 0.5) * 2).toFixed(2),
                    change: +(Math.random() - 0.5).toFixed(2),
                    percent: +(Math.random() - 0.5).toFixed(2),
                }))
            );
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ background: "#000", padding: "7px 0", fontFamily: "monospace", position: "fixed", bottom:0, zIndex:9999 }}>
            <Marquee gradient={false} speed={50}>
                {tickers.map((t, idx) => (
                    <div
                        key={idx}
                        style={{
                            display: "inline-block",
                            marginRight: "50px",
                            color: t.change >= 0 ? "#00ff00" : "#ff4500",
                        }}
                    >
                        {t.symbol}: ${t.price} ({t.change >= 0 ? "+" : ""}{t.change}, {t.percent >= 0 ? "+" : ""}{t.percent}%)
                        <span style={{ marginLeft: "5px", color: "#00ffff" }}>🌱{t.ecoScore}</span>
                    </div>
                ))}
            </Marquee>
        </div>
    );
}

const SimulationPanel = () => {

    return(
        <div>
            Simulation panel
        </div>
    )
}

const NUSTrend = () => {
    const series = [
        {
            name: "NUS Score",
            data: [78, 82, 91, 87, 94, 92, 98],
        },
    ];

    const options = {
        theme: {
            mode: "dark",
        },
        chart: {
            type: "area",
            toolbar: { show: false },
            animations: { enabled: true },
        },
        stroke: {
            curve: "smooth",
            width: 2,
        },
        fill: {
            type: "gradient",
        },
        xaxis: {
            categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        dataLabels: { enabled: false },
        tooltip: { theme: "dark" },
    };

    return (
        <div style={{ width: "100%", maxWidth: "400px", margin: "0 auto" }}>
            <h3>NUS trend</h3>
            <Chart options={options} series={series} type="area" height={300} />
        </div>
    );
}

const LeaderBoard = () => {

    return(
        <div>
            <h2>NUS Leaderboard</h2>
            <div className="leader_title">
                    <h4>Rank</h4>
                    <h4>Name</h4>
                    <h4>NUS Score</h4>
                    <h4>Rank Change </h4>
            </div>

            {leaders.map((leader, index) => (
                <div className="leader_data">
                    <p>{index+1}</p>
                    <p>{leader.country} </p>
                    <p>{leader.nus_score} </p>
                    <p>{leader.rank_change} </p>
                </div>
            ))}
        </div>
    )
}

const GlobalMap = () => {
    return(

            <div style={{width:"100%", maxWidth:"800px", margin:"0 auto", background:"#f0f0f0", padding:"20px", borderRadius:"10px"}}>
                <ComposableMap>
                    <Geographies geography="https://unpkg.com/world-atlas@1/world/110m.json">
                        {({ geographies }) =>
                            geographies.map(geo => (
                                <Geography
                                    key={geo.rsmKey}
                                    geography={geo}
                                    style={{
                                        default: { fill: "#d6d6d6" },
                                        hover: { fill: "teal" },
                                        pressed: { fill: "darkslategray" }
                                    }}
                                />
                            ))
                        }
                    </Geographies>
                </ComposableMap>
            </div>
        );


}

const MarketIndexChart = () => {
    const series = [
        {
            name: "NUS Score",
            data: [78, 82, 91, 87, 94, 92, 98],
        },
    ];

    const options = {
        theme: {
            mode: "dark",
        },
        chart: {
            type: "area",
            toolbar: { show: false },
            animations: { enabled: true },
        },
        stroke: {
            curve: "smooth",
            width: 2,
        },
        fill: {
            type: "gradient",
        },
        xaxis: {
            categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        dataLabels: { enabled: false },
        tooltip: { theme: "dark" },
    };

    return (
        <div style={{ width: "100%", maxWidth: "400px", margin: "0 auto" }}>
            <h3>Market Index Overview</h3>
            <Chart options={options} series={series} type="area" height={300} />
        </div>
    );
}


function Dashboard() {
  return (

      <>

          <h1>FluxAtlas Eco-tech Market</h1>

   <div className="dashboard">

       <div className="leaderboard">

       <LeaderBoard />

       </div>

       <div className="middle">

       <div >
            <TopTickers />
       </div>

           <div className="charts">
               <MarketIndexChart />
               <NUSTrend />
           </div>

           <div className="simulation-panel">
               <SimulationPanel />
           </div>

       <div className='worldmap'>
           <GlobalMap />
       </div>

       </div>

   </div>
          <BottomTickers />
      </>
  );
}

export default Dashboard;
