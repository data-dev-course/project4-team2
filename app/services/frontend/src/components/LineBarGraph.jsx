import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';
import sample_data from "../assets/response_sample.json";

const colorset = [
    "#F7464A",
    "#46BFBD",
    "#FDB45C",
    "#6bb167"
]

/**
 * 
 * @param {Array<JSON>} data 
 * @returns [Array, Array]
 */
function dataSetModification(data) {
    // get the data and apply reducer; according to each time, 
    // gather the content and count value of each content.
    const groupedData = data.reduce((accumulator, item) => {
        const time = item["recorded_time"];
        if (!accumulator[time]) {
            accumulator[time] = []; // Initialize as an array if it's not defined
        }
        item["tags"].forEach((content) => {
            const content_tag = content["content_tag"]
            const content_count = content["total_comment_count"]
            accumulator[time].push({ content_tag, content_count });
        })
        return accumulator;
    }, {});
    
    const time = Object.keys(groupedData)
                .sort((a, b) => a - b); // sort by acending
                //.map(timestr => {timestr.split("T")})

    const contents = data[0].tags.map(content => content.content_tag)
    
    const datasets = contents.map((content,i) => {
        const counts = time.map(time => {
            const timeData = groupedData[time];
            const dataForContent = timeData.find(item => item.content_tag === content);
            return dataForContent ? parseInt(dataForContent.content_count) : 0;
        });
        return {
            label: content,
            data: counts,
            backgroundColor:colorset[i],
            borderColor: colorset[i],
            borderWidth: 1,
            hoverOffset: 4,
        };
    });
    return [time, datasets];
}

function BarChartTime() {
    const chartRef = useRef(null);
    //const {status, data} = useQuery(["strayanimal", "quarterdata"], async () => {
    //    const docSnap = await getDoc(doc(db, "strayanimal", "차트07_분기별_유기발생_건수"));
    //    return docSnap.data().data;
    //})
    useEffect(() => {
        //if (status === 'success' && data !== undefined) {
        //    
        let chartStatus = Chart.getChart("bar_chart_time")
        if(chartStatus !== undefined) {
            chartStatus.destroy()
        }
        const [times, datasets] = dataSetModification(sample_data)
        const ctx = chartRef.current.getContext('2d');
            window.mybarchart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: times,
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        stacked: true,
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true
                    }
                },
            },
            });
    }, [])
    //if (status === "loading") {
    //    return <Loading/>;
    //}
    return <canvas id="bar_chart_time" ref={chartRef} width="auto" height="400" />;
}

export default BarChartTime;