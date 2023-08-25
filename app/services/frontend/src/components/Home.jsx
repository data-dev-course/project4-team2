import { useEffect, useState } from "react";
import "../App.css";

function Home() {
    const [text1, setText1] = useState("어떡게")
    const [text2, setText2] = useState("맛춤뻡")
    const [text3, setText3] = useState("틀릴수있죠")
    
    const [textStyle1, setTextStyle1] = useState("error-btn")
    const [textStyle2, setTextStyle2] = useState("error-btn")
    const [textStyle3, setTextStyle3] = useState("spacing-btn")

    return (
        <div className="grow h-full min-h-[90vh] flex flex-col justify-center items-center">
            <div className="flex flex-row items-center justify-center mb-5">
                <button className={`grammar-style ${textStyle1} mr-1.5 transition ease-in-out delay-150`} onClick={()=>{setText1("어떻게"); setTextStyle1("correct-btn")}}>{text1}</button>
                <button className={`grammar-style ${textStyle2} transition ease-in-out delay-150`} onClick={()=>{setText2("맞춤법"); setTextStyle2("correct-btn")}}>{text2}</button>
                <div className="grammar-style">을</div>
                <button className={`grammar-style ${textStyle3} ml-1.5 transition ease-in-out delay-150`} onClick={()=>{setText3("틀릴 수 있죠"); setTextStyle3("correct-btn")}}>{text3}</button>
                <div className="grammar-style">?</div>
            </div>
            <button className="bg-[#446DFF] rounded-[32px] my-5">
                SNS 속 틀린 맞춤법 알아보기
            </button>
        </div>
    )
}

export default Home;