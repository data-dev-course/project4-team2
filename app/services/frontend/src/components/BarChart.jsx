/* eslint-disable react/prop-types */
import { useState } from "react";
import "../App.css";

function BarChart(props) {
    const [valueType, setValueType] = useState("all")
    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full flex flex-row gap-4 items-baseline justify-start">
                <div className="chart-title text-lg font-bold text-left">{props.title}</div>
                <div className="chart-time text-md text-[#c2c1c1]">
                    2023-08-23 14:00
                </div>
            </div>
            <div className={`w-full flex justify-end pt-2 ${props.selectHidden}`}>
                <select className="chart-select rounded-[32px] px-2.5 py-0.5 text-white bg-[#3757CC] text-md" 
                    name="valuetype" value={valueType} 
                    onChange={(e) => setValueType(e.target.value)}>
                        <option value="all"> 전체 ↓</option>
                        <option value="youtube"> 유튜브 </option>
                        <option value="news"> 뉴스 </option>
                        <option value="news"> 웹툰 </option>
                </select>
            </div>
            <div className="chart min-w-[300px] px-2.5 py-5 min-h-fit grid grid-cols-10 gap-1">
                {
                    props.data.map((elem, i) => (
                        <span key={i} 
                        className={`bar bar-loc-${i} h-4 bg-${props.colorset[i]}`} 
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
                            <span className={`w-2.5 h-2.5 rounded-lg bg-${props.colorset[i]}`}></span>
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