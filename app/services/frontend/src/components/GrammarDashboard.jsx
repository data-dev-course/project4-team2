import BarChart from "./BarChart";
import "../App.css";
import Loading from "./Loading";
import { useQuery } from "@tanstack/react-query";

function GrammarDashboard() {
    const {status, data_error_rate} = useQuery({
        queryKey: ['data-info', "error_rate"],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/grammar_state')
            //const now = new Date();
            //const weekbefore = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            //var params = {
            //    start_time: weekbefore.toISOString().replace("T", " ").slice(0, 19), 
            //    end_time: now.toISOString().replace("T", " ").slice(0, 19)
            //} 
            //url.search = new URLSearchParams(params).toString();
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
                title="댓글 오류 비율" 
                data={[80,20]}
                colorset={["0", "2"]} selectHidden="hidden"/>
            }
            {
                status==="loading"?<Loading/>:
                <BarChart 
                title="맞춤법 종류 비율" 
                data={[20,30,30,20]}
                colorset={["0", "1", "2", "3"]} selectHidden="hidden"/>
            }
        </div>
    )
}

export default GrammarDashboard;