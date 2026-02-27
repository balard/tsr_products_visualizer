# Image Self-Hosting Plan

## Current State
- Images are hotlinked from tsrarchive.com, blogger.googleusercontent.com, and similar sources
- No local copies or thumbnails exist

## Rights Situation
- TSR cover art is copyrighted, rights held by Wizards of the Coast / Hasbro
- Cover artists also retain moral rights in many jurisdictions
- Fair use arguments: non-commercial, educational/archival purpose, transformative context
  (catalog/reference, not republishing the product), no market substitution
- Against: displaying entire artworks (not portions), works are creative (not factual)
- Practical reality: sites like tsrarchive.com, The Acaeum, Wikipedia, and DriveThruRPG
  have hosted these images for 20+ years without takedowns; WotC generally tolerates
  fan/archival use
- A copyright disclaimer has been added to the page footer

## Hosting Options (Evaluated)

| Option            | Pros                                                        | Cons                                                      |
|-------------------|-------------------------------------------------------------|-----------------------------------------------------------|
| **GitHub Pages**  | Free, fast CDN, version-controlled, easy deploy             | 1 GB repo soft limit, 100 MB file limit                   |
| **Google Drive**  | Free 15 GB, easy upload                                     | Unreliable direct-link URLs, CORS issues, throttling      |
| **Cloudflare R2** | Free tier (10 GB storage, no egress fees), proper CDN, CORS | Requires setup, needs a domain                            |
| **GitHub Releases** | Attach large archives to releases                         | Awkward for individual image serving                      |

### Recommendation
1. **First stage: GitHub Pages** — push images to a `/covers` folder, served at
   `https://balard.github.io/tsr_products_visualizer/covers/`. Simple, free, fast.
2. **When outgrowing GitHub limits: Cloudflare R2** — free egress is ideal for images.
3. **Avoid Google Drive** — hotlink URLs are fragile and Google actively discourages it.

## Image Optimization Strategy

Store two sizes per image:

```
covers/
  full/    ← 800–1200px wide, JPEG quality 80 (~80–200 KB each)
  thumb/   ← 300px wide, JPEG quality 70–80 (~15–30 KB each)
```

- **Thumbnails** are loaded instantly for browse/grid view and initial display
- **Full resolution** is loaded on-demand when user selects a product
- The app already has a loading state (`cover-loading`) that can show the thumb
  while the full image loads

## Implementation Steps

1. Collect/download images locally, organized by TSR product code
2. Write a Python (Pillow) batch-resize script to generate `full/` and `thumb/` directories
3. Update `products.json` to use local paths (or make the base URL configurable)
4. Deploy to GitHub Pages
5. Monitor size; migrate to Cloudflare R2 if needed
