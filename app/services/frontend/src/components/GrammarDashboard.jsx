import BarChart from "./BarChart";
import "../App.css";

function GrammarDashboard() {
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <BarChart 
            title="댓글 오류 비율" 
            data={[80,20]} 
            columns={["맞춤법 실패", "맞춤법 통과"]}
            colorset={["0", "2"]} selectHidden="hidden"/>
            <BarChart 
            title="맞춤법 종류 비율" 
            data={[20,30,30,20]} 
            columns={["맞춤법 오류", "띄어쓰기","표준어","통계적 오류"]}
            colorset={["0", "1", "2", "3"]} selectHidden="hidden"/>
        </div>
    )
}

export default GrammarDashboard;