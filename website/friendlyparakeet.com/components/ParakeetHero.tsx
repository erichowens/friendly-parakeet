"use client"

import { Canvas, useFrame } from '@react-three/fiber'
import { Environment, Float, OrbitControls, Sparkles, useGLTF } from '@react-three/drei'
import { EffectComposer, Bloom, ChromaticAberration, Vignette } from '@react-three/postprocessing'
import { useRef, useMemo } from 'react'
import * as THREE from 'three'

// Iridescent Feather Shader
const IridescentFeatherMaterial = () => {
  const vertexShader = `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;

    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewPosition = -mvPosition.xyz;
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * mvPosition;
    }
  `

  const fragmentShader = `
    uniform float time;
    uniform vec3 color1;
    uniform vec3 color2;
    uniform vec3 color3;

    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;

    vec3 getIridescence(float angle) {
      float shift = sin(angle * 3.0) * 0.5 + 0.5;
      vec3 col1 = mix(color1, color2, shift);
      vec3 col2 = mix(color2, color3, 1.0 - shift);
      return mix(col1, col2, sin(angle * 5.0 + time) * 0.5 + 0.5);
    }

    void main() {
      vec3 viewDir = normalize(vViewPosition);
      vec3 normal = normalize(vNormal);

      // Calculate viewing angle for iridescence
      float angle = dot(viewDir, normal);
      angle = acos(angle);

      // Get iridescent color
      vec3 iridescent = getIridescence(angle);

      // Add shimmer based on world position
      float shimmer = sin(vWorldPosition.x * 10.0 + time * 2.0) *
                     sin(vWorldPosition.y * 10.0 + time * 1.5) * 0.1 + 0.9;

      // Feather texture pattern
      float featherPattern = sin(vUv.x * 50.0) * sin(vUv.y * 100.0) * 0.1 + 0.9;

      vec3 finalColor = iridescent * shimmer * featherPattern;

      // Add rim lighting
      float rim = 1.0 - max(0.0, dot(viewDir, normal));
      rim = pow(rim, 2.0);
      finalColor += vec3(0.3, 0.8, 0.4) * rim * 0.5;

      gl_FragColor = vec4(finalColor, 1.0);
    }
  `

  const uniforms = useMemo(() => ({
    time: { value: 0 },
    color1: { value: new THREE.Color(0x00ff88) }, // Bright green
    color2: { value: new THREE.Color(0x00aaff) }, // Sky blue
    color3: { value: new THREE.Color(0xffaa00) }, // Golden yellow
  }), [])

  useFrame((state) => {
    uniforms.time.value = state.clock.elapsedTime
  })

  return (
    <shaderMaterial
      vertexShader={vertexShader}
      fragmentShader={fragmentShader}
      uniforms={uniforms}
      side={THREE.DoubleSide}
    />
  )
}

// Stylized 3D Parakeet Component
function StylizedParakeet() {
  const meshRef = useRef<THREE.Mesh>(null)
  const wingLeftRef = useRef<THREE.Mesh>(null)
  const wingRightRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle floating animation
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
      meshRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1
    }

    // Wing flapping animation
    if (wingLeftRef.current && wingRightRef.current) {
      const flap = Math.sin(state.clock.elapsedTime * 3) * 0.2
      wingLeftRef.current.rotation.z = -0.3 + flap
      wingRightRef.current.rotation.z = 0.3 - flap
    }
  })

  return (
    <group>
      {/* Main body */}
      <mesh ref={meshRef} castShadow receiveShadow>
        <sphereGeometry args={[1, 32, 32]} />
        <IridescentFeatherMaterial />
      </mesh>

      {/* Head */}
      <mesh position={[0, 1.2, 0.3]} castShadow>
        <sphereGeometry args={[0.6, 32, 32]} />
        <IridescentFeatherMaterial />
      </mesh>

      {/* Beak */}
      <mesh position={[0, 1.2, 0.8]} rotation={[Math.PI / 2, 0, 0]}>
        <coneGeometry args={[0.15, 0.4, 8]} />
        <meshStandardMaterial color="#ff6b35" metalness={0.3} roughness={0.4} />
      </mesh>

      {/* Eyes */}
      <mesh position={[0.25, 1.3, 0.5]}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>
      <mesh position={[-0.25, 1.3, 0.5]}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color="#000000" />
      </mesh>

      {/* Eye highlights */}
      <mesh position={[0.27, 1.32, 0.52]}>
        <sphereGeometry args={[0.03, 8, 8]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.5} />
      </mesh>
      <mesh position={[-0.23, 1.32, 0.52]}>
        <sphereGeometry args={[0.03, 8, 8]} />
        <meshStandardMaterial color="#ffffff" emissive="#ffffff" emissiveIntensity={0.5} />
      </mesh>

      {/* Wings */}
      <mesh ref={wingLeftRef} position={[0.8, 0.3, 0]} rotation={[0, 0, -0.3]}>
        <boxGeometry args={[0.8, 1.2, 0.1]} />
        <IridescentFeatherMaterial />
      </mesh>
      <mesh ref={wingRightRef} position={[-0.8, 0.3, 0]} rotation={[0, 0, 0.3]}>
        <boxGeometry args={[0.8, 1.2, 0.1]} />
        <IridescentFeatherMaterial />
      </mesh>

      {/* Tail feathers */}
      {[...Array(5)].map((_, i) => (
        <mesh
          key={i}
          position={[
            Math.sin((i / 5) * Math.PI - Math.PI / 2) * 0.3,
            -1 - i * 0.1,
            -0.5
          ]}
          rotation={[0.3, 0, (i - 2) * 0.1]}
        >
          <boxGeometry args={[0.15, 0.8 - i * 0.1, 0.05]} />
          <IridescentFeatherMaterial />
        </mesh>
      ))}
    </group>
  )
}

// Brilliant Budgie Particles
function BrilliantBudgieIdeas() {
  const particlesRef = useRef<THREE.Points>(null)

  const particles = useMemo(() => {
    const positions = new Float32Array(30 * 3)
    for (let i = 0; i < 30; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10
      positions[i * 3 + 1] = Math.random() * 5
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10
    }
    return positions
  }, [])

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05

      // Make particles float upward
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array
      for (let i = 0; i < positions.length; i += 3) {
        positions[i + 1] += 0.01
        if (positions[i + 1] > 5) {
          positions[i + 1] = -2
        }
      }
      particlesRef.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={30}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        color="#ffeb3b"
        transparent
        opacity={0.8}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}

export default function ParakeetHero() {
  return (
    <div className="h-screen w-full bg-gradient-to-b from-emerald-50 to-sky-50">
      <Canvas
        shadows
        camera={{ position: [5, 2, 5], fov: 45 }}
        className="w-full h-full"
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 5, 5]} intensity={1} castShadow />
        <pointLight position={[-5, 5, -5]} intensity={0.5} color="#00ff88" />

        <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
          <StylizedParakeet />
        </Float>

        <BrilliantBudgieIdeas />

        <Sparkles
          count={100}
          scale={10}
          size={2}
          speed={0.5}
          color="#00ff88"
        />

        <Environment preset="sunset" />
        <OrbitControls
          enablePan={false}
          enableZoom={false}
          minPolarAngle={Math.PI / 3}
          maxPolarAngle={Math.PI / 2}
        />

        <EffectComposer>
          <Bloom
            intensity={0.5}
            luminanceThreshold={0.5}
            luminanceSmoothing={0.9}
          />
          <ChromaticAberration offset={[0.001, 0.001]} />
          <Vignette darkness={0.3} />
        </EffectComposer>
      </Canvas>

      {/* Overlay text */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none flex items-center justify-center">
        <div className="text-center max-w-4xl px-6">
          <h1 className="text-6xl font-bold text-emerald-800 mb-4 drop-shadow-lg">
            Friendly Parakeet
          </h1>
          <p className="text-xl text-emerald-700 drop-shadow">
            Your AI coding companion that dreams in brilliant budgie ideas
          </p>
        </div>
      </div>
    </div>
  )
}