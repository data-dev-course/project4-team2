import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import './App.css'

export function HambergerMenu() {
  const [hamClass, setHamClass] = useState("ham_menu");
  const handleSidebarClose = () => {
      setHamClass("ham_menu");
      const checkbox = document.getElementById("burger-check");
      checkbox.checked = false;
  }
  return (
      <div className="burger_menu_wrap">
          <input className="burger-check" type="checkbox" id="burger-check" />
          <label href="#" className={hamClass} htmlFor="burger-check"
          onClick={()=>{
              if (hamClass === "ham_menu") {setHamClass(`${hamClass} ham_expand`)}
              else {setHamClass("ham_menu")}
          }}>
              <span>메뉴</span>
          </label>
          <button className='bg-[#FFCC00] hidden top-0'>맞춤법 알아보기</button>
          <button className='bg-[#FFCC00] hidden top-0'>분석 대시보드</button>
      </div>
  );
}

function App() {
  return (
    <div className='w-full h-full flex flex-col justify-center align-center items-center'>
      <header className='w-full h-[40px] order-first sticky flex flex-row justify-between bg-[#f9fafc]'>
        <div className='logo'>KORRECT</div>
        <HambergerMenu/>
      </header>
      <Outlet/>
      <footer className='w-full h-auto py-5 bg-[#446DFF] order-last'>
        <div className='logo text-white p-2'>KORRECT</div>
        <div className='text-white font-bold'>데브코스 데이터 엔지니어링 FINAL</div>
        <div className='text-white font-bold mb-1'>[1기] 3팀 2조</div>
        <div className='text-white'><div>강다혜 @kangdaia</div><div>전성현 @Jeon-peng</div><div>조윤지 @joyunji</div></div>
      </footer>
    </div>
  )
}

export default App
