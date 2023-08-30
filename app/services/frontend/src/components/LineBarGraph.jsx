/* eslint-disable react/prop-types */
import React, { useEffect, useRef, useState } from 'react';
import Chart from 'chart.js/auto';
import "../App.css";
import sample_data from "../assets/response_sample.json";

const colorset = [
    "#fa5e68",
    "#FFD644",
    "#46BFBD",
]

/**
 * 
 * @param {Array<JSON>} data 
 * @returns [Array, Array]
 */
function dataSetModification(data, group, date_type) {
    // get the data and apply reducer; according to each time, 
    // gather the content and count value of each content.
    const groupedData = data.reduce((accumulator, item) => {
        const time = item["recorded_time"];
        
        item["tags"].forEach((content) => {
            const content_tag = content["content_tag"]
            const content_count = content["total_comment_count"]
            if (date_type === "hours") { // 오늘치만
                const today = new Date();
                if (time.includes(today.toISOString().substring(0, 10))) {
                    let only_time = time.substring(11,16)
                    if (!accumulator[only_time]) {
                        accumulator[only_time] = []; // Initialize as an array if it's not defined
                    }
                    accumulator[only_time].push({ content_tag, content_count });
                }
            } else if (date_type === "days") { // 하루씩 모아서
                const only_date = time.substring(0, 10);
                if (!accumulator[only_date]) {
                    accumulator[only_date] = []; // Initialize as an array if it's not defined
                }
                accumulator[only_date].push({ content_tag, content_count });
            }
        })
        return accumulator;
    }, {});
    
    const time = Object.keys(groupedData)
                .sort((a, b) => a - b);

    const contents = group
    
    const datasets = contents.map((content,i) => {
        const counts = time.map(time => {
            const timeData = groupedData[time];
            const dataForContent = timeData.find(item => item.content_tag === content);
            return dataForContent ? parseInt(dataForContent.content_count) : 0;
        });
        return {
            label: content.charAt(0).toUpperCase() + content.slice(1),
            data: counts,
            backgroundColor:colorset[i],
            borderColor: colorset[i],
            borderWidth: 1,
            borderRadius: 8,
            hoverOffset: 4,
        };
    });
    return [time, datasets];
}

function BarChartTime(props) {
    const chartRef = useRef(null);
    //const {status, data} = useQuery(["strayanimal", "quarterdata"], async () => {
    //    const docSnap = await getDoc(doc(db, "strayanimal", "차트07_분기별_유기발생_건수"));
    //    return docSnap.data().data;
    //}
    const chartSetting = (labels, datasets) => {
        const ctx = chartRef.current.getContext('2d');
            window.mybarchart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: "#000"
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: false,
                        grid: {
                            display: false
                        },
                        ticks: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        align: 'center',
                        labels: {
                            boxWidth: 8,
                            boxHeight: 8,
                            padding: 12,
                            usePointStyle: true,
                            pointStyle: "circle",
                            color: '#000',
                            font: {
                                size: 16,
                                weight: 400
                            }
                        }
                    }
                },
            }
        });
    }
    useEffect(() => {
        //if (status === 'success' && data !== undefined) {
         
        let chartStatus = Chart.getChart("bar_chart_time")
        if(chartStatus !== undefined) {
            chartStatus.destroy()
        }
        const [times, datasets] = dataSetModification(sample_data, ["youtube", "news", "webtoon"], props.dateType)
        chartSetting(times, datasets)
        
    }, [props.dateType])
    //if (status === "loading") {
    //    return <Loading/>;
    //}
    return <canvas id="bar_chart_time" ref={chartRef} width="auto" height="400" className='md:max-h-96'/>;
}

function DataPerTimeChart(props) {
    const [dateType, setDateType] = useState("hours")
    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full flex flex-row gap-4 items-baseline justify-between">
                <div className="chart-title text-lg font-bold text-left">{props.title}</div>
                <div className="chart-time text-md text-[#c2c1c1]">
                </div>
                <select className="chart-select rounded-[32px] px-2.5 py-0.5 text-white bg-[#3757CC] text-md" 
                name="datetype" value={dateType} 
                onChange={(e) => setDateType(e.target.value)}>
                    <option value="hours"> 시간 ↓</option>
                    <option value="days"> 하루 ↓</option>
                </select>
            </div>
            <div className="chart min-w-[280px] py-5 min-h-fit flex justify-center gap-1">
                <BarChartTime dateType={dateType}/>
            </div>
        </div>
    );
}

export default DataPerTimeChart;