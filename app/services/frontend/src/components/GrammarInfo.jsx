import BarChart from "./BarChart";
import "../App.css";
import BarChartTime from "./LineBarGraph";

function GrammarInfo() {
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <BarChart 
            title="댓글 수집 현황" 
            data={[50,30,20]} 
            columns={["YouTube", "Naver News", "Naver Webtoon"]} 
            colorset={["0", "1", "2"]}/>
            <BarChartTime/>
        </div>
    )
}

export default GrammarInfo;