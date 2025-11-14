# 🦜 Development Guide

## Run Locally

```bash
cd /Users/erichowens/coding/friendly-parakeet/website/friendlyparakeet.com

# Install dependencies (first time only)
npm install

# Start development server with hot reload
npm run dev
```

Then open **http://localhost:3000** in your browser!

## What You'll See

- 🦜 **3D Animated Parakeet** with iridescent feather shaders
- ✨ **Brilliant Budgie particles** floating around
- 🎨 **Interactive orbit controls** - drag to rotate the parakeet
- 📱 **Fully responsive** landing page

## Development Features

### Hot Reload
Any changes you make to code will instantly update in the browser:
- Edit `app/page.tsx` → page updates
- Edit `components/ParakeetHero.tsx` → 3D scene updates
- Edit Tailwind classes → styles update

### Shader Debugging

The parakeet uses custom WebGL shaders for the iridescent feathers. To adjust:

1. Open `components/ParakeetHero.tsx`
2. Find `IridescentFeatherMaterial`
3. Modify the `fragmentShader`:
   - `color1`, `color2`, `color3` → Change feather colors
   - Adjust shimmer, feather patterns, rim lighting

### Animation Tweaking

Wing flapping speed:
```typescript
// In StylizedParakeet component
const flap = Math.sin(state.clock.elapsedTime * 3) * 0.2
// Change the 3 to make wings flap faster/slower
```

### Performance Monitoring

Open browser dev tools:
- **Console** → See any Three.js warnings
- **Performance tab** → Check if hitting 60 FPS
- **Network tab** → Verify Three.js loads correctly

## Testing Changes

### 1. Visual Inspection
- Check desktop (full screen)
- Check mobile (resize browser or use device mode)
- Verify parakeet loads and animates smoothly

### 2. Build Test
Before deploying, test the production build:

```bash
npm run build
npm start
```

Open http://localhost:3000 to see the production version.

### 3. Check for Errors

```bash
# Look for TypeScript errors
npm run build

# Check console in browser for runtime errors
```

## Making Changes

### Update Copy
Edit `app/page.tsx` - all the text content is there

### Adjust Colors
Search for color values:
- `emerald-600` → Primary green
- `sky-50` → Light blue backgrounds
- Parakeet colors in shader: `0x00ff88`, `0x00aaff`, `0xffaa00`

### Add Sections
Just add more `<section>` elements in `app/page.tsx`

### Modify 3D Parakeet
Edit `components/ParakeetHero.tsx`:
- Body shape → Change sphere geometry
- Wing size → Adjust box geometry args
- Lighting → Modify `<directionalLight>` and `<pointLight>`

## Common Issues

### 3D Parakeet Not Loading
```bash
# Reinstall Three.js dependencies
rm -rf node_modules
npm install
```

### Port Already in Use
```bash
# Use different port
npm run dev -- -p 3001
```

### Build Fails
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

## Deployment Workflow

1. **Develop** → `npm run dev` (test changes locally)
2. **Build** → `npm run build` (verify production build works)
3. **Deploy** → Run `./deploy_to_cloudflare.py` (push to live site)

## Tips

- The 3D parakeet is **performance-intensive** - normal to use GPU
- Post-processing effects (bloom, chromatic aberration) can be toggled for performance
- Mobile devices may show simplified visuals automatically

---

**Ready to see it?** Run `npm run dev` and check out http://localhost:3000! 🚀
