import BarChart from "./BarChart";
import "../App.css";
import Ranking from "./RankingChart";

function GrammarDashboard() {
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <BarChart title="댓글 수집 현황" data={[50,30,20]} columns={["YouTube", "Naver News", "Naver Webtoon"]}/>
            <BarChart title="댓글 오류 비율" data={[80,20]} columns={["맞춤법 실패", "맞춤법 통과"]}/>
            <Ranking title="오늘의 맞춤법 랭크"/>
        </div>
    )
}

export default GrammarDashboard;