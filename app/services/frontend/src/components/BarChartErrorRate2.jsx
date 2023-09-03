/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import "../App.css";


function BarChartRateVer2(props) {
    const [valueType, setValueType] = useState("total")
    const [dataByType, setDataByType] = useState([])
    const options = {
        timeZone: 'Asia/Seoul',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric'
    };
    const [datetime, data] = props.data;

    useEffect(()=> {
        const sum_all = data["total"].reduce((a, b) =>  a + b, 0)
        setDataByType([
            data["total"][0]/sum_all*100, 
            data["total"][1]/sum_all*100, 
            data["total"][2]/sum_all*100, 
            data["total"][3]/sum_all*100
        ])
    }, [])

    useEffect(()=>{
        const sum_all = data[valueType].reduce((a, b) =>  a + b, 0)
        setDataByType([
            data[valueType][0]/sum_all*100, 
            data[valueType][1]/sum_all*100, 
            data[valueType][2]/sum_all*100, 
            data[valueType][3]/sum_all*100
        ])
    }, [valueType])

    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full grid grid-cols-12 items-baseline justify-items-start">
                <div className="col-span-9 flex flex-row items-baseline gap-2">
                    <div className="chart-title text-lg font-bold text-left">{props.title}</div>
                    <div className="chart-time text-md text-[#c2c1c1]">
                        {new Date(datetime).toLocaleString('ko-KR', options)}
                    </div>
                </div>
                <select className="chart-select rounded-[32px] px-2.5 py-0.5 text-white bg-[#3757CC] text-md col-start-10 col-span-3 justify-self-end" 
                name="valuetype" value={valueType} 
                onChange={(e) => setValueType(e.target.value)}>
                    <option value="total"> 전체 ↓</option>
                    {Object.keys(data).includes("youtube")?<option value="youtube"> 유튜브 </option>:""}
                    {Object.keys(data).includes("news")?<option value="news"> 뉴스 </option>:""}
                    {Object.keys(data).includes("webtoon")?<option value="webtoon"> 웹툰 </option>:""}
                </select>
            </div>
            
            <div className="chart min-w-[300px] flex flex-row px-2.5 py-5 min-h-fit gap-1 transition-all ease-in-out">
                <span
                className={`flex w-full bar bar-loc-0 h-4 bg-${props.colorset[0]}`} 
                style={{
                    width: `${dataByType[0]}%`,
                    borderRadius: `16px 0px 0px 16px`
                }}>
                </span>
                <span
                className={`flex w-full bar bar-loc-0 h-4 bg-${props.colorset[1]}`} 
                style={{
                    width: `${dataByType[1]}%`,
                    borderRadius: `0px`
                }}>
                </span>
                <span
                className={`flex w-full bar bar-loc-0 h-4 bg-${props.colorset[2]}`} 
                style={{
                    width: `${dataByType[2]}%`,
                    borderRadius: `0px`
                }}>
                </span>
                <span
                className={`flex w-full bar bar-loc-0 h-4 bg-${props.colorset[3]}`} 
                style={{
                    width: `${dataByType[3]}%`,
                    borderRadius: `0px 16px 16px 0px`
                }}>
                </span>
            </div>
            <div className="legend w-full min-h-fit grid grid-rows px-5 text-md text-left gap-0.5">
            {
                ["맞춤법 오류", "띄어쓰기 오류", "표준어 오류", "통계적 오류"].map((elem, i) => (
                    <div key={i} className="flex flex-row items-center gap-2">
                        <span className={`w-2.5 h-2.5 rounded-lg bg-${props.colorset[i]}`}></span>
                        <div className="font-medium">{elem}</div>
                        <div className="text-[#999797]">{dataByType.length>0?dataByType[i].toFixed(2):""}%</div>
                    </div>
                ))
            }
            </div>
        </div>
    )
}

export default BarChartRateVer2;