/* eslint-disable react/prop-types */
import { useState } from "react";
import "../App.css";

function BarChart(props) {
    const [valueType, setValueType] = useState("all")
    const options = {
        timeZone: 'Asia/Seoul',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: 'numeric'
    };
    const [datetime, data] = props.data;
    //console.log(props.data)
    const bar_elements = Object.keys(data).map(function(key, index) {
        const value = data[key].toFixed(2);
        //console.log(value);
        return (
            <span key={index} 
                  className={`flex w-full bar bar-loc-${index} h-4 bg-${props.colorset[index]}`} 
                  style={{
                      width: `${value*100}%`,
                      borderRadius: `${index===0?16:0}px ${index===Object.keys(data).length-1?16:0}px ${index===Object.keys(data).length-1?16:0}px ${index===0?16:0}px`
                  }}>
            </span>
        );
    });

    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full flex flex-row gap-4 items-baseline justify-start">
                <div className="chart-title text-lg font-bold text-left">{props.title}</div>
                <div className="chart-time text-md text-[#c2c1c1]">
                    {new Date(datetime).toLocaleString('ko-KR', options)
                    }
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
            <div className="chart min-w-[300px] flex flex-row px-2.5 py-5 min-h-fit gap-1">
                {bar_elements
                }
            </div>
            <div className="legend w-full min-h-fit grid grid-rows px-5 text-md text-left gap-0.5">
                {
                    Object.keys(data).map((elem, i) => (
                        <div key={i} className="flex flex-row items-center gap-2">
                            <span className={`w-2.5 h-2.5 rounded-lg bg-${props.colorset[i]}`}></span>
                            <div className="font-medium">{elem.charAt(0).toUpperCase() + elem.slice(1)}</div>
                            <div className="text-[#999797]">{(data[elem]*100).toFixed(2)}%</div>
                        </div>
                    ))
                }
            </div>
        </div>
    )
}

export default BarChart;