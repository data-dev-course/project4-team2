import BarChart from "./BarChart";
import "../App.css";
import DataPerTimeChart from "./LineBarGraph";
import Loading from "./Loading";
import { useQuery } from "@tanstack/react-query";

//console.log(import.meta.env.VITE_API_ENDPOINT);

function GrammarInfo() {
    const {status, data} = useQuery({
        queryKey: ['data-info'],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/comment_count')
            //var params = {start_time:35.696233, end_time:139.570431} 
            //url.search = new URLSearchParams(params).toString();
            const res = await fetch(url);
            return await res.json();
        },
    })
    if (status == "success") {
        console.log(data)
    }
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <BarChart 
            title="댓글 수집 현황" 
            data={[50,30,20]} 
            columns={["YouTube", "Naver News", "Naver Webtoon"]} 
            colorset={["0", "1", "2"]} selectHidden="hidden"/>
            <DataPerTimeChart title="시간별 수집 현황"/>
        </div>
    )
}

export default GrammarInfo;