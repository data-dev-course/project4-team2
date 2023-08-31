import "../App.css";

function Error404() {
    return (
        <div className="min-h-[90vmax] flex flex-col justify-center">
            <div className="text-[#446DFF] font-black text-[32px] py-2.5">404 NOT FOUND</div>
            <div className="text-md">존재하지 않는 페이지입니다.</div>
            <a href="/" className="px-2.5 py-2.5 my-4 rounded-[32px] bg-[#446DFF] text-white font-bold">홈으로 돌아가기</a>
        </div>
    )
}

export default Error404;