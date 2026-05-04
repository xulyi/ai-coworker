---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics. Trigger when user mentions frontend, UI design, web components, React components, CSS styling, or visual design.
license: Complete terms in LICENSE.txt
metadata:
  version: "1.1.0"
  author: "Claude"
  language: "en"
  domain: "frontend-development"
  trigger_keywords:
    - frontend
    - UI design
    - web components
    - React components
    - CSS styling
    - visual design
    - build a page
    - create a component
    - design a website
    - interface design
  tools_hint:
    - html
    - css
    - javascript
    - react
    - vue
---

# Frontend Design

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

---

## Trigger Conditions

- Building web components, pages, or applications
- Frontend/UI design requests
- CSS styling and visual design
- React/Vue component creation
- Website interface design

---

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

---

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.

---

## ⚠️ Gotchas (Common Pitfalls)

### Pitfall 1: Generic "AI Aesthetic" Defaults
- **Trap**: Falling back to overused patterns (Inter font, purple gradients, white backgrounds)
- **Consequence**: Output looks like every other AI-generated design, lacks distinction
- **Solution**: Always choose a bold, specific aesthetic direction before starting. Commit to it fully.

### Pitfall 2: Aesthetic-Implementation Mismatch
- **Trap**: Trying to implement a maximalist vision with minimalist code (or vice versa)
- **Consequence**: Design feels incomplete or cluttered
- **Solution**: Match implementation complexity to aesthetic vision. Maximalism = elaborate animations; Minimalism = precise restraint.

### Pitfall 3: Accessibility Neglect
- **Trap**: Focusing only on visuals without considering contrast, keyboard navigation, screen readers
- **Consequence**: Design is unusable for many users
- **Solution**: Always check color contrast ratios, ensure interactive elements are keyboard accessible.

### Pitfall 4: No Clear Differentiator
- **Trap**: Creating something "nice" but forgettable
- **Consequence**: User gets a generic result they could have made themselves
- **Solution**: Always answer: "What's the ONE thing someone will remember about this design?"

### Pitfall 5: Ignoring Performance
- **Trap**: Heavy animations, unoptimized images, excessive DOM nodes
- **Consequence**: Slow load times, janky interactions
- **Solution**: Profile performance early. Optimize images, use CSS transforms, lazy load where appropriate.

### Pitfall 6: Inconsistency Across Iterations
- **Trap**: Changing aesthetic direction mid-implementation
- **Consequence**: Frankenstein design with mismatched elements
- **Solution**: Define the aesthetic direction upfront and stick to it. If user wants changes, clarify if it's a pivot or refinement.

---

## Output Requirements

Every frontend deliverable should include:

1. **Working code** (HTML/CSS/JS or framework-specific)
2. **Design rationale** — brief explanation of aesthetic choices
3. **Responsive considerations** — how it adapts to different screens
4. **Accessibility notes** — contrast ratios, keyboard navigation
5. **Performance considerations** — optimization strategies used

---

## Fallback Strategies

### When user requirements are vague
- Ask about: purpose, audience, brand personality, competitors they like
- Propose 2-3 distinct aesthetic directions with mood boards

### When technical constraints conflict with design vision
- Explain the trade-off clearly
- Offer alternatives that preserve the core aesthetic
- Never sacrifice accessibility for aesthetics

### When the design feels "off"
- Check: Is the aesthetic direction clear? Is implementation matching the vision?
- Review against the "one memorable thing" test
- Consider simplifying rather than adding more

---

## Testing Recommendations

Suggested eval scenarios (create evals/evals.json):

```json
{
  "evals": [
    {
      "name": "distinctive-landing-page",
      "prompt": "Create a landing page for a boutique coffee roaster",
      "expected": "Unique aesthetic direction, not generic corporate design"
    },
    {
      "name": "component-with-motion",
      "prompt": "Build an animated card component for a portfolio site",
      "expected": "Thoughtful animations, performance-conscious implementation"
    },
    {
      "name": "minimalist-dashboard",
      "prompt": "Design a minimal analytics dashboard",
      "expected": "Clean, refined design with intentional whitespace"
    }
  ]
}
```

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
