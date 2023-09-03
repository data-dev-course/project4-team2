import BarChartRateVer from "./BarChartErrorRate";
import BarChartRateVer2 from "./BarChartErrorRate2";
import "../App.css";
import Loading from "./Loading";
import { useQuery } from "@tanstack/react-query";

function error_rate_count(dataset) {
    const time = dataset[dataset.length-1]["recorded_time"];
    var len = dataset.length;

    const groupedData = dataset.reduce((accumulator, item) => {
        Object.keys(item["tags"]).map(content => { // news, webtoon, youtube, all_tags
            const error_rate = item["tags"][content]["error_rate"]
            if (!accumulator[content]) {
                accumulator[content] = []; // Initialize as an array if it's not defined
            }
            accumulator[content].push(parseFloat(error_rate));
        })
        return accumulator;
    }, {});
    Object.keys(groupedData).map(key => groupedData[key]=groupedData[key].reduce((a, b) => a + b, 0)/len)
    return [time, groupedData]
}

function error_for_types(dataset) {
    const time = dataset[dataset.length-1]["recorded_time"];
    const groupedData = dataset.reduce((accumulator, item) => {
        //console.log(item["tags"])
        Object.keys(item["tags"]).map(content => { // news, webtoon, youtube, total
            if (!accumulator[content]) {
                accumulator[content] = [[], [], [], []]; // Initialize as an array if it's not defined
            }
            [0, 1, 2, 3].map(i => 
                accumulator[content][i].push(item["tags"][content][i+1]))
        })
        return accumulator;
    }, {});
    console.log(groupedData)
    Object.keys(groupedData).map(key => //news, naver, webtoon
        groupedData[key]=groupedData[key].map(elem => elem.reduce((a, b) => a + b, 0))
    )
    console.log(groupedData)
    return [time, groupedData]
}


function GrammarDashboard() {
    const {status: status1, data: data1} = useQuery({
        queryKey: ['data-info', "error_rate"],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/grammar_state/')
            return await fetch(url)
            .then(res => res.json())
            .then(json => {return json})
        },
    })
    const {status: status2, data: data2} = useQuery({
        queryKey: ['data-info', "error_parts"],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/word_collection/word_state')
            return await fetch(url)
            .then(res => res.json())
            .then(json => {return json})
        },
    })
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            {
                status1==="loading"?<Loading/>:
                <BarChartRateVer 
                title="댓글 오류 비율" 
                data={error_rate_count(data1)}
                colorset={["0", "2"]}/>
            }
            {
                status2==="loading"?<Loading/>:
                <BarChartRateVer2 
                title="맞춤법 종류 비율" 
                data={error_for_types(data2)}
                colorset={["0", "1", "2", "3"]}/>
            }
        </div>
    )
}

export default GrammarDashboard;