/* eslint-disable react/prop-types */
import "../App.css";

function BarChart(props) {

    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full flex flex-row gap-4 items-baseline">
                <div className="chart-title text-lg font-bold text-left">{props.title}</div>
                <div className="chart-time text-md text-[#c2c1c1]">
                    2023-08-23 14:00
                </div>
                <div className="chart-select"></div>
            </div>
            <div className="chart min-w-[280px] p-5 min-h-fit grid grid-cols-10 gap-1">
                {
                    props.data.map((elem, i) => (
                        <span key={i} 
                        className={`bar bar-loc-${i} h-4 bg-${i}`} 
                        style={{
                            gridColumn: `span ${elem/10} / span ${elem/10}`,
                            borderRadius: `${i===0?16:0}px ${i===props.data.length-1?16:0}px ${i===props.data.length-1?16:0}px ${i===0?16:0}px`
                        }}></span>
                    ))
                }
            </div>
            <div className="legend w-full min-h-fit grid grid-rows px-5 text-md text-left gap-0.5">
                {
                    props.columns.map((elem, i) => (
                        <div key={i} className="flex flex-row items-center gap-2">
                            <span className={`w-2.5 h-2.5 rounded-lg bg-${i}`}></span>
                            <div className="font-medium">{elem}</div>
                            <div className="text-[#999797]">{props.data[i]}%</div>
                        </div>
                    ))
                }
            </div>
        </div>
    )
}

export default BarChart;