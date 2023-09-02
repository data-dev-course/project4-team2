/* eslint-disable react/prop-types */
import "../App.css";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Loading from "./Loading";

const colorset = [
    "#fa5e68",
    "#FFD644",
    "#46BFBD",
    "#d271ec"
]

function WordCard(props) {
    const [textWord, setTextWord] = useState("")
    useEffect(()=>{
        setTextWord(props.incorrectWord);
    },[])
    return (
        <div className="my-1.5 grid grid-cols-6 justify-evenly items-center bg-white rounded-[32px] py-1.5 shadow-cm ease-in-out md:grid-cols-10">
            <div className="col-span-1 font-medium">{props.rank}</div>
            <button 
            className={`grammar-style-sm transition ease-in-out delay-150 col-span-2 text-left`} 
            style = {{
                borderBottom: `2px solid ${colorset[parseInt(props.error_type)-1]}`,
                wordWrap: 'break-word'
            }}
            onClick={()=>{}}>
                {textWord}
            </button>
            <div className="col-span-2 text-left text-[#446DFF] break-keep">{props.correctWord}</div>
            <div className="font-medium text-[#c2c1c1] text-left col-span-1 col-start-6 md:col-start-10">{props.count}회</div>
        </div>
    )
}

function Ranking() {
    const {status, data} = useQuery({
        queryKey: ['data-info', "ranking"],
        queryFn: async () => {
            var url = new URL(import.meta.env.VITE_API_ENDPOINT+'/word_collection/rank')
            const now = new Date();
            const hourbefore = new Date(now.getTime() - 1 * 2 * 60 * 60 * 1000);
            var params = {
                start_time: hourbefore.toISOString().replace("T", " ").slice(0, 19), 
                end_time: now.toISOString().replace("T", " ").slice(0, 19)
            }
            //console.log(params)
            url.search = new URLSearchParams(params).toString();
            return await fetch(url)
            .then(res => res.json())
            .then(json => { 
                return json[json.length-1];
            })
        },
    })
    const options = {
        timeZone: 'Asia/Seoul',
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: 'numeric'
    };

    if (status === "loading") {
        return <div className="min-h-[90vh] flex justify-center items-center"><Loading/></div>
    }
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <div className="bar-chart w-full min-w-[320px] px-1">
                <div className="chart-header w-full flex flex-row gap-4 items-baseline">
                    <div className="chart-title text-lg font-bold text-left">맞춤법 순위</div>
                    <div className="chart-time text-md text-[#c2c1c1]">
                        {new Date(data["recorded_time"]).toLocaleString('ko-KR', options)}
                    </div>
                    <div className="chart-select"></div>
                </div>
                
                <div className="p-1.5 grid auto-rows-auto gap-0.5">
                {
                    Object.keys(data["total"]["rank"]).map(rank => 
                        <WordCard key={rank}
                        incorrectWord={data["total"]["rank"][rank]["incorrect_word"]} 
                        correctWord={data["total"]["rank"][rank]["correct_word"]} 
                        rank={rank} 
                        error_type={data["total"]["rank"][rank]["check_result"]}
                        count={data["total"]["rank"][rank]["occurrence_count"]}/>
                    )
                }
                </div>
            </div>
        </div>
    )
}

export default Ranking;