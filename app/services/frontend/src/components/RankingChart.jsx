/* eslint-disable react/prop-types */
import "../App.css";
import { useEffect, useState } from "react";

function WordCard(props) {
    const [textStyleW, setTextStyleW] = useState("error-btn")
    const [textWord, setTextWord] = useState("")
    useEffect(()=>{
        setTextWord(props.incorrectWord);
    },[])
    return (
        <div className="my-1.5 grid grid-cols-5 justify-evenly items-center bg-white rounded-[32px] py-1.5 drop-shadow-m ">
            <div className="col-span-1 font-medium">{props.rank}</div>
            <button 
            className={`grammar-style-sm ${textStyleW} transition ease-in-out delay-150 col-span-2`} 
            onClick={()=>{setTextWord(props.correctWord); setTextStyleW("correct-btn")}}>
                {textWord}
            </button>
            <div className="font-medium text-[#c2c1c1] col-span-1 col-start-5">{props.count}회</div>
        </div>
    )
}

function Ranking(props) {
    return (
        <div className="bar-chart w-full min-w-[320px] px-1">
            <div className="chart-header w-full flex flex-row gap-4 items-baseline">
                <div className="chart-title text-lg font-bold text-left">{props.title}</div>
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
    )
}

export default Ranking;