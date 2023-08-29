/* eslint-disable react/prop-types */
import "../App.css";
import { useEffect, useState } from "react";

function WordCard(props) {
    const [textWord, setTextWord] = useState("")
    useEffect(()=>{
        setTextWord(props.incorrectWord);
    },[])
    return (
        <div className="my-1.5 grid grid-cols-5 justify-evenly items-center bg-white rounded-[32px] py-1.5 shadow-cm ease-in-out md:grid-cols-10">
            <div className="col-span-1 font-medium">{props.rank}</div>
            <button 
            className={`grammar-style-sm error-btn transition ease-in-out delay-150 col-span-1`} 
            onClick={()=>{}}>
                {textWord}
            </button>
            <div className="col-span-1 text-left text-[#446DFF]">{textWord}</div>
            <div className="font-medium text-[#c2c1c1] text-left col-span-1 col-start-5 md:col-start-10">{props.count}회</div>
        </div>
    )
}

function Ranking() {
    return (
        <div className="grow w-full h-full min-h-[90vh] flex flex-col justify-start items-center gap-10 py-8">
            <div className="bar-chart w-full min-w-[320px] px-1">
                <div className="chart-header w-full flex flex-row gap-4 items-baseline">
                    <div className="chart-title text-lg font-bold text-left">맞춤법 순위</div>
                    <div className="chart-time text-md text-[#c2c1c1]">
                        2023-08-23 14:00
                    </div>
                    <div className="chart-select"></div>
                </div>
                {//loop
                }
                <div className="p-1.5 grid auto-rows-auto gap-0.5">
                    <WordCard incorrectWord="어렵쓰" correctWord="어렵다" rank="1" count="697"/>
                    <WordCard incorrectWord="넓슴" correctWord="넓음" rank="2" count="950"/>
                    <WordCard incorrectWord="넓슴" correctWord="넓음" rank="3" count="950"/>
                    <WordCard incorrectWord="넓슴" correctWord="넓음" rank="4" count="950"/>
                    <WordCard incorrectWord="넓슴" correctWord="넓음" rank="5" count="950"/>
                </div>
            </div>
        </div>
    )
}

export default Ranking;