"use client"

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function AnimatedParakeet() {
  const [isFlying, setIsFlying] = useState(false)
  const [isMounted, setIsMounted] = useState(false)

  const handleClick = () => {
    setIsFlying(true)
    setTimeout(() => setIsFlying(false), 2000)
  }

  // Wait for client-side mount to use window
  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Safe defaults for SSR
  const windowWidth = isMounted && typeof window !== 'undefined' ? window.innerWidth : 1200
  const windowHeight = isMounted && typeof window !== 'undefined' ? window.innerHeight : 800

  // Generate particles only on client side
  const particles = isMounted ? [...Array(20)].map((_, i) => ({
    id: i,
    x: Math.random() * windowWidth,
    y: Math.random() * windowHeight,
    duration: 3 + Math.random() * 2,
    delay: Math.random() * 2,
  })) : []

  return (
    <div className="relative h-screen w-full bg-gradient-to-br from-[#fff7ed] to-[#fed7aa] flex items-center justify-center overflow-hidden">
      {/* Floating particles */}
      <div className="absolute inset-0">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-2 h-2 bg-orange-300/30 rounded-full"
            initial={{
              x: particle.x,
              y: particle.y,
            }}
            animate={{
              y: [null, -100],
              opacity: [0.3, 0],
            }}
            transition={{
              duration: particle.duration,
              repeat: Infinity,
              delay: particle.delay,
            }}
          />
        ))}
      </div>

      {/* Animated Parakeet */}
      <motion.div
        className="relative cursor-pointer"
        onClick={handleClick}
        whileHover={{ scale: 1.1 }}
        animate={
          isFlying
            ? {
                y: -windowHeight,
                x: windowWidth / 2,
                scale: 0.5,
              }
            : {
                y: [0, -20, 0],
              }
        }
        transition={
          isFlying
            ? {
                duration: 2,
                ease: "easeInOut",
              }
            : {
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut",
              }
        }
      >
        <svg
          width="380"
          height="380"
          viewBox="0 0 380 380"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Drop shadow filters for paper cut effect */}
            <filter id="paperShadow">
              <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
              <feOffset dx="0" dy="6" result="offsetblur"/>
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.15"/>
              </feComponentTransfer>
              <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="beakShadow">
              <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
              <feOffset dx="0" dy="3" result="offsetblur"/>
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.4"/>
              </feComponentTransfer>
              <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            <filter id="wingShadow">
              <feGaussianBlur in="SourceAlpha" stdDeviation="2.5"/>
              <feOffset dx="0" dy="4" result="offsetblur"/>
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.3"/>
              </feComponentTransfer>
              <feMerge>
                <feMergeNode/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Shadow layer (deepest) */}
          <g opacity="0.25" transform="translate(8, 8)">
            <ellipse cx="190" cy="190" rx="62" ry="80" fill="#059669"/>
            <circle cx="190" cy="120" r="42" fill="#059669"/>
          </g>

          {/* Base body layer */}
          <g filter="url(#paperShadow)">
            <ellipse cx="190" cy="185" rx="60" ry="78" fill="#10b981"/>
            <circle cx="190" cy="115" r="40" fill="#34d399"/>
          </g>

          {/* Highlight layer on body */}
          <g filter="url(#paperShadow)">
            <path d="M 160 145 Q 155 175 170 205 L 175 195 Q 165 170 160 145 Z" fill="#6ee7b7"/>
            <path d="M 180 100 Q 175 110 180 125 L 185 120 Q 182 110 180 100 Z" fill="#6ee7b7"/>
          </g>

          {/* PROMINENT CURVED BEAK - Layered paper cut style */}
          <g filter="url(#beakShadow)">
            {/* Upper beak layer (largest) */}
            <path d="M 215 115 Q 255 110 260 120 Q 257 128 245 132 Q 235 135 225 130 L 220 125 Z"
                  fill="#fb923c"/>
            {/* Middle beak layer */}
            <path d="M 220 118 Q 250 115 253 122 Q 250 127 240 129 L 225 126 Z"
                  fill="#fdba74"/>
            {/* Lower beak */}
            <path d="M 215 125 Q 240 128 245 135 Q 240 138 230 137 L 220 130 Z"
                  fill="#ea580c"/>
            {/* Beak highlight detail */}
            <ellipse cx="235" cy="120" rx="8" ry="4" fill="#fff7ed" opacity="0.6"/>
          </g>

          {/* Eye - layered */}
          <g>
            <circle cx="200" cy="110" r="9" fill="white" filter="url(#paperShadow)"/>
            <circle cx="200" cy="110" r="5" fill="#1f2937"/>
            <circle cx="201" cy="109" r="2.5" fill="white"/>
          </g>

          {/* LEFT WING - Pivots from SHOULDER, layered feathers */}
          <motion.g
            animate={{
              rotate: isFlying ? [-30, -52, -30] : [-30, -52, -30],
            }}
            transition={{
              duration: isFlying ? 0.6 : 1.2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{ transformOrigin: "145px 175px" }}
          >
            <ellipse cx="130" cy="195" rx="38" ry="70" fill="#3b82f6" opacity="0.85"
                     filter="url(#wingShadow)" transform="rotate(-30 130 195)"/>
            {/* Feather detail layers */}
            <path d="M 130 160 Q 118 185 125 220" stroke="#60a5fa" strokeWidth="3" fill="none"
                  opacity="0.7" transform="rotate(-30 130 195)"/>
            <path d="M 140 165 Q 132 185 137 215" stroke="#93c5fd" strokeWidth="2" fill="none"
                  opacity="0.6" transform="rotate(-30 130 195)"/>
          </motion.g>

          {/* RIGHT WING - Pivots from SHOULDER, layered feathers */}
          <motion.g
            animate={{
              rotate: isFlying ? [30, 52, 30] : [30, 52, 30],
            }}
            transition={{
              duration: isFlying ? 0.6 : 1.2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
            style={{ transformOrigin: "235px 175px" }}
          >
            <ellipse cx="250" cy="195" rx="38" ry="70" fill="#3b82f6" opacity="0.85"
                     filter="url(#wingShadow)" transform="rotate(30 250 195)"/>
            {/* Feather detail layers */}
            <path d="M 250 160 Q 262 185 255 220" stroke="#60a5fa" strokeWidth="3" fill="none"
                  opacity="0.7" transform="rotate(30 250 195)"/>
            <path d="M 240 165 Q 248 185 243 215" stroke="#93c5fd" strokeWidth="2" fill="none"
                  opacity="0.6" transform="rotate(30 250 195)"/>
          </motion.g>

          {/* Tail - layered feather cuts */}
          <g filter="url(#wingShadow)">
            <path d="M 178 258 Q 172 290 178 310 L 185 305 Q 182 285 178 260 Z" fill="#6366f1" opacity="0.8"/>
            <path d="M 190 258 Q 190 295 190 318 L 193 318 Q 193 295 190 260 Z" fill="#818cf8" opacity="0.9"/>
            <path d="M 202 258 Q 208 290 202 310 L 195 305 Q 198 285 202 260 Z" fill="#6366f1" opacity="0.8"/>
            {/* Tail highlights */}
            <path d="M 180 265 Q 178 280 180 295" stroke="#a5b4fc" strokeWidth="2" fill="none" opacity="0.5"/>
            <path d="M 200 265 Q 202 280 200 295" stroke="#a5b4fc" strokeWidth="2" fill="none" opacity="0.5"/>
          </g>
        </svg>

        {/* Sparkles around parakeet - warm paper cut themed */}
        {!isFlying && (
          <>
            <motion.div
              className="absolute top-10 left-10 text-3xl"
              animate={{
                scale: [1, 1.2, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0,
              }}
            >
              ✨
            </motion.div>
            <motion.div
              className="absolute top-20 right-10 text-xl"
              animate={{
                scale: [1, 1.3, 1],
                opacity: [0.4, 1, 0.4],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0.5,
              }}
            >
              🧡
            </motion.div>
            <motion.div
              className="absolute bottom-20 left-20 text-2xl"
              animate={{
                scale: [1, 1.1, 1],
                opacity: [0.6, 1, 0.6],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 1,
              }}
            >
              🍃
            </motion.div>
            <motion.div
              className="absolute top-32 right-20 text-sm"
              animate={{
                scale: [1, 1.4, 1],
                opacity: [0.3, 0.8, 0.3],
              }}
              transition={{
                duration: 2.5,
                repeat: Infinity,
                delay: 0.7,
              }}
            >
              ✨
            </motion.div>
          </>
        )}
      </motion.div>

      {/* Hint text */}
      <motion.p
        className="absolute bottom-40 text-amber-800 text-sm font-medium"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        Click the parakeet to watch it fly! 🦜
      </motion.p>
    </div>
  )
}
