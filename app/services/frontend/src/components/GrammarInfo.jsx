import BarChart from "./BarChart";
import "../App.css";
import DataPerTimeChart from "./LineBarGraph";
import Loading from "./Loading";
import { useQuery } from "@tanstack/react-query";

function comment_count_per_tags(dataset, hour_range) {
    const time = dataset[dataset.length-1]["recorded_time"];
    var sum_all_count = 0
    //const now = new Date();
    //const daybefore = new Date(now.getTime() - 1 * hour_range * 60 * 60 * 1000);
    //const filter_dataset = dataset.filter(item => item.recorded_time >= daybefore);
    const groupedData = dataset.reduce((accumulator, item) => {
        item["tags"].forEach((content) => {
            const content_tag = content["content_tag"]
            const content_count = content["total_comment_count"]

            if (!accumulator[content_tag]) {
                accumulator[content_tag] = []; // Initialize as an array if it's not defined
            }
            accumulator[content_tag].push(parseInt(content_count));
            
        })
        sum_all_count += parseInt(item["all_count"])
        return accumulator;
    }, {});
    Object.keys(groupedData).map(key => groupedData[key]=groupedData[key].reduce((a, b) => a + b, 0)/sum_all_count)
    return [time, groupedData]
}

function GrammarInfo() {
    const {status, data} = useQuery({
        queryKey: ['data-info', "pertags"],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/comment_count')
            const now = new Date();
            const weekbefore = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            var params = {
                start_time: weekbefore.toISOString().replace("T", " ").slice(0, 19), 
                end_time: now.toISOString().replace("T", " ").slice(0, 19)
            } 
            //console.log(params)
            url.search = new URLSearchParams(params).toString();
            return await fetch(url)
            .then(res => res.json())
            .then(json => {return json})
        },
    })
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            {
                status==="loading"?<Loading/>:
                <BarChart 
                title="댓글 수집 현황" 
                data={comment_count_per_tags(data, 24)} 
                colorset={["0", "1", "2"]} selectHidden="hidden"/>
            }
            {
                status==="loading"?<Loading/>:
                <DataPerTimeChart title="시간별 수집 현황" data={data}/>
            }
        </div>
    )
}

export default GrammarInfo;