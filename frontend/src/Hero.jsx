import React from 'react'
import Carousel from './componants/Carousel'
const Hero = () => {
  return (
    <section className='w-full flex xl:flex-row flex-col justify-center min-h-screen gap-10 max-container'>

      <div className='relative flex justify-center items-start w-full max-xl:padding-x'>
       <Carousel />

      </div>
    </section>
  )
}

export default Hero