"use client"

import AnimatedParakeet from '@/components/AnimatedParakeet'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section with Animated Parakeet */}
      <section className="relative">
        <AnimatedParakeet />

        {/* Hero Content Overlay */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white via-white/90 to-transparent p-8">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Your coding companion that never forgets
            </h2>
            <p className="text-xl text-gray-700 max-w-3xl">
              A tiny parakeet living in your Mac menu bar, quietly tracking your progress across every project.
              When you're stuck, it knows. When you context-switch, it remembers.
              And while you sleep, it dreams up Brilliant Budgie ideas.
            </p>
            <div className="mt-8 flex gap-4">
              <a
                href="#download"
                className="px-8 py-4 bg-emerald-600 text-white rounded-full font-semibold hover:bg-emerald-700 transition-colors shadow-lg"
              >
                Download for Mac
              </a>
              <a
                href="#features"
                className="px-8 py-4 bg-white text-emerald-600 rounded-full font-semibold hover:bg-emerald-50 transition-colors shadow-lg border-2 border-emerald-600"
              >
                See How It Works
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* The Problem Section */}
      <section className="py-20 px-8 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              The Context-Switching Catastrophe
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Every developer knows the pain...
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-red-50 p-8 rounded-2xl">
              <div className="text-4xl mb-4">😵</div>
              <h3 className="text-xl font-bold text-red-900 mb-2">Monday Morning Amnesia</h3>
              <p className="text-red-700">
                "What was I working on Friday? Which branch? What was that bug fix about?"
                You spend 30 minutes just remembering where you left off.
              </p>
            </div>

            <div className="bg-orange-50 p-8 rounded-2xl">
              <div className="text-4xl mb-4">🔥</div>
              <h3 className="text-xl font-bold text-orange-900 mb-2">The Hotfix Hijack</h3>
              <p className="text-orange-700">
                Emergency fix interrupts your flow. Two hours later, you can't remember
                what you were doing before the fire drill.
              </p>
            </div>

            <div className="bg-purple-50 p-8 rounded-2xl">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold text-purple-900 mb-2">AI Context Chaos</h3>
              <p className="text-purple-700">
                You paste code to ChatGPT or Claude, but half the context is missing.
                The AI suggests things you already tried. Time wasted.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="features" className="py-20 px-8 bg-gradient-to-b from-emerald-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              A Parakeet That Watches, Remembers, and Dreams
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Friendly Parakeet sits quietly in your menu bar, doing three magical things:
            </p>
          </div>

          <div className="space-y-16">
            {/* Feature 1: Tracking */}
            <div className="flex items-center gap-12">
              <div className="flex-1">
                <h3 className="text-3xl font-bold text-emerald-800 mb-4">
                  1. Tracks Everything, Silently
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  It watches your git commits, file changes, and IDE activity across
                  VSCode, Cursor, Windsurf, XCode, and even terminal editors. No setup required.
                </p>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Monitors 20+ IDEs and editors
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Tracks git operations automatically
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Knows when you're stuck or in flow
                  </li>
                </ul>
              </div>
              <div className="flex-1 bg-gray-900 p-4 rounded-lg shadow-xl">
                <pre className="text-green-400 font-mono text-sm">
{`🦜 Parakeet Activity Log
─────────────────────
10:32 AM • Opened authentication.ts in Cursor
10:45 AM • Stuck pattern detected (no changes 10min)
10:46 AM • Chirp! "Try checking the JWT expiry?"
11:02 AM • Flow state achieved!
11:45 AM • Created breadcrumb for handoff`}
                </pre>
              </div>
            </div>

            {/* Feature 2: Breadcrumbs */}
            <div className="flex items-center gap-12 flex-row-reverse">
              <div className="flex-1">
                <h3 className="text-3xl font-bold text-emerald-800 mb-4">
                  2. Creates AI-Perfect Breadcrumbs
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  When you stop working, it automatically generates a perfect summary
                  that any AI (or human) can use to understand exactly where you left off.
                </p>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    One-click resume with full context
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Share with AI assistants instantly
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Perfect for async team collaboration
                  </li>
                </ul>
              </div>
              <div className="flex-1 bg-white p-6 rounded-lg shadow-xl border-2 border-emerald-200">
                <h4 className="font-bold text-gray-800 mb-2">📍 Breadcrumb Created</h4>
                <p className="text-sm text-gray-600 mb-4">Friday 5:47 PM</p>
                <div className="bg-emerald-50 p-4 rounded text-sm">
                  <p className="font-semibold mb-2">Where you left off:</p>
                  <p>Implementing JWT refresh token rotation in auth middleware.
                  Fixed expiry bug in line 47. Next: Add refresh endpoint tests.</p>
                  <p className="font-semibold mt-3 mb-2">Context files:</p>
                  <p>• auth/middleware.ts (modified)</p>
                  <p>• auth/tokens.test.ts (pending)</p>
                </div>
              </div>
            </div>

            {/* Feature 3: Brilliant Budgies */}
            <div className="flex items-center gap-12">
              <div className="flex-1">
                <h3 className="text-3xl font-bold text-emerald-800 mb-4">
                  3. Dreams Up Brilliant Budgies
                </h3>
                <p className="text-lg text-gray-700 mb-4">
                  While you sleep, your parakeet analyzes your code and generates
                  helpful ideas: missing tests, performance improvements, refactoring
                  suggestions, and tools that could save you hours.
                </p>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Overnight AI analysis of your codebase
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    Wake up to actionable improvements
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-emerald-600">✓</span>
                    One-click implementation
                  </li>
                </ul>
              </div>
              <div className="flex-1">
                <div className="bg-gradient-to-br from-yellow-100 to-emerald-100 p-6 rounded-lg shadow-xl">
                  <h4 className="font-bold text-gray-800 mb-4">✨ 3 Brilliant Budgies waiting!</h4>
                  <div className="space-y-3">
                    <div className="bg-white/80 p-3 rounded">
                      <p className="font-semibold text-sm">🧪 Missing Test Coverage</p>
                      <p className="text-xs text-gray-600">AuthService.refreshToken() has no tests</p>
                    </div>
                    <div className="bg-white/80 p-3 rounded">
                      <p className="font-semibold text-sm">⚡ Performance Boost</p>
                      <p className="text-xs text-gray-600">Database query in UserRepo could use index</p>
                    </div>
                    <div className="bg-white/80 p-3 rounded">
                      <p className="font-semibold text-sm">🔧 Refactor Opportunity</p>
                      <p className="text-xs text-gray-600">Extract validation logic to middleware</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="py-20 px-8 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Start Free, Upgrade When You Love It
            </h2>
            <p className="text-xl text-gray-600">
              No credit card required. Use your own OpenAI key or our hosted service.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Free Tier */}
            <div className="border-2 border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Free Forever</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">
                $0<span className="text-lg font-normal text-gray-600">/month</span>
              </p>
              <p className="text-gray-600 mb-6">Perfect for trying it out</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Basic progress tracking</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Manual breadcrumbs</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>10 AI assists/month</span>
                </li>
                <li className="flex items-center gap-2 text-gray-400">
                  <span>✗</span>
                  <span>Brilliant Budgies</span>
                </li>
              </ul>
              <button className="w-full py-3 border-2 border-gray-300 rounded-full font-semibold hover:bg-gray-50 transition-colors">
                Download Free
              </button>
            </div>

            {/* Friendly Tier */}
            <div className="border-2 border-emerald-600 rounded-2xl p-8 relative hover:shadow-xl transition-shadow">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-emerald-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                MOST POPULAR
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Friendly</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">
                $4.99<span className="text-lg font-normal text-gray-600">/month</span>
              </p>
              <p className="text-gray-600 mb-6">For daily developers</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Everything in Free</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>500 AI assists/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>5 Brilliant Budgies/day</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Auto breadcrumbs</span>
                </li>
              </ul>
              <button className="w-full py-3 bg-emerald-600 text-white rounded-full font-semibold hover:bg-emerald-700 transition-colors">
                Start Free Trial
              </button>
            </div>

            {/* Professional Tier */}
            <div className="border-2 border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Professional</h3>
              <p className="text-4xl font-bold text-gray-900 mb-4">
                $9.99<span className="text-lg font-normal text-gray-600">/month</span>
              </p>
              <p className="text-gray-600 mb-6">For power users</p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Everything in Friendly</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>2000 AI assists/month</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>Unlimited Brilliant Budgies</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-emerald-600">✓</span>
                  <span>GPT-4 access</span>
                </li>
              </ul>
              <button className="w-full py-3 border-2 border-gray-300 rounded-full font-semibold hover:bg-gray-50 transition-colors">
                Start Free Trial
              </button>
            </div>
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600">
              🔑 Already have an OpenAI API key? <a href="#" className="text-emerald-600 underline">Use it for free</a>
            </p>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-8 bg-gradient-to-b from-emerald-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Developers Love Their Parakeets
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <p className="text-gray-700 mb-4">
                "Monday mornings used to be painful. Now I just check my breadcrumbs
                and I'm back in flow within minutes. It's like I never left."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-full"></div>
                <div>
                  <p className="font-semibold">Sarah Chen</p>
                  <p className="text-sm text-gray-600">Senior Dev @ Stripe</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <p className="text-gray-700 mb-4">
                "The Brilliant Budgies are incredible. It found 3 N+1 queries
                I'd been living with for months. Fixed them over coffee."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full"></div>
                <div>
                  <p className="font-semibold">Marcus Rodriguez</p>
                  <p className="text-sm text-gray-600">CTO @ TechStartup</p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <p className="text-gray-700 mb-4">
                "It knows when I'm stuck and suggests a break. Sounds silly but
                my productivity has actually increased since I started using it."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-red-500 rounded-full"></div>
                <div>
                  <p className="font-semibold">Alex Kim</p>
                  <p className="text-sm text-gray-600">Indie Developer</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Download CTA */}
      <section id="download" className="py-20 px-8 bg-gradient-to-br from-emerald-600 to-emerald-800 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Never Lose Context Again?
          </h2>
          <p className="text-xl mb-8 text-emerald-100">
            Join thousands of developers who've made Friendly Parakeet their coding companion.
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/download/FriendlyParakeet-1.0.0.dmg"
              className="px-8 py-4 bg-white text-emerald-600 rounded-full font-semibold hover:bg-emerald-50 transition-colors shadow-lg"
            >
              Download for Mac
            </a>
            <a
              href="https://github.com/friendlyparakeet/parakeet"
              className="px-8 py-4 bg-emerald-700 text-white rounded-full font-semibold hover:bg-emerald-900 transition-colors shadow-lg"
            >
              View on GitHub
            </a>
          </div>
          <p className="mt-8 text-emerald-200">
            macOS 10.15+ • Apple Silicon & Intel • 24MB
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-8 bg-gray-900 text-gray-400">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-white font-bold mb-4">Friendly Parakeet</h3>
              <p className="text-sm">
                Your AI coding companion that never forgets.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#features" className="hover:text-white">Features</a></li>
                <li><a href="#pricing" className="hover:text-white">Pricing</a></li>
                <li><a href="/brilliant-budgies" className="hover:text-white">Brilliant Budgies</a></li>
                <li><a href="/docs" className="hover:text-white">Documentation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="/about" className="hover:text-white">About</a></li>
                <li><a href="/blog" className="hover:text-white">Blog</a></li>
                <li><a href="/privacy" className="hover:text-white">Privacy</a></li>
                <li><a href="/terms" className="hover:text-white">Terms</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Connect</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="https://twitter.com/friendlyparakeet" className="hover:text-white">Twitter</a></li>
                <li><a href="https://github.com/friendlyparakeet" className="hover:text-white">GitHub</a></li>
                <li><a href="mailto:hello@friendlyparakeet.com" className="hover:text-white">Email</a></li>
                <li><a href="/discord" className="hover:text-white">Discord</a></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-sm">
            <p>© 2024 Friendly Parakeet. Made with 🦜 and ❤️</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
